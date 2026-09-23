"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  Search,
  Star,
  GitFork,
  ExternalLink,
  AlertCircle,
  RefreshCw,
  Code2,
  GitBranch,
  ArrowUpRight,
  SlidersHorizontal,
  X,
  CheckCircle2,
  TrendingUp,
  AlertTriangle,
  Sparkles,
  Lightbulb,
} from "lucide-react";

import { fetchRepositories } from "@/lib/api";

/* ============================================================
   TYPES
============================================================ */

type AnalysisDimension = {
  score?: number;
  reasons?: string[];
};

type Analysis = {
  overall_score?: number;

  documentation?: AnalysisDimension;
  architecture?: AnalysisDimension;
  code_quality?: AnalysisDimension;
  testing?: AnalysisDimension;
  devops?: AnalysisDimension;
  scalability?: AnalysisDimension;

  actionable_improvements?: string[];
};

type Repository = {
  id: number;
  github_repo_id?: number;

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
};

type SortOption =
  | "quality"
  | "stars"
  | "name"
  | "forks";

type FilterOption =
  | "all"
  | "excellent"
  | "good"
  | "needs-work"
  | "forks";

/* ============================================================
   PAGE
============================================================ */

export default function RepositoriesPage() {
  const [repositories, setRepositories] = useState<Repository[]>([]);

  const [search, setSearch] = useState("");

  const [sortBy, setSortBy] =
    useState<SortOption>("quality");

  const [filter, setFilter] =
    useState<FilterOption>("all");

  const [loading, setLoading] = useState(true);

  const [error, setError] =
    useState<string | null>(null);

  /* ==========================================================
     LOAD REPOSITORIES
  ========================================================== */

  async function loadRepositories(refresh = false) {
    try {
      setLoading(true);
      setError(null);

      const data = await fetchRepositories(refresh);

      setRepositories(
        Array.isArray(data) ? data : []
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load repositories."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRepositories();
  }, []);

  /* ==========================================================
     FILTER + SORT
  ========================================================== */

  const filteredRepositories = useMemo(() => {
    const query = search.trim().toLowerCase();

    let result = repositories.filter((repo) => {
      const matchesSearch =
        !query ||
        repo.name
          .toLowerCase()
          .includes(query) ||
        repo.full_name
          .toLowerCase()
          .includes(query) ||
        repo.description
          ?.toLowerCase()
          .includes(query) ||
        repo.language
          ?.toLowerCase()
          .includes(query);

      if (!matchesSearch) {
        return false;
      }

      const score =
        Number(repo.quality_score || 0);

      if (filter === "excellent") {
        return score >= 80;
      }

      if (filter === "good") {
        return (
          score >= 60 &&
          score < 80
        );
      }

      if (filter === "needs-work") {
        return score < 60;
      }

      if (filter === "forks") {
        return repo.is_fork;
      }

      return true;
    });

    result = [...result].sort((a, b) => {
      if (sortBy === "quality") {
        return (
          Number(b.quality_score || 0) -
          Number(a.quality_score || 0)
        );
      }

      if (sortBy === "stars") {
        return (
          Number(b.stars_count || 0) -
          Number(a.stars_count || 0)
        );
      }

      if (sortBy === "forks") {
        return (
          Number(b.forks_count || 0) -
          Number(a.forks_count || 0)
        );
      }

      return a.name.localeCompare(
        b.name
      );
    });

    return result;
  }, [
    repositories,
    search,
    sortBy,
    filter,
  ]);

  /* ==========================================================
     STATS
  ========================================================== */

  const averageScore =
    repositories.length > 0
      ? repositories.reduce(
          (sum, repo) =>
            sum +
            Number(
              repo.quality_score || 0
            ),
          0
        ) / repositories.length
      : 0;

  const totalStars =
    repositories.reduce(
      (sum, repo) =>
        sum +
        Number(
          repo.stars_count || 0
        ),
      0
    );

  const totalForks =
    repositories.reduce(
      (sum, repo) =>
        sum +
        Number(
          repo.forks_count || 0
        ),
      0
    );

  const excellentCount =
    repositories.filter(
      (repo) =>
        Number(
          repo.quality_score || 0
        ) >= 80
    ).length;

  /* ==========================================================
     RENDER
  ========================================================== */

  return (
    <div className="space-y-8 py-6">

      {/* =====================================================
          HEADER
      ====================================================== */}

      <section className="relative overflow-hidden rounded-3xl border border-gray-800 bg-gradient-to-br from-gray-900 via-gray-900/90 to-[#0b0f19] p-7 md:p-9">

        <div className="pointer-events-none absolute -right-24 -top-24 h-64 w-64 rounded-full bg-cyan-500/10 blur-3xl" />

        <div className="relative flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">

          <div>

            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-cyan-500/20 bg-cyan-500/5 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-cyan-400">

              <Code2 className="h-3.5 w-3.5" />

              GitHub Intelligence

            </div>

            <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Your Repositories
            </h1>

            <p className="mt-3 max-w-2xl text-sm leading-relaxed text-gray-400">
              GitVia analyzes your actual GitHub repositories
              across documentation, architecture, testing,
              DevOps, and scalability.
            </p>

          </div>

          <button
            onClick={() => loadRepositories(true)}
            disabled={loading}
            className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl border border-gray-700 bg-gray-900/80 px-4 py-2.5 text-sm font-semibold text-gray-200 transition hover:border-cyan-500/40 hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
          >

            <RefreshCw
              className={`h-4 w-4 ${
                loading
                  ? "animate-spin"
                  : ""
              }`}
            />

            Refresh Analysis

          </button>

        </div>

      </section>

      {/* =====================================================
          STATS
      ====================================================== */}

      {!loading &&
        !error &&
        repositories.length > 0 && (

          <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">

            <StatCard
              label="Repositories"
              value={
                repositories.length
              }
              icon={
                <Code2 className="h-4 w-4" />
              }
              description="Analyzed projects"
            />

            <StatCard
              label="Average Quality"
              value={
                averageScore.toFixed(1)
              }
              icon={
                <TrendingUp className="h-4 w-4" />
              }
              description="Across all repositories"
            />

            <StatCard
              label="Total Stars"
              value={totalStars}
              icon={
                <Star className="h-4 w-4" />
              }
              description="GitHub stars"
            />

            <StatCard
              label="Strong Projects"
              value={excellentCount}
              icon={
                <CheckCircle2 className="h-4 w-4" />
              }
              description="Quality score ≥ 80"
            />

          </section>
        )}

      {/* =====================================================
          CONTROLS
      ====================================================== */}

      {!loading &&
        !error &&
        repositories.length > 0 && (

          <section className="rounded-2xl border border-gray-800 bg-gray-900/40 p-4">

            <div className="flex flex-col gap-4 lg:flex-row">

              {/* Search */}

              <div className="relative flex-1">

                <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />

                <input
                  value={search}
                  onChange={(e) =>
                    setSearch(
                      e.target.value
                    )
                  }
                  placeholder="Search repositories, languages, descriptions..."
                  className="w-full rounded-xl border border-gray-800 bg-gray-950/60 py-3 pl-11 pr-10 text-sm text-white outline-none placeholder:text-gray-600 transition focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/10"
                />

                {search && (
                  <button
                    onClick={() =>
                      setSearch("")
                    }
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}

              </div>

              {/* Sort */}

              <div className="flex items-center gap-2 rounded-xl border border-gray-800 bg-gray-950/60 px-3">

                <TrendingUp className="h-4 w-4 text-gray-500" />

                <select
                  value={sortBy}
                  onChange={(e) =>
                    setSortBy(
                      e.target.value as SortOption
                    )
                  }
                  className="bg-transparent py-3 text-sm text-gray-300 outline-none"
                >

                  <option value="quality">
                    Quality score
                  </option>

                  <option value="stars">
                    Stars
                  </option>

                  <option value="forks">
                    Forks
                  </option>

                  <option value="name">
                    Name
                  </option>

                </select>

              </div>

            </div>

            {/* Filters */}

            <div className="mt-4 flex flex-wrap items-center gap-2">

              <div className="mr-1 flex items-center gap-2 text-xs text-gray-500">

                <SlidersHorizontal className="h-3.5 w-3.5" />

                Filter

              </div>

              <FilterButton
                active={
                  filter === "all"
                }
                onClick={() =>
                  setFilter("all")
                }
              >
                All
              </FilterButton>

              <FilterButton
                active={
                  filter === "excellent"
                }
                onClick={() =>
                  setFilter("excellent")
                }
              >
                Excellent · 80+
              </FilterButton>

              <FilterButton
                active={
                  filter === "good"
                }
                onClick={() =>
                  setFilter("good")
                }
              >
                Good · 60–79
              </FilterButton>

              <FilterButton
                active={
                  filter === "needs-work"
                }
                onClick={() =>
                  setFilter("needs-work")
                }
              >
                Needs work · &lt;60
              </FilterButton>

              <FilterButton
                active={
                  filter === "forks"
                }
                onClick={() =>
                  setFilter("forks")
                }
              >
                Forks
              </FilterButton>

            </div>

          </section>
        )}

      {/* =====================================================
          LOADING
      ====================================================== */}

      {loading && (

        <div className="grid gap-5 lg:grid-cols-2">

          {Array.from({
            length: 6,
          }).map((_, index) => (

            <RepositorySkeleton
              key={index}
            />

          ))}

        </div>
      )}

      {/* =====================================================
          ERROR
      ====================================================== */}

      {!loading && error && (

        <div className="rounded-2xl border border-red-900/50 bg-red-950/20 p-7">

          <div className="flex items-start gap-4">

            <div className="rounded-xl border border-red-900/50 bg-red-950/40 p-2">

              <AlertCircle className="h-5 w-5 text-red-400" />

            </div>

            <div>

              <h2 className="font-semibold text-red-300">
                Unable to load repositories
              </h2>

              <p className="mt-1 max-w-xl text-sm text-red-300/70">
                {error}
              </p>

              <button
                onClick={() => loadRepositories(true)}
                className="mt-5 inline-flex items-center gap-2 rounded-lg border border-red-800 bg-red-950/40 px-4 py-2 text-xs font-semibold text-red-300 transition hover:bg-red-900/40"
              >

                <RefreshCw className="h-3.5 w-3.5" />

                Try again

              </button>

            </div>

          </div>

        </div>
      )}

      {/* =====================================================
          EMPTY
      ====================================================== */}

      {!loading &&
        !error &&
        repositories.length === 0 && (

          <div className="rounded-2xl border border-gray-800 bg-gray-900/40 p-14 text-center">

            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-gray-800 bg-gray-950">

              <Code2 className="h-7 w-7 text-gray-600" />

            </div>

            <h2 className="mt-5 text-lg font-semibold text-white">
              No repositories found
            </h2>

            <p className="mx-auto mt-2 max-w-md text-sm text-gray-500">
              GitVia couldn't find repositories connected
              to your GitHub account.
            </p>

          </div>
        )}

      {/* =====================================================
          REPOSITORIES
      ====================================================== */}

      {!loading &&
        !error &&
        filteredRepositories.length > 0 && (

          <div className="grid gap-5 lg:grid-cols-2">

            {filteredRepositories.map(
              (repo) => (

                <RepositoryCard
                  key={repo.id}
                  repository={repo}
                />

              )
            )}

          </div>
        )}

      {/* =====================================================
          SEARCH EMPTY
      ====================================================== */}

      {!loading &&
        !error &&
        repositories.length > 0 &&
        filteredRepositories.length === 0 && (

          <div className="rounded-2xl border border-gray-800 bg-gray-900/40 p-12 text-center">

            <Search className="mx-auto h-7 w-7 text-gray-600" />

            <h2 className="mt-4 text-base font-semibold text-white">
              No matching repositories
            </h2>

            <p className="mt-2 text-sm text-gray-500">
              Try another search term or change the filters.
            </p>

            <button
              onClick={() => {
                setSearch("");
                setFilter("all");
              }}
              className="mt-5 rounded-lg border border-gray-700 px-4 py-2 text-xs font-semibold text-gray-300 transition hover:bg-gray-800"
            >
              Clear filters
            </button>

          </div>
        )}

      {/* =====================================================
          RESULT COUNT
      ====================================================== */}

      {!loading &&
        !error &&
        repositories.length > 0 && (

          <div className="flex items-center justify-between border-t border-gray-800 pt-5 text-xs text-gray-600">

            <span>
              Showing{" "}
              {filteredRepositories.length}{" "}
              of{" "}
              {repositories.length}{" "}
              repositories
            </span>

            <span>
              {totalForks} total forks
            </span>

          </div>
        )}

    </div>
  );
}

/* ============================================================
   REPOSITORY CARD
============================================================ */

function RepositoryCard({
  repository,
}: {
  repository: Repository;
}) {

  const score =
    Number(
      repository.quality_score || 0
    );

  const analysis =
    repository.analysis;

  const dimensions = [
    {
      label: "Docs",
      value:
        analysis?.documentation?.score,
    },
    {
      label: "Architecture",
      value:
        analysis?.architecture?.score,
    },
    {
      label: "Code",
      value:
        analysis?.code_quality?.score,
    },
    {
      label: "Testing",
      value:
        analysis?.testing?.score,
    },
    {
      label: "DevOps",
      value:
        analysis?.devops?.score,
    },
    {
      label: "Scale",
      value:
        analysis?.scalability?.score,
    },
  ];

  const recommendations =
    analysis?.actionable_improvements ||
    [];

  return (

    <article className="group relative overflow-hidden rounded-2xl border border-gray-800 bg-gray-900/50 p-6 transition duration-300 hover:-translate-y-0.5 hover:border-cyan-500/30 hover:bg-gray-900/80 hover:shadow-2xl hover:shadow-cyan-950/10">

      {/* Hover glow */}

      <div className="pointer-events-none absolute -right-16 -top-16 h-32 w-32 rounded-full bg-cyan-500/5 blur-3xl transition group-hover:bg-cyan-500/10" />

      {/* =====================================================
          HEADER
      ====================================================== */}

      <div className="relative flex items-start justify-between gap-4">

        <div className="min-w-0 flex-1">

          <div className="flex items-center gap-2">

            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-gray-800 bg-gray-950">

              <Code2 className="h-4 w-4 text-cyan-400" />

            </div>

            <div className="min-w-0">

              <Link
                href={`/repositories/${repository.id}`}
                className="block truncate text-lg font-semibold text-white transition hover:text-cyan-400"
              >
                {repository.name}
              </Link>

              <p className="truncate text-xs text-gray-500">
                {repository.full_name}
              </p>

            </div>

          </div>

        </div>

        <ScoreBadge
          score={score}
        />

      </div>

      {/* =====================================================
          DESCRIPTION
      ====================================================== */}

      <p className="relative mt-5 min-h-[44px] text-sm leading-relaxed text-gray-400">

        {repository.description ||
          "No description provided for this repository."}

      </p>

      {/* =====================================================
          METADATA
      ====================================================== */}

      <div className="relative mt-5 flex flex-wrap items-center gap-4 border-b border-gray-800 pb-5 text-xs text-gray-500">

        {repository.language && (

          <span className="inline-flex items-center gap-2">

            <span className="h-2.5 w-2.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.4)]" />

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

        {repository.is_fork && (

          <span className="rounded-full border border-gray-700 bg-gray-800/50 px-2 py-0.5">
            Fork
          </span>
        )}

      </div>

      {/* =====================================================
          ANALYSIS DIMENSIONS
      ====================================================== */}

      <div className="relative mt-5 grid grid-cols-3 gap-x-4 gap-y-4">

        {dimensions.map(
          (dimension) => (

            <MiniScore
              key={dimension.label}
              label={dimension.label}
              value={dimension.value}
            />

          )
        )}

      </div>

      {/* =====================================================
          REPOSITORY-SPECIFIC RECOMMENDATIONS
      ====================================================== */}

      <div className="relative mt-6 overflow-hidden rounded-xl border border-amber-500/10 bg-amber-500/[0.03]">

        <div className="flex items-center gap-2 border-b border-amber-500/10 px-4 py-3">

          <div className="flex h-7 w-7 items-center justify-center rounded-lg border border-amber-500/20 bg-amber-500/10">

            <Lightbulb className="h-3.5 w-3.5 text-amber-400" />

          </div>

          <div>

            <p className="text-xs font-semibold text-gray-200">
              GitVia Recommendations
            </p>

            <p className="text-[10px] text-gray-600">
              Specific to this repository
            </p>

          </div>

        </div>

        <div className="p-4">

          {recommendations.length > 0 ? (

            <div className="space-y-2.5">

              {recommendations
                .slice(0, 3)
                .map(
                  (
                    recommendation,
                    index
                  ) => (

                    <div
                      key={`${recommendation}-${index}`}
                      className="flex items-start gap-2.5"
                    >

                      <div className="mt-1 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-amber-500/10">

                        <Sparkles className="h-2.5 w-2.5 text-amber-400" />

                      </div>

                      <p className="text-xs leading-relaxed text-gray-400">

                        {recommendation}

                      </p>

                    </div>

                  )
                )}

            </div>

          ) : (

            <div className="flex items-center gap-2 text-xs text-emerald-400">

              <CheckCircle2 className="h-4 w-4" />

              <span>
                No immediate improvements detected.
              </span>

            </div>

          )}

        </div>

      </div>

      {/* =====================================================
          ACTIONS
      ====================================================== */}

      <div className="relative mt-6 flex items-center gap-3">

        <Link
          href={`/repositories/${repository.id}`}
          className="group/button inline-flex items-center gap-2 rounded-lg bg-cyan-500 px-4 py-2.5 text-xs font-bold text-black transition hover:bg-cyan-400"
        >

          Inspect Repository

          <ArrowUpRight className="h-3.5 w-3.5 transition-transform group-hover/button:translate-x-0.5 group-hover/button:-translate-y-0.5" />

        </Link>

        <a
          href={repository.html_url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1.5 rounded-lg border border-gray-700 px-4 py-2.5 text-xs font-semibold text-gray-300 transition hover:border-gray-600 hover:bg-gray-800 hover:text-white"
        >

          GitHub

          <ExternalLink className="h-3.5 w-3.5" />

        </a>

      </div>

    </article>
  );
}

/* ============================================================
   SCORE BADGE
============================================================ */

function ScoreBadge({
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

  return (

    <div className="shrink-0 text-right">

      <div
        className={`text-2xl font-bold ${
          score >= 80
            ? "text-emerald-400"
            : score >= 60
            ? "text-cyan-400"
            : "text-amber-400"
        }`}
      >
        {score.toFixed(1)}
      </div>

      <div className="mt-0.5 text-[9px] font-semibold uppercase tracking-[0.15em] text-gray-600">
        {label}
      </div>

    </div>
  );
}

/* ============================================================
   MINI SCORE
============================================================ */

function MiniScore({
  label,
  value,
}: {
  label: string;
  value?: number;
}) {

  const score =
    typeof value === "number"
      ? Math.max(
          0,
          Math.min(100, value)
        )
      : 0;

  const scoreText =
    typeof value === "number"
      ? Math.round(score)
      : "—";

  return (

    <div>

      <div className="mb-1.5 flex items-center justify-between">

        <span className="text-[10px] uppercase tracking-wider text-gray-600">
          {label}
        </span>

        <span className="text-[10px] font-semibold text-gray-400">
          {scoreText}
        </span>

      </div>

      <div className="h-1 overflow-hidden rounded-full bg-gray-800">

        <div
          className={`h-full rounded-full transition-all duration-700 ${
            score >= 80
              ? "bg-emerald-400"
              : score >= 60
              ? "bg-cyan-400"
              : score >= 40
              ? "bg-amber-400"
              : "bg-red-400"
          }`}
          style={{
            width:
              typeof value === "number"
                ? `${score}%`
                : "0%",
          }}
        />

      </div>

    </div>
  );
}

/* ============================================================
   STAT CARD
============================================================ */

function StatCard({
  label,
  value,
  icon,
  description,
}: {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  description: string;
}) {

  return (

    <div className="group rounded-2xl border border-gray-800 bg-gray-900/50 p-5 transition hover:border-gray-700 hover:bg-gray-900/80">

      <div className="flex items-center justify-between">

        <div className="flex items-center gap-2 text-gray-500">

          {icon}

          <span className="text-xs font-medium">
            {label}
          </span>

        </div>

        <ArrowUpRight className="h-3.5 w-3.5 text-gray-700 transition group-hover:text-cyan-400" />

      </div>

      <div className="mt-3 text-2xl font-bold text-white">
        {value}
      </div>

      <div className="mt-1 text-[11px] text-gray-600">
        {description}
      </div>

    </div>
  );
}

/* ============================================================
   FILTER BUTTON
============================================================ */

function FilterButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {

  return (

    <button
      onClick={onClick}
      className={`rounded-lg border px-3 py-1.5 text-xs font-medium transition ${
        active
          ? "border-cyan-500/30 bg-cyan-500/10 text-cyan-300"
          : "border-gray-800 bg-gray-950/40 text-gray-500 hover:border-gray-700 hover:text-gray-300"
      }`}
    >
      {children}
    </button>
  );
}

/* ============================================================
   LOADING SKELETON
============================================================ */

function RepositorySkeleton() {

  return (

    <div className="animate-pulse rounded-2xl border border-gray-800 bg-gray-900/50 p-6">

      <div className="flex items-start justify-between">

        <div className="flex items-center gap-3">

          <div className="h-9 w-9 rounded-lg bg-gray-800" />

          <div>

            <div className="h-4 w-40 rounded bg-gray-800" />

            <div className="mt-2 h-3 w-28 rounded bg-gray-800" />

          </div>

        </div>

        <div className="h-8 w-12 rounded bg-gray-800" />

      </div>

      <div className="mt-6 space-y-2">

        <div className="h-3 w-full rounded bg-gray-800" />

        <div className="h-3 w-4/5 rounded bg-gray-800" />

      </div>

      <div className="mt-6 grid grid-cols-3 gap-4">

        {Array.from({
          length: 6,
        }).map((_, index) => (

          <div key={index}>

            <div className="mb-2 h-2 w-12 rounded bg-gray-800" />

            <div className="h-1 rounded bg-gray-800" />

          </div>

        ))}

      </div>

      <div className="mt-6 rounded-xl border border-gray-800 p-4">

        <div className="h-3 w-36 rounded bg-gray-800" />

        <div className="mt-3 h-3 w-full rounded bg-gray-800" />

        <div className="mt-2 h-3 w-4/5 rounded bg-gray-800" />

      </div>

      <div className="mt-6 flex gap-3 border-t border-gray-800 pt-5">

        <div className="h-9 w-32 rounded-lg bg-gray-800" />

        <div className="h-9 w-20 rounded-lg bg-gray-800" />

      </div>

    </div>
  );
}