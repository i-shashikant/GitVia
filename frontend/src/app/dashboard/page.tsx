"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  ArrowRight,
  ArrowUpRight,
  Award,
  Briefcase,
  CheckCircle2,
  Code2,
  Cpu,
  ExternalLink,
  GitBranch,
  Layers,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Star,
  TrendingUp,
  Zap,
} from "lucide-react";

import { fetchProfile, fetchRepositories, GITHUB_LOGIN_URL } from "@/lib/api";

type ProfileData = {
  user: {
    id: number;
    github_id: number;
    github_username: string;
    name: string | null;
    email: string | null;
    avatar_url: string | null;
  };

  repository_count: number;

  profile: {
    primary_role: string;
    secondary_role: string;
    current_level: string;

    portfolio_score: number;
    github_score: number;
    readiness_score: number;

    dimension_averages: Record<string, number>;
    skill_scores: Record<string, number>;

    strongest_skills: string[];
    weakest_skills: string[];

    top_recommendations: string[];
  };
};

type Repository = {
  id: number;
  name: string;
  full_name: string;
  description: string | null;
  language: string | null;
  stars_count: number;
  forks_count: number;
  html_url: string;
  default_branch: string;
  is_fork: boolean;
  quality_score: number;
};

export default function DashboardPage() {
  const [data, setData] = useState<ProfileData | null>(null);
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDashboard() {
    try {
      setLoading(true);
      setError("");

      const [profileData, repoData] = await Promise.all([
        fetchProfile(),
        fetchRepositories(),
      ]);

      setData(profileData);
      setRepositories(Array.isArray(repoData) ? repoData : []);
    } catch (err) {
      console.error("Dashboard loading error:", err);

      if (err instanceof Error && err.message === "AUTH_REQUIRED") {
        setError("Your GitHub session has expired. Please reconnect GitHub.");
      } else {
        setError(
          "Unable to load GitVia intelligence. Make sure the backend is running and your GitHub session is connected."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  const profile = data?.profile;

  const averageQuality = useMemo(() => {
    if (!repositories.length) return 0;

    const total = repositories.reduce(
      (sum, repo) => sum + Number(repo.quality_score || 0),
      0
    );

    return total / repositories.length;
  }, [repositories]);

  const topRepositories = useMemo(() => {
    return [...repositories]
      .sort(
        (a, b) =>
          Number(b.quality_score || 0) -
          Number(a.quality_score || 0)
      )
      .slice(0, 5);
  }, [repositories]);

  if (loading) {
    return <DashboardSkeleton />;
  }

  if (error || !data || !profile) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center px-4">
        <div className="w-full max-w-md rounded-3xl border border-red-500/20 bg-red-950/20 p-8 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-red-500/20 bg-red-500/10">
            <AlertTriangle className="h-7 w-7 text-red-400" />
          </div>

          <h2 className="mt-5 text-xl font-bold text-white">
            GitVia couldn't load your intelligence
          </h2>

          <p className="mt-3 text-sm leading-relaxed text-gray-400">
            {error || "The API returned an unexpected response."}
          </p>

          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <button
              onClick={loadDashboard}
              className="inline-flex items-center gap-2 rounded-xl border border-gray-700 bg-gray-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:border-gray-600 hover:bg-gray-800"
            >
              <RefreshCw className="h-4 w-4" />
              Retry
            </button>
            <a
              href={GITHUB_LOGIN_URL}
              className="inline-flex items-center rounded-xl bg-cyan-600 px-5 py-2.5 text-sm font-semibold text-white"
            >
              Connect GitHub
            </a>
          </div>
        </div>
      </div>
    );
  }

  const user = data.user;

  return (
    <div className="space-y-8 pb-16">

      {/* ====================================================== */}
      {/* HERO */}
      {/* ====================================================== */}

      <section className="relative overflow-hidden rounded-3xl border border-gray-800 bg-gradient-to-br from-[#101722] via-[#0b111b] to-[#080c13] p-6 md:p-8">

        <div className="pointer-events-none absolute -right-32 -top-32 h-80 w-80 rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-40 left-1/3 h-72 w-72 rounded-full bg-indigo-500/10 blur-3xl" />

        <div className="relative flex flex-col gap-7 lg:flex-row lg:items-center lg:justify-between">

          <div className="flex items-center gap-5">

            {user.avatar_url ? (
              <div className="relative">
                <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-cyan-500/40 to-indigo-500/40 blur-md" />

                <img
                  src={user.avatar_url}
                  alt={user.github_username}
                  className="relative h-20 w-20 rounded-2xl border border-gray-700 object-cover"
                />
              </div>
            ) : (
              <div className="flex h-20 w-20 items-center justify-center rounded-2xl border border-gray-700 bg-gray-900">
                <GitBranch className="h-8 w-8 text-cyan-400" />
              </div>
            )}

            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-sm font-semibold text-cyan-400">
                  GitVia Intelligence
                </span>

                <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-[10px] font-bold tracking-wide text-emerald-400">
                  <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
                  LIVE DATA
                </span>
              </div>

              <h1 className="mt-1 text-2xl font-extrabold tracking-tight text-white md:text-3xl">
                Welcome back, {user.name || user.github_username}
              </h1>

              <p className="mt-1 text-sm text-gray-500">
                @{user.github_username}
                <span className="mx-2 text-gray-700">•</span>
                {data.repository_count} repositories analyzed
              </p>
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            <Link
              href="/repositories"
              className="inline-flex items-center gap-2 rounded-xl border border-gray-700 bg-gray-900/80 px-4 py-2.5 text-sm font-semibold text-gray-200 transition hover:border-cyan-500/30 hover:bg-gray-800"
            >
              <Code2 className="h-4 w-4 text-cyan-400" />
              Repositories
            </Link>

            <Link
              href="/career"
              className="inline-flex items-center gap-2 rounded-xl bg-cyan-400 px-4 py-2.5 text-sm font-bold text-black transition hover:bg-cyan-300"
            >
              <Briefcase className="h-4 w-4" />
              Career Analysis
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

        </div>
      </section>


      {/* ====================================================== */}
      {/* SCORE CARDS */}
      {/* ====================================================== */}

      <section className="grid grid-cols-1 gap-5 md:grid-cols-3">

        <ScoreCard
          label="Portfolio Score"
          value={profile.portfolio_score}
          icon={<Award className="h-5 w-5" />}
          accent="cyan"
          description="Overall portfolio strength"
        />

        <ScoreCard
          label="GitHub Score"
          value={profile.github_score}
          icon={<Cpu className="h-5 w-5" />}
          accent="purple"
          description="Repository engineering quality"
        />

        <ScoreCard
          label="Career Readiness"
          value={profile.readiness_score}
          icon={<Briefcase className="h-5 w-5" />}
          accent="emerald"
          description="Current job-readiness assessment"
        />

      </section>


      {/* ====================================================== */}
      {/* PROFILE + ENGINEERING */}
      {/* ====================================================== */}

      <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">

        <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-6">

          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-purple-500/20 bg-purple-500/10">
              <ShieldCheck className="h-5 w-5 text-purple-400" />
            </div>

            <div>
              <h2 className="font-bold text-white">
                Developer Profile
              </h2>

              <p className="text-xs text-gray-500">
                Based on GitHub evidence
              </p>
            </div>
          </div>

          <div className="mt-7 space-y-6">

            <ProfileField
              label="Primary Role"
              value={profile.primary_role}
              valueClass="text-cyan-400"
            />

            <ProfileField
              label="Secondary Role"
              value={profile.secondary_role}
              valueClass="text-purple-300"
            />

            <ProfileField
              label="Current Level"
              value={profile.current_level}
              valueClass="text-emerald-400"
            />

          </div>

        </div>


        <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-6 lg:col-span-2">

          <div className="flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-500/20 bg-cyan-500/10">
              <Layers className="h-5 w-5 text-cyan-400" />
            </div>

            <div>
              <h2 className="font-bold text-white">
                Engineering Dimensions
              </h2>

              <p className="text-xs text-gray-500">
                Aggregated from repository analysis
              </p>
            </div>

          </div>

          <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-3">

            {Object.entries(profile.dimension_averages).map(
              ([dimension, value]) => (
                <DimensionCard
                  key={dimension}
                  label={dimension}
                  value={Number(value)}
                />
              )
            )}

          </div>

        </div>

      </section>


      {/* ====================================================== */}
      {/* SKILL INTELLIGENCE */}
      {/* ====================================================== */}

      <section className="rounded-2xl border border-gray-800 bg-gray-900/60 p-6">

        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">

          <div className="flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-500/20 bg-cyan-500/10">
              <Zap className="h-5 w-5 text-cyan-400" />
            </div>

            <div>
              <h2 className="font-bold text-white">
                Skill Intelligence
              </h2>

              <p className="mt-1 text-xs text-gray-500">
                Technologies inferred from your analyzed projects.
              </p>
            </div>

          </div>

          <span className="w-fit rounded-full border border-gray-700 bg-gray-950 px-3 py-1 text-xs text-gray-400">
            {Object.keys(profile.skill_scores).length} technologies
          </span>

        </div>


        <div className="mt-7 grid grid-cols-1 gap-x-10 gap-y-6 md:grid-cols-2">

          {Object.entries(profile.skill_scores).map(
            ([skill, value]) => (
              <SkillBar
                key={skill}
                skill={skill}
                value={Number(value)}
              />
            )
          )}

        </div>

      </section>


      {/* ====================================================== */}
      {/* REPOSITORY INTELLIGENCE */}
      {/* ====================================================== */}

      <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">

        <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-6">

          <div className="flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-500/20 bg-cyan-500/10">
              <GitBranch className="h-5 w-5 text-cyan-400" />
            </div>

            <div>
              <h2 className="font-bold text-white">
                Repository Intelligence
              </h2>

              <p className="text-xs text-gray-500">
                Live GitHub analysis
              </p>
            </div>

          </div>


          <div className="mt-7">

            <p className="text-5xl font-black tracking-tight text-white">
              {repositories.length}
            </p>

            <p className="mt-1 text-xs text-gray-500">
              repositories analyzed
            </p>

          </div>


          <div className="mt-6 grid grid-cols-2 gap-3">

            <MiniStat
              label="Average Quality"
              value={averageQuality.toFixed(1)}
            />

            <MiniStat
              label="Stars"
              value={repositories
                .reduce(
                  (sum, repo) =>
                    sum + Number(repo.stars_count || 0),
                  0
                )
                .toString()}
            />

          </div>


          <Link
            href="/repositories"
            className="mt-6 flex items-center justify-center gap-2 rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 text-xs font-semibold text-gray-200 transition hover:border-cyan-500/30 hover:bg-gray-900"
          >
            Inspect all repositories
            <ArrowUpRight className="h-3.5 w-3.5" />
          </Link>

        </div>


        {/* TOP REPOSITORIES */}

        <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-6 lg:col-span-2">

          <div className="flex items-center justify-between">

            <div>
              <h2 className="font-bold text-white">
                Top Repository Signals
              </h2>

              <p className="mt-1 text-xs text-gray-500">
                Highest quality scores from your GitHub repositories.
              </p>
            </div>

            <TrendingUp className="h-5 w-5 text-emerald-400" />

          </div>


          <div className="mt-5 space-y-3">

            {topRepositories.length === 0 ? (
              <p className="text-sm text-gray-500">
                No repositories found.
              </p>
            ) : (
              topRepositories.map((repo, index) => (
                <div
                  key={repo.id}
                  className="group flex items-center gap-4 rounded-xl border border-gray-800 bg-gray-950/50 p-4 transition hover:border-gray-700 hover:bg-gray-950"
                >

                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gray-900 text-xs font-bold text-gray-500">
                    {index + 1}
                  </div>

                  <div className="min-w-0 flex-1">

                    <div className="flex items-center gap-2">

                      <p className="truncate text-sm font-semibold text-white">
                        {repo.name}
                      </p>

                      {repo.is_fork && (
                        <span className="rounded-full border border-gray-700 px-2 py-0.5 text-[9px] text-gray-500">
                          fork
                        </span>
                      )}

                    </div>

                    <div className="mt-1 flex items-center gap-3 text-[11px] text-gray-500">

                      {repo.language && (
                        <span>{repo.language}</span>
                      )}

                      <span className="inline-flex items-center gap-1">
                        <Star className="h-3 w-3" />
                        {repo.stars_count}
                      </span>

                      <span>
                        {repo.forks_count} forks
                      </span>

                    </div>

                  </div>


                  <div className="text-right">

                    <p className="text-lg font-bold text-cyan-400">
                      {Number(repo.quality_score || 0).toFixed(1)}
                    </p>

                    <p className="text-[9px] uppercase tracking-wider text-gray-600">
                      quality
                    </p>

                  </div>


                  <a
                    href={repo.html_url}
                    target="_blank"
                    rel="noreferrer"
                    className="hidden rounded-lg border border-gray-800 p-2 text-gray-500 transition hover:border-gray-700 hover:text-white sm:block"
                    title="Open on GitHub"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>

                </div>
              ))
            )}

          </div>

        </div>

      </section>


      {/* ====================================================== */}
      {/* STRENGTHS + WEAKNESSES */}
      {/* ====================================================== */}

      <section className="grid grid-cols-1 gap-6 md:grid-cols-2">

        <SkillGroup
          title="Strongest Capabilities"
          description="Areas currently supported by your GitHub evidence."
          skills={profile.strongest_skills}
          type="strength"
        />

        <SkillGroup
          title="Development Areas"
          description="Areas where your repository evidence shows room to improve."
          skills={profile.weakest_skills}
          type="weakness"
        />

      </section>


      {/* ====================================================== */}
      {/* RECOMMENDATIONS */}
      {/* ====================================================== */}

      <section className="relative overflow-hidden rounded-2xl border border-cyan-500/20 bg-gradient-to-br from-cyan-950/20 via-gray-900/70 to-purple-950/10 p-6">

        <div className="pointer-events-none absolute -right-24 -top-24 h-64 w-64 rounded-full bg-cyan-500/10 blur-3xl" />

        <div className="relative">

          <div className="flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-500/20 bg-cyan-500/10">
              <Sparkles className="h-5 w-5 text-cyan-400" />
            </div>

            <div>
              <h2 className="font-bold text-white">
                GitVia Recommendations
              </h2>

              <p className="mt-1 text-xs text-gray-500">
                Generated from your current repository intelligence.
              </p>
            </div>

          </div>


          <div className="mt-6 grid gap-3">

            {profile.top_recommendations.map(
              (recommendation, index) => (
                <div
                  key={`${recommendation}-${index}`}
                  className="group flex items-start gap-4 rounded-xl border border-gray-800 bg-black/20 p-4 transition hover:border-cyan-500/20 hover:bg-black/30"
                >

                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-cyan-500/20 bg-cyan-500/10 text-xs font-bold text-cyan-400">
                    {index + 1}
                  </div>

                  <p className="flex-1 text-sm leading-relaxed text-gray-300">
                    {recommendation}
                  </p>

                  <ArrowUpRight className="mt-1 h-4 w-4 shrink-0 text-gray-700 transition group-hover:text-cyan-400" />

                </div>
              )
            )}

          </div>

        </div>

      </section>

    </div>
  );
}


/* ============================================================ */
/* SCORE CARD */
/* ============================================================ */

function ScoreCard({
  label,
  value,
  icon,
  accent,
  description,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
  accent: "cyan" | "purple" | "emerald";
  description: string;
}) {
  const styles = {
    cyan: {
      border: "border-cyan-500/20",
      icon: "bg-cyan-500/10 text-cyan-400",
      value: "text-cyan-400",
    },

    purple: {
      border: "border-purple-500/20",
      icon: "bg-purple-500/10 text-purple-400",
      value: "text-purple-400",
    },

    emerald: {
      border: "border-emerald-500/20",
      icon: "bg-emerald-500/10 text-emerald-400",
      value: "text-emerald-400",
    },
  };

  const style = styles[accent];

  const safeValue = Math.min(
    Math.max(Number(value) || 0, 0),
    100
  );

  return (
    <div
      className={`group relative overflow-hidden rounded-2xl border ${style.border} bg-gray-900/70 p-6 shadow-xl transition hover:-translate-y-0.5 hover:bg-gray-900`}
    >

      <div className="flex items-start justify-between">

        <div>

          <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
            {label}
          </p>

          <p className={`mt-2 text-4xl font-black ${style.value}`}>
            {safeValue.toFixed(1)}
            <span className="ml-1 text-base font-normal text-gray-600">
              /100
            </span>
          </p>

        </div>

        <div
          className={`flex h-11 w-11 items-center justify-center rounded-xl border border-gray-800 ${style.icon}`}
        >
          {icon}
        </div>

      </div>


      <div className="mt-5 h-1.5 overflow-hidden rounded-full bg-gray-800">

        <div
          className={`h-full rounded-full bg-current ${style.value} transition-all duration-1000`}
          style={{ width: `${safeValue}%` }}
        />

      </div>


      <p className="mt-4 text-xs text-gray-500">
        {description}
      </p>

    </div>
  );
}


/* ============================================================ */
/* PROFILE FIELD */
/* ============================================================ */

function ProfileField({
  label,
  value,
  valueClass,
}: {
  label: string;
  value: string;
  valueClass: string;
}) {
  return (
    <div>
      <p className="text-[10px] font-semibold uppercase tracking-wider text-gray-600">
        {label}
      </p>

      <p className={`mt-1 text-sm font-bold ${valueClass}`}>
        {value}
      </p>
    </div>
  );
}


/* ============================================================ */
/* DIMENSION CARD */
/* ============================================================ */

function DimensionCard({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  const safeValue = Math.min(
    Math.max(Number(value) || 0, 0),
    100
  );

  const formattedLabel = label
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-950/50 p-4 transition hover:border-gray-700">

      <div className="flex items-center justify-between gap-2">

        <p className="text-xs capitalize text-gray-500">
          {formattedLabel}
        </p>

        <p className="text-sm font-bold text-white">
          {safeValue.toFixed(1)}
        </p>

      </div>

      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-gray-800">

        <div
          className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-1000"
          style={{
            width: `${safeValue}%`,
          }}
        />

      </div>

    </div>
  );
}


/* ============================================================ */
/* SKILL BAR */
/* ============================================================ */

function SkillBar({
  skill,
  value,
}: {
  skill: string;
  value: number;
}) {
  const safeValue = Math.min(
    Math.max(Number(value) || 0, 0),
    100
  );

  return (
    <div>

      <div className="mb-2 flex items-center justify-between">

        <span className="text-sm font-medium text-gray-300">
          {skill}
        </span>

        <span className="font-mono text-xs text-gray-500">
          {safeValue}/100
        </span>

      </div>

      <div className="h-2 overflow-hidden rounded-full bg-gray-800">

        <div
          className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-1000"
          style={{
            width: `${safeValue}%`,
          }}
        />

      </div>

    </div>
  );
}


/* ============================================================ */
/* MINI STAT */
/* ============================================================ */

function MiniStat({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-gray-800 bg-gray-950/70 p-3">

      <p className="text-[10px] uppercase tracking-wider text-gray-600">
        {label}
      </p>

      <p className="mt-1 text-lg font-bold text-white">
        {value}
      </p>

    </div>
  );
}


/* ============================================================ */
/* SKILL GROUP */
/* ============================================================ */

function SkillGroup({
  title,
  description,
  skills,
  type,
}: {
  title: string;
  description: string;
  skills: string[];
  type: "strength" | "weakness";
}) {
  const strength = type === "strength";

  return (
    <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-6">

      <div className="flex items-center gap-3">

        <div
          className={`flex h-10 w-10 items-center justify-center rounded-xl border ${
            strength
              ? "border-emerald-500/20 bg-emerald-500/10"
              : "border-amber-500/20 bg-amber-500/10"
          }`}
        >
          {strength ? (
            <TrendingUp className="h-5 w-5 text-emerald-400" />
          ) : (
            <AlertTriangle className="h-5 w-5 text-amber-400" />
          )}
        </div>

        <div>

          <h2 className="font-bold text-white">
            {title}
          </h2>

          <p className="mt-1 text-xs text-gray-500">
            {description}
          </p>

        </div>

      </div>


      <div className="mt-5 flex flex-wrap gap-2">

        {skills.map((skill) => (
          <span
            key={skill}
            className={`inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-xs font-medium ${
              strength
                ? "border-emerald-500/20 bg-emerald-500/5 text-emerald-300"
                : "border-amber-500/20 bg-amber-500/5 text-amber-300"
            }`}
          >
            {strength ? (
              <CheckCircle2 className="h-3.5 w-3.5" />
            ) : (
              <AlertTriangle className="h-3.5 w-3.5" />
            )}

            {skill}
          </span>
        ))}

      </div>

    </div>
  );
}


/* ============================================================ */
/* LOADING SKELETON */
/* ============================================================ */

function DashboardSkeleton() {
  return (
    <div className="space-y-8 pb-16 animate-pulse">

      <div className="h-36 rounded-3xl border border-gray-800 bg-gray-900/60" />

      <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
        <SkeletonBox />
        <SkeletonBox />
        <SkeletonBox />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <SkeletonBox className="h-64" />
        <SkeletonBox className="h-64 lg:col-span-2" />
      </div>

      <SkeletonBox className="h-72" />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <SkeletonBox className="h-64" />
        <SkeletonBox className="h-64 lg:col-span-2" />
      </div>

    </div>
  );
}


function SkeletonBox({
  className = "h-40",
}: {
  className?: string;
}) {
  return (
    <div
      className={`rounded-2xl border border-gray-800 bg-gray-900/60 ${className}`}
    />
  );
}