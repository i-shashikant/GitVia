"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  ArrowUpRight,
  AlertTriangle,
  CheckCircle2,
  Code2,
  ExternalLink,
  GitBranch,
  GitFork,
  Loader2,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Star,
  TrendingUp,
  Layers,
  TestTube2,
  Container,
  Database,
  FileText,
} from "lucide-react";

/* ============================================================
   TYPES
============================================================ */

type Reason = string;

type Dimension = {
  score?: number;
  reasons?: Reason[];
};

type Analysis = {
  overall_score?: number;
  documentation?: Dimension;
  architecture?: Dimension;
  code_quality?: Dimension;
  testing?: Dimension;
  devops?: Dimension;
  scalability?: Dimension;
  actionable_improvements?: string[];
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
  analysis?: Analysis;
  cached?: boolean;
  updated_at?: string | null;
};

/* ============================================================
   API
============================================================ */

async function fetchRepository(repoId: string): Promise<Repository> {
  const API_BASE =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const response = await fetch(
    `${API_BASE}/api/repos/${repoId}`,
    {
      credentials: "include",
      cache: "no-store",
    }
  );

  if (!response.ok) {
    let message = "Unable to load repository.";

    try {
      const data = await response.json();

      if (data?.detail) {
        message = data.detail;
      }
    } catch {
      // Ignore invalid JSON responses.
    }

    throw new Error(message);
  }

  return response.json();
}

/* ============================================================
   PAGE
============================================================ */

