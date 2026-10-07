"use client";

import { useEffect, useState } from "react";

import {
  uploadResume,
  analyzeJobDescription,
  fetchJobAnalysisHistory,
  deleteJobAnalysis,
} from "@/lib/api";

import {
  FileText,
  Upload,
  Briefcase,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Sparkles,
  Search,
  ArrowRight,
  Map,
  Trash2,
  ShieldAlert,
} from "lucide-react";

export default function CareerPage() {
  // ============================================================
  // RESUME ANALYZER
  // ============================================================

  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeResult, setResumeResult] = useState<any>(null);
  const [uploading, setUploading] = useState(false);

  // ============================================================
  // JOB ANALYZER
  // ============================================================

  const [jobTitle, setJobTitle] = useState("");
  const [company, setCompany] = useState("");
  const [jobText, setJobText] = useState("");

  const [jobResult, setJobResult] = useState<any>(null);
  const [analyzingJob, setAnalyzingJob] = useState(false);

  // ============================================================
  // JOB HISTORY
  // ============================================================

  const [jobHistory, setJobHistory] = useState<any[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  // ID of the JobMatch/history entry currently selected.
  const [selectedHistoryId, setSelectedHistoryId] =
    useState<number | null>(null);

  // ID of the actual JobDescription.
  // This is what we use for the roadmap.
  const [selectedJobId, setSelectedJobId] =
    useState<number | null>(null);

  const [deletingJobId, setDeletingJobId] =
    useState<number | null>(null);

  // ============================================================
  // LOAD JOB HISTORY
  // ============================================================

  const loadJobHistory = async () => {
    try {
      setLoadingHistory(true);

      const data = await fetchJobAnalysisHistory();

      setJobHistory(data.history || []);
    } catch (err) {
      console.error("Failed to load job history:", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    loadJobHistory();
  }, []);

  // ============================================================
  // SELECT / RESTORE HISTORY ITEM
  // ============================================================

  const handleHistorySelect = (job: any) => {
    setSelectedHistoryId(job.match_id ?? null);
    setSelectedJobId(job.job_id ?? null);

    // Restore the original job form.
    setJobTitle(job.title || "");
    setCompany(job.company || "");
    setJobText(job.job_text || "");

    // Restore the complete analysis result.
    setJobResult({
      ...job,

      job_id: job.job_id,
      match_id: job.match_id,

      overall_match_score:
        job.overall_match_score ??
        job.match_score ??
        0,

      match_score:
        job.overall_match_score ??
        job.match_score ??
        0,

      tech_score: job.tech_score ?? 0,
      project_score: job.project_score ?? 0,
      experience_score: job.experience_score ?? 0,
      devops_score: job.devops_score ?? 0,
      problem_solving_score:
        job.problem_solving_score ?? 0,

      required_skills:
        job.required_skills || [],

      preferred_skills:
        job.preferred_skills || [],

      skill_gaps: {
        strong:
          job.strong_skills || [],

        improving:
          job.improving_skills || [],

        missing:
          job.skill_gap_missing_skills ||
          job.missing_skills ||
          [],
      },

      missing_skills:
        job.missing_skills || [],

      feedback_notes:
        job.feedback_notes || [],
    });

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  // ============================================================
  // DELETE HISTORY ITEM
  // ============================================================

  const handleDeleteHistory = async (
    event: React.MouseEvent,
    jobId: number
  ) => {
    // Prevent the history card's onClick from firing.
    event.stopPropagation();

    if (deletingJobId !== null) {
      return;
    }

    const confirmed = window.confirm(
      "Delete this job analysis from your history?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingJobId(jobId);

      await deleteJobAnalysis(jobId);

      // Remove immediately from UI.
      setJobHistory((previous) =>
        previous.filter(
          (job) => job.job_id !== jobId
        )
      );

      // If the deleted job was currently selected,
      // completely clear the active analysis.
      if (selectedJobId === jobId) {
        setSelectedJobId(null);
        setSelectedHistoryId(null);
        setJobResult(null);

        setJobTitle("");
        setCompany("");
        setJobText("");
      }
    } catch (err) {
      console.error(
        "Failed to delete job analysis:",
        err
      );

      window.alert(
        "Failed to delete this job analysis."
      );
    } finally {
      setDeletingJobId(null);
    }
  };

  // ============================================================
  // RESUME UPLOAD
  // ============================================================

  const handleResumeUpload = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (
      !e.target.files ||
      !e.target.files[0]
    ) {
      return;
    }

    const file = e.target.files[0];

    setResumeFile(file);
    setUploading(true);

    try {
      const data = await uploadResume(file);

      setResumeResult(data);
    } catch (err) {
      console.error(
        "Failed to upload resume:",
        err
      );
    } finally {
      setUploading(false);
    }
  };

  // ============================================================
  // BUILD JOB-SPECIFIC ROADMAP
  // ============================================================

  const handleBuildRoadmap = () => {
    if (!selectedJobId) {
      return;
    }

    window.location.href =
      `/roadmap?job_id=${selectedJobId}`;
  };

  // ============================================================
  // ANALYZE JOB
  // ============================================================

  const handleJobAnalyze = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    if (
      !jobTitle.trim() ||
      !jobText.trim()
    ) {
      return;
    }

    setAnalyzingJob(true);

    try {
      const data =
        await analyzeJobDescription(
          jobTitle.trim(),
          company.trim(),
          jobText.trim()
        );

      // Display the new analysis.
      setJobResult(data);

      // Store the actual JobDescription ID.
      setSelectedJobId(
        typeof data.job_id === "number"
          ? data.job_id
          : null
      );

      // Store the JobMatch ID.
      setSelectedHistoryId(
        typeof data.match_id === "number"
          ? data.match_id
          : null
      );

      // Refresh history so the new analysis
      // immediately appears in the history section.
      await loadJobHistory();
    } catch (err) {
      console.error(
        "Failed to analyze job:",
        err
      );

      window.alert(
        "Failed to analyze this job description."
      );
    } finally {
      setAnalyzingJob(false);
    }
  };

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <div className="space-y-10 pb-12">

      {/* ======================================================
          PAGE HEADER
      ======================================================= */}

      <div className="border-b border-gray-800 pb-6">
        <h1 className="text-3xl font-extrabold text-white">
          Career Intelligence & Job Matcher
        </h1>

        <p className="text-sm text-gray-400 mt-1">
          Upload your resume to detect claims
          unsupported by code, and paste target
          job specs for multi-factor match
          evaluation.
        </p>
      </div>

      {/* ======================================================
          MAIN TWO-COLUMN AREA
      ======================================================= */}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

        {/* ====================================================
            LEFT COLUMN — RESUME ANALYZER
        ===================================================== */}

        <div className="space-y-6">

          <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-6 space-y-6">

            {/* Header */}

            <div className="border-b border-gray-800 pb-4">

              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <FileText className="h-5 w-5 text-cyan-400" />

                Resume Analyzer
              </h2>

              <p className="text-xs text-gray-400 mt-0.5">
                Upload your PDF resume to extract
                skills and detect GitHub code
                mismatches.
              </p>

            </div>

            {/* Upload Input */}

            <div className="relative border-2 border-dashed border-gray-700 hover:border-cyan-500/50 rounded-xl p-6 text-center space-y-3 bg-gray-900/40 transition-colors">

              <Upload className="mx-auto h-8 w-8 text-cyan-400" />

              <div className="text-xs text-gray-300">

                <label className="cursor-pointer font-bold text-cyan-400 hover:underline">

                  <span>
                    Choose PDF file
                  </span>

                  <input
                    type="file"
                    accept=".pdf"
                    className="hidden"
                    onChange={
                      handleResumeUpload
                    }
                  />

                </label>

                <span className="text-gray-400">
                  {" "}or drag and drop
                </span>

              </div>

              <p className="text-[10px] text-gray-400">
                PyMuPDF structured extraction
                engine
              </p>

            </div>

            {/* Uploading State */}

            {uploading && (
              <div className="text-xs text-cyan-400 flex items-center gap-2 justify-center py-2">

                <div className="h-4 w-4 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />

                <span>
                  Extracting resume skills &
                  checking GitHub code
                  evidence...
                </span>

              </div>
            )}

            {/* Resume Result */}

            {resumeResult && (
              <div className="space-y-4 pt-2">

                {/* Mismatch Warnings */}

                <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-4 space-y-3">

                  <div className="flex items-center gap-2 text-xs font-bold text-amber-400 uppercase tracking-wider">

                    <ShieldAlert className="h-4 w-4" />

                    <span>
                      ⚠️ Resume ↔ GitHub
                      Code Mismatch
                    </span>

                  </div>

                  {resumeResult
                    .mismatch_flags
                    ?.map(
                      (
                        flag: any,
                        idx: number
                      ) => (
                        <div
                          key={idx}
                          className="text-xs text-gray-300 space-y-1 border-t border-amber-800/40 pt-2"
                        >

                          <div className="font-semibold text-amber-300">
                            {flag.message}
                          </div>

                          <div className="text-gray-400 text-[11px]">
                            💡 Action:{" "}
                            {flag.action}
                          </div>

                        </div>
                      )
                    )}

                </div>

                {/* Bullet Suggestions */}

                <div className="rounded-xl border border-gray-800 bg-gray-900/80 p-4 space-y-3">

                  <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">
                    Suggested Bullet
                    Enhancements
                  </span>

                  {resumeResult
                    .bullets_suggestions
                    ?.map(
                      (
                        bullet: any,
                        idx: number
                      ) => (
                        <div
                          key={idx}
                          className="text-xs space-y-1 border-t border-gray-800 pt-2"
                        >

                          <div className="text-rose-400 line-through">
                            ❌{" "}
                            {bullet.original}
                          </div>

                          <div className="text-emerald-400 font-medium">
                            ✓{" "}
                            {bullet.improved}
                          </div>

                        </div>
                      )
                    )}

                </div>

              </div>
            )}

          </div>

        </div>

        {/* ====================================================
            RIGHT COLUMN — JOB MATCHER
        ===================================================== */}

        <div className="space-y-6">

          <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-6 space-y-6">

            {/* Matcher Header */}

            <div className="border-b border-gray-800 pb-4">

              <h2 className="text-xl font-bold text-white flex items-center gap-2">

                <Briefcase className="h-5 w-5 text-purple-400" />

                Job Description Matcher ⭐

              </h2>

              <p className="text-xs text-gray-400 mt-0.5">
                Paste target job description to
                compute percentage match score
                and skill gaps.
              </p>

            </div>

            {/* ==================================================
                JOB FORM
            ================================================== */}

            <form
              onSubmit={handleJobAnalyze}
              className="space-y-4 text-xs"
            >

              {/* Role + Company */}

              <div className="grid grid-cols-2 gap-3">

                <div>

                  <label className="text-gray-400 font-medium">
                    Role Title
                  </label>

                  <input
                    type="text"
                    value={jobTitle}
                    onChange={(e) =>
                      setJobTitle(
                        e.target.value
                      )
                    }
                    placeholder="e.g. Software Development Intern"
                    className="mt-1 w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-white placeholder:text-gray-600 focus:border-cyan-500 focus:outline-none"
                  />

                </div>

                <div>

                  <label className="text-gray-400 font-medium">
                    Company
                  </label>

                  <input
                    type="text"
                    value={company}
                    onChange={(e) =>
                      setCompany(
                        e.target.value
                      )
                    }
                    placeholder="e.g. Microsoft"
                    className="mt-1 w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-white placeholder:text-gray-600 focus:border-cyan-500 focus:outline-none"
                  />

                </div>

              </div>

              {/* Job Description */}

              <div>

                <label className="text-gray-400 font-medium">
                  Job Description Text
                </label>

                <textarea
                  rows={7}
                  value={jobText}
                  onChange={(e) =>
                    setJobText(
                      e.target.value
                    )
                  }
                  placeholder="Paste the complete job description here..."
                  className="mt-1 w-full rounded-lg border border-gray-700 bg-gray-900 p-3 text-white placeholder:text-gray-600 focus:border-cyan-500 focus:outline-none font-mono text-[11px]"
                />

              </div>

              {/* Analyze */}

              <button
                type="submit"
                disabled={
                  analyzingJob ||
                  !jobTitle.trim() ||
                  !jobText.trim()
                }
                className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-4 py-3 font-bold text-white shadow-lg shadow-cyan-500/20 hover:opacity-90 transition-all disabled:cursor-not-allowed disabled:opacity-40"
              >
                {analyzingJob
                  ? "Analyzing Job Requirements..."
                  : "Calculate Job Match & Skill Gap Matrix"}
              </button>

            </form>

            {/* ==================================================
                CURRENT JOB RESULT
            ================================================== */}

            {jobResult && (
              <div className="space-y-6 pt-4 border-t border-gray-800">

                {/* Match Score Banner */}

                <div className="rounded-xl border border-cyan-500/30 bg-cyan-950/40 p-5">

                  <div className="flex items-center justify-between gap-4">

                    <div>

                      <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
                        {jobResult.company ||
                          company ||
                          "Job"}{" "}
                        Match Score
                      </span>

                      <div className="text-4xl font-extrabold text-white mt-1">
                        {
                          jobResult
                            .overall_match_score ??
                          jobResult.match_score ??
                          0
                        }%
                      </div>

                    </div>

                    <div className="text-right text-xs space-y-1.5 font-mono text-gray-300">

                      <div>
                        Technical:{" "}
                        <span className="text-cyan-400 font-bold">
                          {jobResult.tech_score ??
                            0}
                          %
                        </span>
                      </div>

                      <div>
                        Projects:{" "}
                        <span className="text-emerald-400 font-bold">
                          {jobResult.project_score ??
                            0}
                          %
                        </span>
                      </div>

                      <div>
                        Experience:{" "}
                        <span className="text-purple-400 font-bold">
                          {jobResult.experience_score ??
                            0}
                          %
                        </span>
                      </div>

                      <div>
                        DevOps:{" "}
                        <span className="text-amber-400 font-bold">
                          {jobResult.devops_score ??
                            0}
                          %
                        </span>
                      </div>

                      <div>
                        Problem Solving:{" "}
                        <span className="text-rose-400 font-bold">
                          {jobResult.problem_solving_score ??
                            0}
                          %
                        </span>
                      </div>

                    </div>

                  </div>

                </div>

                {/* ==================================================
                    SKILL GAP MATRIX
                ================================================== */}

                <div className="space-y-3">

                  <h3 className="text-sm font-bold text-white flex items-center gap-2">

                    <Sparkles className="h-4 w-4 text-cyan-400" />

                    Skill Gap Analysis Matrix ⭐

                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">

                    {/* Strong */}

                    <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-3 space-y-2">

                      <div className="font-bold text-emerald-400 flex items-center gap-1">

                        <CheckCircle2 className="h-3.5 w-3.5" />

                        Already Strong ✓

                      </div>

                      {jobResult.skill_gaps
                        ?.strong?.length ? (
                        <ul className="space-y-1 text-[11px] text-gray-300">
                          {jobResult.skill_gaps.strong.map(
                            (
                              skill: string,
                              index: number
                            ) => (
                              <li key={index}>
                                • {skill}
                              </li>
                            )
                          )}
                        </ul>
                      ) : (
                        <p className="text-[11px] text-gray-600">
                          No strong skills
                          identified.
                        </p>
                      )}

                    </div>

                    {/* Improving */}

                    <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-3 space-y-2">

                      <div className="font-bold text-amber-400 flex items-center gap-1">

                        <AlertTriangle className="h-3.5 w-3.5" />

                        Need Improvement ⚠

                      </div>

                      {jobResult.skill_gaps
                        ?.improving?.length ? (
                        <ul className="space-y-1 text-[11px] text-gray-300">
                          {jobResult.skill_gaps.improving.map(
                            (
                              skill: string,
                              index: number
                            ) => (
                              <li key={index}>
                                • {skill}
                              </li>
                            )
                          )}
                        </ul>
                      ) : (
                        <p className="text-[11px] text-gray-600">
                          No improvement areas
                          identified.
                        </p>
                      )}

                    </div>

                    {/* Missing */}

                    <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-3 space-y-2">

                      <div className="font-bold text-rose-400 flex items-center gap-1">

                        <XCircle className="h-3.5 w-3.5" />

                        Missing ✕

                      </div>

                      {jobResult.skill_gaps
                        ?.missing?.length ? (
                        <ul className="space-y-1 text-[11px] text-gray-300">
                          {jobResult.skill_gaps.missing.map(
                            (
                              skill: string,
                              index: number
                            ) => (
                              <li key={index}>
                                • {skill}
                              </li>
                            )
                          )}
                        </ul>
                      ) : (
                        <p className="text-[11px] text-gray-600">
                          No missing skills
                          identified.
                        </p>
                      )}

                    </div>

                  </div>

                </div>

                {/* ==================================================
                    BUILD ROADMAP
                    IMPORTANT: THIS IS OUTSIDE HISTORY MAP
                ================================================== */}

                {selectedJobId && (
                  <div className="pt-1">

                    <button
                      type="button"
                      onClick={
                        handleBuildRoadmap
                      }
                      className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-purple-500/20 transition-all hover:scale-[1.01] hover:opacity-95"
                    >

                      <Map className="h-4 w-4" />

                      Build Roadmap for
                      This Job

                      <ArrowRight className="h-4 w-4" />

                    </button>

                  </div>
                )}

              </div>
            )}

          </div>

          {/* ====================================================
              JOB ANALYSIS HISTORY

              IMPORTANT:
              This is OUTSIDE {jobResult && (...)}
              so history is always visible.
          ===================================================== */}

          <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-6 space-y-5">

            {/* History Header */}

            <div className="flex items-center justify-between gap-4">

              <div>

                <h2 className="text-xl font-bold text-white">
                  Job Analysis History
                </h2>

                <p className="text-xs text-gray-400 mt-1">
                  Your recently analyzed roles
                  and match scores.
                </p>

              </div>

              <div className="rounded-lg border border-gray-700 bg-gray-800/60 px-3 py-1.5 text-xs text-gray-400">
                {jobHistory.length} saved
              </div>

            </div>

            {/* Loading */}

            {loadingHistory ? (
              <div className="flex items-center justify-center py-8 text-cyan-400">

                <div className="h-4 w-4 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />

                <span className="ml-2 text-xs">
                  Loading analysis history...
                </span>

              </div>

            ) : jobHistory.length === 0 ? (

              /* Empty */

              <div className="rounded-xl border border-dashed border-gray-700 bg-gray-900/40 p-8 text-center">

                <Search className="mx-auto h-7 w-7 text-gray-600" />

                <p className="mt-3 text-sm text-gray-400">
                  No job analyses yet.
                </p>

                <p className="text-xs text-gray-600 mt-1">
                  Analyze your first job
                  description above and it
                  will appear here.
                </p>

              </div>

            ) : (

              /* History Cards */

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

                {jobHistory.map(
                  (job) => (

                    <div
                      key={job.match_id}
                      onClick={() =>
                        handleHistorySelect(
                          job
                        )
                      }
                      className={`cursor-pointer rounded-xl border bg-gray-950/50 p-4 transition-all ${
                        selectedHistoryId ===
                        job.match_id
                          ? "border-cyan-400/70 shadow-lg shadow-cyan-500/10"
                          : "border-gray-800 hover:border-cyan-500/40"
                      }`}
                    >

                      {/* Card Header */}

                      <div className="flex items-start justify-between gap-3">

                        <div className="min-w-0">

                          <h3 className="font-bold text-white text-sm truncate">
                            {job.title}
                          </h3>

                          <p className="text-xs text-gray-500 mt-1 truncate">
                            {job.company ||
                              "Unknown Company"}
                          </p>

                        </div>

                        <div className="flex items-start gap-2 shrink-0">

                          {/* Score */}

                          <div className="text-right">

                            <div className="text-xl font-extrabold text-cyan-400">
                              {job.overall_match_score ??
                                0}
                              %
                            </div>

                            <div className="text-[9px] uppercase tracking-wider text-gray-600">
                              match
                            </div>

                          </div>

                          {/* Delete */}

                          <button
                            type="button"
                            onClick={(event) =>
                              handleDeleteHistory(
                                event,
                                job.job_id
                              )
                            }
                            disabled={
                              deletingJobId ===
                              job.job_id
                            }
                            className="rounded-lg border border-rose-500/20 bg-rose-500/5 p-2 text-rose-400 transition hover:border-rose-500/40 hover:bg-rose-500/10 disabled:opacity-40"
                            title="Delete analysis"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>

                        </div>

                      </div>

                      {/* Score Breakdown */}

                      <div className="grid grid-cols-2 gap-2 mt-4 text-[10px]">

                        <div className="rounded-lg bg-gray-900 p-2">

                          <span className="text-gray-500">
                            Technical
                          </span>

                          <div className="text-cyan-400 font-bold mt-0.5">
                            {job.tech_score ??
                              0}
                            %
                          </div>

                        </div>

                        <div className="rounded-lg bg-gray-900 p-2">

                          <span className="text-gray-500">
                            Projects
                          </span>

                          <div className="text-emerald-400 font-bold mt-0.5">
                            {job.project_score ??
                              0}
                            %
                          </div>

                        </div>

                        <div className="rounded-lg bg-gray-900 p-2">

                          <span className="text-gray-500">
                            Experience
                          </span>

                          <div className="text-purple-400 font-bold mt-0.5">
                            {job.experience_score ??
                              0}
                            %
                          </div>

                        </div>

                        <div className="rounded-lg bg-gray-900 p-2">

                          <span className="text-gray-500">
                            DevOps
                          </span>

                          <div className="text-amber-400 font-bold mt-0.5">
                            {job.devops_score ??
                              0}
                            %
                          </div>

                        </div>

                      </div>

                      {/* Missing Skills */}

                      {job.missing_skills
                        ?.length > 0 && (
                        <div className="mt-4">

                          <span className="text-[10px] uppercase tracking-wider text-gray-600">
                            Missing
                          </span>

                          <div className="flex flex-wrap gap-1.5 mt-2">

                            {job.missing_skills
                              .slice(0, 4)
                              .map(
                                (
                                  skill: string,
                                  index: number
                                ) => (
                                  <span
                                    key={index}
                                    className="rounded-md border border-rose-500/20 bg-rose-950/20 px-2 py-1 text-[10px] text-rose-300"
                                  >
                                    {skill}
                                  </span>
                                )
                              )}

                          </div>

                        </div>
                      )}

                      {/* Restore Hint */}

                      <div className="mt-3 text-[10px] text-cyan-400 font-medium">
                        Click to restore analysis →
                      </div>

                      {/* Timestamp */}

                      <div className="mt-4 pt-3 border-t border-gray-800 text-[10px] text-gray-600">

                        {job.calculated_at
                          ? new Date(
                              job.calculated_at
                            ).toLocaleString()
                          : "Recently analyzed"}

                      </div>

                    </div>

                  )
                )}

              </div>

            )}

          </div>

        </div>

      </div>

    </div>
  );
}