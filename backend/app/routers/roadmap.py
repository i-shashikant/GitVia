from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.analyzers.roadmap_generator import RoadmapGenerator
from app.auth.session import get_current_user
from app.database import get_db
from app.github.client import GitHubAPIError
from app.models import (
    JobDescription,
    JobMatch,
    Roadmap,
    SkillGap,
    User,
)
from app.services.developer_context import build_developer_context


router = APIRouter(
    prefix="/api/roadmap",
    tags=["Personalized Learning Roadmap"],
)


def _merge_unique(*groups):
    """Merge skill lists while preserving order and removing duplicates."""
    result = []
    seen = set()

    for group in groups:
        if not group:
            continue

        for item in group:
            if not item:
                continue

            skill = str(item).strip()

            if not skill:
                continue

            key = skill.lower()

            if key not in seen:
                seen.add(key)
                result.append(skill)

    return result


def _build_job_aware_profile(
    base_profile: dict,
    job: JobDescription,
    match: JobMatch,
    skill_gap: SkillGap | None,
) -> dict:
    """
    Adapt the existing developer profile for a specific job.

    We deliberately keep RoadmapGenerator unchanged. Instead, we enrich
    the profile it already understands with the exact job's skill gaps.
    """

    profile = dict(base_profile or {})

    base_scores = dict(profile.get("skill_scores") or {})

    strong_skills = _merge_unique(
        profile.get("strongest_skills") or [],
        skill_gap.strong_skills if skill_gap else [],
    )

    improving_skills = _merge_unique(
        profile.get("weakest_skills") or [],
        skill_gap.improving_skills if skill_gap else [],
    )

    missing_skills = _merge_unique(
        skill_gap.missing_skills if skill_gap else [],
        match.missing_skills or [],
    )

    # A skill that is explicitly missing from the target job should not
    # accidentally remain in the "strong" bucket.
    strong_lookup = {skill.lower() for skill in strong_skills}

    missing_skills = [
        skill
        for skill in missing_skills
        if skill.lower() not in strong_lookup
    ]

    skill_scores = base_scores

    missing_skills = [
        skill
        for skill in missing_skills
        if skill.lower() not in strong_lookup
        and not (
            isinstance(skill_scores.get(skill), (int, float))
            and skill_scores.get(skill, 0) >= 70
        )
    ]

    # Required job skills become roadmap-relevant evidence.
    #
    # We only assign a low score when the job analysis explicitly identifies
    # the skill as missing. Existing developer-profile scores remain intact.
    for skill in missing_skills:
        if skill not in base_scores:
            base_scores[skill] = 20

    # Improving skills should be visible to RoadmapGenerator as weak skills.
    for skill in improving_skills:
        if skill not in base_scores:
            base_scores[skill] = 55

    # Make sure the profile exposes all three concepts expected by the
    # existing RoadmapGenerator.
    profile["skill_scores"] = base_scores
    profile["strongest_skills"] = strong_skills
    profile["weakest_skills"] = _merge_unique(
        improving_skills,
        missing_skills,
    )

    # Helpful metadata for the generator / future extensions.
    profile["job_required_skills"] = list(job.required_skills or [])
    profile["job_preferred_skills"] = list(job.preferred_skills or [])
    profile["job_missing_skills"] = missing_skills
    profile["job_match_score"] = match.overall_match_score

    return profile


@router.get("")
async def get_roadmap(
    target_role: str = "Backend Engineer",
    refresh: bool = Query(False),
    job_id: int | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return a personalized roadmap.

    Modes:

    1. Normal role roadmap:
       /api/roadmap?target_role=Backend%20Engineer

    2. Job-specific roadmap:
       /api/roadmap?job_id=123

    Job-specific roadmaps always use the stored JobMatch + SkillGap
    associated with that user's job analysis.
    """

    job = None
    match = None
    skill_gap = None

    # ---------------------------------------------------------
    # JOB-SPECIFIC ROADMAP
    # ---------------------------------------------------------

    if job_id is not None:
        job = (
            db.query(JobDescription)
            .filter(
                JobDescription.id == job_id,
                JobDescription.user_id == current_user.id,
            )
            .first()
        )

        if not job:
            raise HTTPException(
                status_code=404,
                detail="Job analysis not found.",
            )

        match = (
            db.query(JobMatch)
            .filter(
                JobMatch.job_id == job.id,
                JobMatch.user_id == current_user.id,
            )
            .order_by(JobMatch.calculated_at.desc())
            .first()
        )

        if not match:
            raise HTTPException(
                status_code=404,
                detail="No job match exists for this job.",
            )

        # SkillGap does not currently have a direct job_id relationship,
        # so associate the latest matching role analysis with this job.
        skill_gap = (
            db.query(SkillGap)
            .filter(
                SkillGap.user_id == current_user.id,
                SkillGap.target_role == job.title,
                SkillGap.created_at <= match.calculated_at,
            )
            .order_by(SkillGap.created_at.desc())
            .first()
        )

        # Job-specific roadmaps must not accidentally return the generic
        # cached roadmap for the same role.
        refresh = True

        target_role = job.title

    # ---------------------------------------------------------
    # NORMAL CACHED ROADMAP
    # ---------------------------------------------------------

    if not refresh:
        existing = (
            db.query(Roadmap)
            .filter(
                Roadmap.user_id == current_user.id,
                Roadmap.target_role == target_role,
            )
            .order_by(Roadmap.created_at.desc())
            .first()
        )

        if existing and existing.weekly_tasks:
            return existing.weekly_tasks

    # ---------------------------------------------------------
    # BUILD CURRENT DEVELOPER CONTEXT
    # ---------------------------------------------------------

    try:
        ctx = await build_developer_context(current_user, db)
    except GitHubAPIError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc

    profile = ctx["profile"]
    repos = ctx["repos"]

    # ---------------------------------------------------------
    # MAKE PROFILE JOB-AWARE
    # ---------------------------------------------------------

    if job is not None and match is not None:
        profile = _build_job_aware_profile(
            profile,
            job,
            match,
            skill_gap,
        )

    # ---------------------------------------------------------
    # GENERATE ROADMAP
    # ---------------------------------------------------------

    generator = RoadmapGenerator()

    result = generator.generate_roadmap(
        profile,
        repos,
        target_role,
    )

    # Add useful job metadata to the response.
    if job is not None and match is not None:
        result["job_id"] = job.id
        result["job_title"] = job.title
        result["company"] = job.company
        result["job_match_score"] = match.overall_match_score

    # ---------------------------------------------------------
    # PERSIST ROADMAP
    # ---------------------------------------------------------

    roadmap = Roadmap(
        user_id=current_user.id,
        target_role=target_role,
        duration_weeks=result.get("duration_weeks") or 6,
        weekly_tasks=result,
        created_at=datetime.utcnow(),
    )

    db.add(roadmap)
    db.commit()

    return result