export default function RepositoryInspectionPage() {
  const params = useParams();

  const repoId = Array.isArray(params.repo_id)
    ? params.repo_id[0]
    : params.repo_id;

  const [repository, setRepository] =
    useState<Repository | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadRepository() {
    if (!repoId) return;

    try {
      setLoading(true);
      setError("");

      const data = await fetchRepository(repoId);

      setRepository(data);
    } catch (err) {
      console.error(err);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load repository."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRepository();
  }, [repoId]);

  /* ==========================================================
     LOADING
  ========================================================== */

  if (loading) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="relative">
            <div className="h-12 w-12 animate-spin rounded-full border-2 border-cyan-500/20 border-t-cyan-400" />

            <Code2 className="absolute inset-0 m-auto h-4 w-4 text-cyan-400" />
          </div>

          <div>
            <p className="text-sm font-semibold text-white">
              Inspecting repository
            </p>

            <p className="mt-1 text-xs text-gray-500">
              Loading GitVia repository intelligence...
            </p>
          </div>
        </div>
      </div>
    );
  }

  /* ==========================================================
     ERROR
  ========================================================== */

  if (error || !repository) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <div className="w-full max-w-md rounded-2xl border border-red-500/20 bg-red-950/20 p-7 text-center">
          <AlertTriangle className="mx-auto h-8 w-8 text-red-400" />

          <h1 className="mt-4 text-lg font-bold text-white">
            GitVia couldn't inspect this repository
          </h1>

          <p className="mt-2 text-sm leading-relaxed text-gray-400">
            {error || "Repository data was not returned by the API."}
          </p>

          <div className="mt-5 flex justify-center gap-3">
            <button
              onClick={loadRepository}
              className="inline-flex items-center gap-2 rounded-lg bg-cyan-500 px-4 py-2.5 text-sm font-bold text-black transition hover:bg-cyan-400"
            >
              <RefreshCw className="h-4 w-4" />
              Retry
            </button>

            <Link
              href="/repositories"
              className="inline-flex items-center gap-2 rounded-lg border border-gray-700 bg-gray-900 px-4 py-2.5 text-sm font-semibold text-gray-300 transition hover:bg-gray-800 hover:text-white"
            >
              Back
            </Link>
          </div>
        </div>
      </div>
    );
  }

  /* ==========================================================
     DATA
  ========================================================== */

  const analysis = repository.analysis || {};

  const score = Number(
    repository.quality_score ??
      analysis.overall_score ??
      0
  );

  const dimensions = [
    {
      key: "documentation",
      label: "Documentation",
      icon: FileText,
      value: Number(
        analysis.documentation?.score ?? 0
      ),
      reasons:
        analysis.documentation?.reasons || [],
    },
    {
      key: "architecture",
      label: "Architecture",
      icon: Layers,
      value: Number(
        analysis.architecture?.score ?? 0
      ),
      reasons:
        analysis.architecture?.reasons || [],
    },
    {
      key: "code_quality",
      label: "Code Quality",
      icon: Code2,
      value: Number(
        analysis.code_quality?.score ?? 0
      ),
      reasons:
        analysis.code_quality?.reasons || [],
    },
    {
      key: "testing",
      label: "Testing",
      icon: TestTube2,
      value: Number(
        analysis.testing?.score ?? 0
      ),
      reasons:
        analysis.testing?.reasons || [],
    },
    {
      key: "devops",
      label: "DevOps",
      icon: Container,
      value: Number(
        analysis.devops?.score ?? 0
      ),
      reasons:
        analysis.devops?.reasons || [],
    },
    {
      key: "scalability",
      label: "Scalability",
      icon: Database,
      value: Number(
        analysis.scalability?.score ?? 0
      ),
      reasons:
        analysis.scalability?.reasons || [],
    },
  ];

  const improvements =
    analysis.actionable_improvements || [];

  const strengths = dimensions
    .filter((dimension) => dimension.value >= 70)
    .sort((a, b) => b.value - a.value);

  const weaknesses = dimensions
    .filter((dimension) => dimension.value < 70)
    .sort((a, b) => a.value - b.value);

  return (
    <div className="space-y-7 pb-16">

      {/* ======================================================
          TOP NAV
      ====================================================== */}

      <div className="flex items-center justify-between">
        <Link
          href="/repositories"
          className="inline-flex items-center gap-2 text-sm font-medium text-gray-400 transition hover:text-cyan-400"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to repositories
        </Link>

        <button
          onClick={loadRepository}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-lg border border-gray-800 bg-gray-900 px-3 py-2 text-xs font-semibold text-gray-400 transition hover:border-cyan-500/40 hover:text-white disabled:opacity-50"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Refresh
        </button>
      </div>

      {/* ======================================================
          HERO
      ====================================================== */}

      <section className="relative overflow-hidden rounded-3xl border border-gray-800 bg-gradient-to-br from-gray-900 via-[#0d1420] to-[#091019] p-6 md:p-8">

        <div className="pointer-events-none absolute -right-32 -top-32 h-80 w-80 rounded-full bg-cyan-500/10 blur-3xl" />

        <div className="pointer-events-none absolute -bottom-32 -left-32 h-72 w-72 rounded-full bg-purple-500/5 blur-3xl" />

        <div className="relative flex flex-col gap-7 lg:flex-row lg:items-start lg:justify-between">

          <div className="min-w-0">

            {/* Repository label */}

            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-gray-700 bg-black/30">
                <Code2 className="h-6 w-6 text-cyan-400" />
              </div>

              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-400">
                    Repository Intelligence
                  </span>

                  {repository.is_fork && (
                    <span className="rounded-full border border-gray-700 bg-gray-800 px-2 py-0.5 text-[10px] text-gray-400">
                      Fork
                    </span>
                  )}
                </div>

                <p className="mt-1 text-xs text-gray-500">
                  GitVia engineering analysis
                </p>
              </div>
            </div>

            {/* Name */}

            <h1 className="mt-7 break-words text-3xl font-extrabold tracking-tight text-white md:text-4xl">
              {repository.name}
            </h1>

            <p className="mt-2 break-all text-sm text-gray-500">
              {repository.full_name}
            </p>

            <p className="mt-5 max-w-3xl text-sm leading-7 text-gray-400 md:text-base">
              {repository.description ||
                "No description provided for this repository."}
            </p>

            {/* Metadata */}

            <div className="mt-6 flex flex-wrap items-center gap-4 text-xs text-gray-500">

              {repository.language && (
                <span className="inline-flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-cyan-400" />
                  {repository.language}
                </span>
              )}

              <span className="inline-flex items-center gap-1.5">
                <Star className="h-3.5 w-3.5" />
                {repository.stars_count}
              </span>

              <span className="inline-flex items-center gap-1.5">
                <GitFork className="h-3.5 w-3.5" />
                {repository.forks_count}
              </span>

              <span className="inline-flex items-center gap-1.5">
                <GitBranch className="h-3.5 w-3.5" />
                {repository.default_branch}
              </span>

            </div>

            {/* Buttons */}

            <div className="mt-7 flex flex-wrap gap-3">

              <a
                href={repository.html_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 rounded-xl bg-cyan-500 px-4 py-2.5 text-sm font-bold text-black transition hover:bg-cyan-400"
              >
                Open on GitHub
                <ExternalLink className="h-4 w-4" />
              </a>

              <Link
                href="/repositories"
                className="inline-flex items-center gap-2 rounded-xl border border-gray-700 bg-gray-900/70 px-4 py-2.5 text-sm font-semibold text-gray-300 transition hover:border-gray-600 hover:bg-gray-800 hover:text-white"
              >
                All repositories
              </Link>

            </div>

          </div>

          {/* Main score */}

          <div className="shrink-0 rounded-2xl border border-gray-700 bg-black/20 p-6 text-center lg:min-w-[210px]">

            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gray-500">
              Quality Score
            </p>

            <div
              className={`mt-2 text-6xl font-black tracking-tight ${
                score >= 80
                  ? "text-emerald-400"
                  : score >= 60
                  ? "text-cyan-400"
                  : "text-amber-400"
              }`}
            >
              {score.toFixed(1)}
            </div>

            <p className="mt-1 text-sm text-gray-500">
              / 100
            </p>

            <ScoreLabel score={score} />

          </div>

        </div>
      </section>

      {/* ======================================================
          SCORE OVERVIEW
      ====================================================== */}

      <section className="grid gap-5 md:grid-cols-3">

        <OverviewCard
          title="Strongest area"
          value={
            strengths[0]
              ? strengths[0].label
              : "No strong area yet"
          }
          score={
            strengths[0]
              ? strengths[0].value
              : 0
          }
          icon={
            <TrendingUp className="h-5 w-5 text-emerald-400" />
          }
        />

        <OverviewCard
          title="Needs attention"
          value={
            weaknesses[0]
              ? weaknesses[0].label
              : "No major weakness"
          }
          score={
            weaknesses[0]
              ? weaknesses[0].value
              : 0
          }
          icon={
            <AlertTriangle className="h-5 w-5 text-amber-400" />
          }
        />

        <OverviewCard
          title="Analysis status"
          value="GitHub evidence"
          score={dimensions.length}
          suffix=" dimensions"
          icon={
            <ShieldCheck className="h-5 w-5 text-cyan-400" />
          }
        />

      </section>

      {/* ======================================================
          DIMENSIONS
      ====================================================== */}

      <section className="rounded-2xl border border-gray-800 bg-gray-900/50 p-6 md:p-7">

        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">

          <div>
            <div className="flex items-center gap-2">
              <Layers className="h-5 w-5 text-cyan-400" />

              <h2 className="text-lg font-bold text-white">
                Engineering Dimensions
              </h2>
            </div>

            <p className="mt-1 text-xs text-gray-500">
              How this repository performs across GitVia's six engineering dimensions.
            </p>
          </div>

          <span className="rounded-full border border-gray-800 bg-gray-950 px-3 py-1 text-xs text-gray-500">
            Weighted analysis
          </span>

        </div>

        <div className="mt-7 grid gap-5 md:grid-cols-2">

          {dimensions.map((dimension) => {
            const Icon = dimension.icon;

            return (
              <DimensionCard
                key={dimension.key}
                label={dimension.label}
                value={dimension.value}
                icon={<Icon className="h-4 w-4" />}
                reasons={dimension.reasons}
              />
            );
          })}

        </div>

      </section>

      {/* ======================================================
          STRENGTHS + WEAKNESSES
      ====================================================== */}

      <section className="grid gap-6 lg:grid-cols-2">

        {/* Strengths */}

        <section className="rounded-2xl border border-emerald-500/10 bg-gray-900/50 p-6">

          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-emerald-400" />

            <h2 className="font-bold text-white">
              What is working
            </h2>
          </div>

          <p className="mt-1 text-xs text-gray-500">
            Strong signals detected in this repository.
          </p>

          <div className="mt-5 space-y-3">

            {strengths.length > 0 ? (
              strengths.map((item) => (
                <div
                  key={item.key}
                  className="rounded-xl border border-gray-800 bg-gray-950/60 p-4"
                >
                  <div className="flex items-center justify-between gap-4">

                    <span className="text-sm font-semibold text-gray-200">
                      {item.label}
                    </span>

                    <span className="text-sm font-bold text-emerald-400">
                      {item.value}
                    </span>

                  </div>

                  <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-gray-800">
                    <div
                      className="h-full rounded-full bg-emerald-400"
                      style={{
                        width: `${Math.min(
                          100,
                          Math.max(0, item.value)
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              ))
            ) : (
              <EmptyState text="No dimension currently scores 70 or above." />
            )}

          </div>

        </section>

        {/* Weaknesses */}

        <section className="rounded-2xl border border-amber-500/10 bg-gray-900/50 p-6">

          <div className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-400" />

            <h2 className="font-bold text-white">
              What needs attention
            </h2>
          </div>

          <p className="mt-1 text-xs text-gray-500">
            Areas that are limiting the repository score.
          </p>

          <div className="mt-5 space-y-3">

            {weaknesses.length > 0 ? (
              weaknesses.map((item) => (
                <div
                  key={item.key}
                  className="rounded-xl border border-gray-800 bg-gray-950/60 p-4"
                >
                  <div className="flex items-center justify-between gap-4">

                    <span className="text-sm font-semibold text-gray-200">
                      {item.label}
                    </span>

                    <span className="text-sm font-bold text-amber-400">
                      {item.value}
                    </span>

                  </div>

                  <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-gray-800">
                    <div
                      className="h-full rounded-full bg-amber-400"
                      style={{
                        width: `${Math.min(
                          100,
                          Math.max(0, item.value)
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              ))
            ) : (
              <EmptyState text="No dimension currently falls below 70." />
            )}

          </div>

        </section>

      </section>

      {/* ======================================================
          EVIDENCE
      ====================================================== */}

      <section className="rounded-2xl border border-gray-800 bg-gray-900/50 p-6 md:p-7">

        <div className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-cyan-400" />

          <h2 className="text-lg font-bold text-white">
            Analysis Evidence
          </h2>
        </div>

        <p className="mt-1 text-xs text-gray-500">
          Signals GitVia detected while analyzing the repository.
        </p>

        <div className="mt-6 space-y-5">

          {dimensions.map((dimension) => (

            <div key={dimension.key}>

              <div className="mb-2 flex items-center justify-between">

                <span className="text-sm font-semibold text-gray-300">
                  {dimension.label}
                </span>

                <span className="text-xs text-gray-500">
                  {dimension.value}/100
                </span>

              </div>

              {dimension.reasons.length > 0 ? (
                <div className="space-y-2">

                  {dimension.reasons.map(
                    (reason, index) => {

                      const positive =
                        !reason
                          .toLowerCase()
                          .includes("missing") &&
                        !reason
                          .toLowerCase()
                          .includes("no automated") &&
                        !reason
                          .toLowerCase()
                          .includes("no asynchronous") &&
                        !reason
                          .toLowerCase()
                          .includes("flat file");

                      return (
                        <div
                          key={`${dimension.key}-${index}`}
                          className="flex items-start gap-3 rounded-lg border border-gray-800 bg-gray-950/50 px-4 py-3"
                        >

                          {positive ? (
                            <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
                          ) : (
                            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
                          )}

                          <p className="text-sm leading-relaxed text-gray-400">
                            {reason}
                          </p>

                        </div>
                      );
                    }
                  )}

                </div>
              ) : (
                <div className="rounded-lg border border-gray-800 bg-gray-950/50 px-4 py-3 text-sm text-gray-600">
                  No additional evidence recorded.
                </div>
              )}

            </div>

          ))}

        </div>

      </section>

      {/* ======================================================
          RECOMMENDATIONS
      ====================================================== */}

      <section className="relative overflow-hidden rounded-2xl border border-cyan-500/10 bg-gradient-to-br from-[#0b1722] via-gray-900 to-[#10101b] p-6 md:p-7">

        <div className="pointer-events-none absolute -right-20 -top-20 h-56 w-56 rounded-full bg-cyan-500/10 blur-3xl" />

        <div className="relative">

          <div className="flex items-center gap-2">

            <Sparkles className="h-5 w-5 text-cyan-400" />

            <h2 className="text-lg font-bold text-white">
              GitVia Recommendations
            </h2>

          </div>

          <p className="mt-1 text-xs text-gray-500">
            Actionable improvements generated specifically for this repository.
          </p>

          <div className="mt-6 space-y-3">

            {improvements.length > 0 ? (
              improvements.map((recommendation, index) => (

                <div
                  key={index}
                  className="flex items-start gap-4 rounded-xl border border-gray-800 bg-gray-950/50 p-4 transition hover:border-gray-700"
                >

                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-cyan-500/10 text-xs font-bold text-cyan-400">
                    {index + 1}
                  </div>

                  <p className="pt-1 text-sm leading-relaxed text-gray-300">
                    {recommendation}
                  </p>

                </div>

              ))
            ) : (
              <div className="rounded-xl border border-emerald-500/10 bg-emerald-500/5 p-5">

                <div className="flex items-center gap-3">
                  <CheckCircle2 className="h-5 w-5 text-emerald-400" />

                  <p className="text-sm font-semibold text-emerald-300">
                    No immediate improvements were generated.
                  </p>
                </div>

                <p className="mt-2 text-xs leading-relaxed text-gray-500">
                  This repository currently satisfies the analyzer's improvement thresholds.
                </p>

              </div>
            )}

          </div>

        </div>

      </section>

      {/* ======================================================
          FOOTER INFO
      ====================================================== */}

      <div className="flex flex-col gap-2 border-t border-gray-800 pt-5 text-xs text-gray-600 md:flex-row md:items-center md:justify-between">

        <span>
          GitVia repository analysis
        </span>

        <span>
          {repository.cached
            ? "Using cached analysis"
            : "Fresh analysis"}
          {repository.updated_at
            ? ` • Updated ${formatDate(repository.updated_at)}`
            : ""}
        </span>

      </div>

    </div>
  );
}

/* ============================================================
   SCORE LABEL
============================================================ */

function ScoreLabel({
  score,
}: {
  score: number;
}) {
  const label =
    score >= 80
      ? "Excellent"
      : score >= 60
      ? "Good"
      : "Needs work";

  const className =
    score >= 80
      ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-400"
      : score >= 60
      ? "border-cyan-500/20 bg-cyan-500/10 text-cyan-400"
      : "border-amber-500/20 bg-amber-500/10 text-amber-400";

  return (
    <div
      className={`mx-auto mt-4 w-fit rounded-full border px-3 py-1 text-[10px] font-bold uppercase tracking-[0.18em] ${className}`}
    >
      {label}
    </div>
  );
}

/* ============================================================
   OVERVIEW CARD
============================================================ */

function OverviewCard({
  title,
  value,
  score,
  suffix,
  icon,
}: {
  title: string;
  value: string;
  score: number;
  suffix?: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-5">

      <div className="flex items-center justify-between">

        <div className="flex items-center gap-2 text-gray-500">
          {icon}

          <span className="text-xs font-medium">
            {title}
          </span>
        </div>

      </div>

      <div className="mt-4 truncate text-lg font-bold text-white">
        {value}
      </div>

      <div className="mt-1 text-xs text-gray-600">
        {score}
        {suffix || "/100"}
      </div>

    </div>
  );
}

/* ============================================================
   DIMENSION CARD
============================================================ */

function DimensionCard({
  label,
  value,
  icon,
  reasons,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
  reasons: string[];
}) {
  const safeValue = Math.min(
    100,
    Math.max(0, Number(value) || 0)
  );

  const scoreClass =
    safeValue >= 80
      ? "text-emerald-400"
      : safeValue >= 60
      ? "text-cyan-400"
      : "text-amber-400";

  const barClass =
    safeValue >= 80
      ? "bg-emerald-400"
      : safeValue >= 60
      ? "bg-cyan-400"
      : "bg-amber-400";

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-950/50 p-5">

      <div className="flex items-center justify-between">

        <div className="flex items-center gap-2">

          <span className="text-gray-500">
            {icon}
          </span>

          <span className="text-sm font-semibold text-gray-300">
            {label}
          </span>

        </div>

        <span
          className={`text-xl font-bold ${scoreClass}`}
        >
          {safeValue}
        </span>

      </div>

      <div className="mt-4 h-2 overflow-hidden rounded-full bg-gray-800">

        <div
          className={`h-full rounded-full transition-all duration-700 ${barClass}`}
          style={{
            width: `${safeValue}%`,
          }}
        />

      </div>

      {reasons.length > 0 && (
        <p className="mt-3 line-clamp-2 text-xs leading-relaxed text-gray-600">
          {reasons[0]}
        </p>
      )}

    </div>
  );
}

/* ============================================================
   EMPTY STATE
============================================================ */

function EmptyState({
  text,
}: {
  text: string;
}) {
  return (
    <div className="rounded-xl border border-gray-800 bg-gray-950/50 p-5 text-sm text-gray-600">
      {text}
    </div>
  );
}

/* ============================================================
   DATE
============================================================ */

function formatDate(
  value: string
) {
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}