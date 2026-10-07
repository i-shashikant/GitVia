"use client";

import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Clock3,
  Code2,
  Cpu,
  Flag,
  Layers,
  Map,
  Sparkles,
  Terminal,
  Trophy,
  Wrench,
} from "lucide-react";

import { fetchRoadmap } from "@/lib/api";

type RoadmapTask = {
  title?: string;
  task?: string;
  description?: string;
  skill?: string;
  skills?: string[];
  estimated_hours?: number;
  hours?: number;
  completed?: boolean;
  done?: boolean;
};

type RoadmapWeek = {
  week?: number;
  title?: string;
  theme?: string;
  focus?: string;
  description?: string;
  deliverable?: string;
  guidance?: string;
  status?: string;
  tasks?: RoadmapTask[];
};

type RoadmapData = {
  target_role?: string;
  duration_weeks?: number;
  headline?: string;
  job_id?: number;
  job_title?: string;
  company?: string | null;
  job_match_score?: number;
  job_specific?: boolean;
  weekly_plan?: RoadmapWeek[];
  weekly_tasks?: RoadmapWeek[];
  weeks?: RoadmapWeek[];
  strong_skills?: string[];
  improving_skills?: string[];
  missing_skills?: string[];
  skill_gaps?: {
    strong?: string[];
    improving?: string[];
    missing?: string[];
  };
};

function normalizeTask(task: RoadmapTask): RoadmapTask {
  return {
    ...task,
    title: task.title || task.task || "Development task",
    description:
      task.description ||
      "Work on this area to strengthen your profile for the target job.",
    estimated_hours: task.estimated_hours || task.hours || 4,
    completed: Boolean(task.completed ?? task.done),
  };
}

function normalizeWeek(week: RoadmapWeek, index: number): RoadmapWeek {
  const rawTasks = Array.isArray(week.tasks) ? week.tasks : [];

  return {
    ...week,
    week: week.week || index + 1,
    title: week.title || week.theme || `Week ${index + 1}`,
    description:
      week.description ||
      week.focus ||
      "Build practical evidence for the target job.",
    tasks: rawTasks.map((task: RoadmapTask | string) =>
      typeof task === "string"
        ? normalizeTask({
            title: task,
            description: week.deliverable || week.guidance,
          })
        : normalizeTask(task)
    ),
  };
}

export default function RoadmapPage() {
  const [roadmap, setRoadmap] = useState<RoadmapData | null>(null);
  const [jobId, setJobId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandedWeek, setExpandedWeek] = useState<number | null>(1);
  const [completedTasks, setCompletedTasks] = useState<Record<string, boolean>>(
    {}
  );

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const rawJobId = params.get("job_id");
    const parsedJobId = rawJobId ? Number(rawJobId) : null;
    const activeJobId =
      parsedJobId !== null && Number.isFinite(parsedJobId)
        ? parsedJobId
        : null;

    setJobId(activeJobId);
    setLoading(true);
    setError("");

    fetchRoadmap(
      "Backend Engineer",
      false,
      activeJobId ?? undefined
    )
      .then((data) => {
        setRoadmap(data);

        const weeks =
          data?.weekly_plan || data?.weekly_tasks || data?.weeks || [];

        if (weeks.length > 0) {
          setExpandedWeek(weeks[0]?.week || 1);
        }
      })
      .catch((err) => {
        console.error(err);
        setError(
          "Unable to load this roadmap. Return to Career & Jobs and build the roadmap from a saved job analysis."
        );
      })
      .finally(() => setLoading(false));
  }, []);

  const weeks = useMemo(() => {
    if (!roadmap) return [];

    const rawWeeks =
      roadmap.weekly_plan || roadmap.weekly_tasks || roadmap.weeks || [];

    return rawWeeks.map(normalizeWeek);
  }, [roadmap]);

  const strongSkills =
    roadmap?.strong_skills || roadmap?.skill_gaps?.strong || [];

  const improvingSkills =
    roadmap?.improving_skills || roadmap?.skill_gaps?.improving || [];

  const missingSkills =
    roadmap?.missing_skills || roadmap?.skill_gaps?.missing || [];

  const totalTasks = weeks.reduce(
    (total, week) => total + (week.tasks?.length || 0),
    0
  );

  const completedCount = Object.values(completedTasks).filter(Boolean).length;

  const progress =
    totalTasks > 0 ? Math.round((completedCount / totalTasks) * 100) : 0;

  function toggleTask(weekNumber: number, taskIndex: number) {
    const key = `${weekNumber}-${taskIndex}`;

    setCompletedTasks((previous) => ({
      ...previous,
      [key]: !previous[key],
    }));
  }

  if (loading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="relative">
            <div className="h-12 w-12 rounded-full border-2 border-cyan-500/20 border-t-cyan-400 animate-spin" />
            <Sparkles className="absolute inset-0 m-auto h-5 w-5 text-cyan-400" />
          </div>

          <div>
            <p className="text-sm font-semibold text-white">
              Building your career roadmap...
            </p>
            <p className="mt-1 text-xs text-gray-500">
              GitVia is combining the job requirements with your GitHub
              evidence.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !roadmap) {
    return (
      <div className="space-y-6 pb-12">
        <div className="rounded-2xl border border-rose-500/20 bg-rose-950/10 p-8">
          <div className="flex items-start gap-4">
            <AlertTriangle className="h-6 w-6 shrink-0 text-rose-400" />

            <div>
              <h1 className="text-lg font-bold text-white">
                Roadmap unavailable
              </h1>

              <p className="mt-2 text-sm leading-6 text-gray-400">
                {error ||
                  "No roadmap was returned for the selected job analysis."}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const isJobSpecific = Boolean(jobId || roadmap.job_specific);

  return (
    <div className="space-y-8 pb-16">
      {/* HEADER */}
      <section className="relative overflow-hidden rounded-2xl border border-gray-800 bg-gray-900/60 p-6 md:p-8">
        <div className="pointer-events-none absolute -right-32 -top-32 h-80 w-80 rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-40 left-1/3 h-80 w-80 rounded-full bg-purple-500/10 blur-3xl" />

        <div className="relative">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-cyan-400">
                <Map className="h-4 w-4" />
                Career Roadmap
              </div>

              <h1 className="text-3xl font-extrabold tracking-tight text-white md:text-4xl">
                Your path from{" "}
                <span className="text-cyan-400">code</span> to{" "}
                <span className="text-purple-400">career</span>.
              </h1>

              <p className="mt-3 max-w-2xl text-sm leading-6 text-gray-400">
                {isJobSpecific
                  ? "A job-specific development plan built from the requirements of this role and the evidence already present in your GitHub profile."
                  : "A personalized development plan generated from your GitHub evidence and current development profile."}
              </p>
            </div>

            {isJobSpecific && (
              <div className="shrink-0 rounded-xl border border-cyan-500/20 bg-cyan-500/5 px-4 py-3">
                <p className="text-[10px] font-bold uppercase tracking-wider text-cyan-400">
                  Job-specific roadmap
                </p>

                <p className="mt-1 text-sm font-semibold text-white">
                  {roadmap.job_title || roadmap.target_role}
                </p>

                {roadmap.company && (
                  <p className="mt-0.5 text-xs text-gray-500">
                    {roadmap.company}
                  </p>
                )}
              </div>
            )}
          </div>

          {isJobSpecific && typeof roadmap.job_match_score === "number" && (
            <div className="relative mt-6 flex flex-wrap items-center gap-2 text-xs">
              <span className="rounded-full border border-cyan-500/20 bg-cyan-500/5 px-3 py-1.5 font-semibold text-cyan-300">
                Based on your analyzed job
              </span>

              <span className="text-gray-600">•</span>

              <span className="text-gray-400">
                Current match{" "}
                <strong className="text-purple-300">
                  {roadmap.job_match_score.toFixed(1)}%
                </strong>
              </span>
            </div>
          )}
        </div>
      </section>

      {/* SUMMARY */}
      <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="rounded-2xl border border-cyan-500/20 bg-gradient-to-br from-cyan-950/30 via-gray-900/70 to-gray-900 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
                {isJobSpecific ? "Target Role" : "Profile Focus"}
              </p>

              <h2 className="mt-2 text-xl font-bold text-white">
                {isJobSpecific
                  ? roadmap.target_role || roadmap.job_title || "Target role"
                  : "General Development"}
              </h2>
            </div>

            <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-cyan-500/20 bg-cyan-500/10">
              <Map className="h-5 w-5 text-cyan-400" />
            </div>
          </div>

          <p className="mt-4 text-xs leading-5 text-gray-400">
            Every roadmap task is selected to close the highest-impact gaps
            for this target.
          </p>
        </div>

        <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
                Roadmap Duration
              </p>

              <p className="mt-2 text-3xl font-extrabold text-white">
                {roadmap.duration_weeks || weeks.length || 6}
                <span className="ml-1 text-sm font-medium text-gray-500">
                  weeks
                </span>
              </p>
            </div>

            <Clock3 className="h-6 w-6 text-purple-400" />
          </div>

          <p className="mt-3 text-xs text-gray-500">
            Focused execution instead of random tutorial hopping.
          </p>
        </div>

        <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
                Progress
              </p>

              <p className="mt-2 text-3xl font-extrabold text-white">
                {progress}
                <span className="text-lg text-gray-500">%</span>
              </p>
            </div>

            <Trophy className="h-6 w-6 text-emerald-400" />
          </div>

          <div className="mt-4 h-2 overflow-hidden rounded-full bg-gray-800">
            <div
              className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>

          <p className="mt-2 text-xs text-gray-500">
            {completedCount} of {totalTasks} tasks completed
          </p>
        </div>
      </section>

      {/* SKILL GAP MATRIX */}
      <section className="rounded-2xl border border-gray-800 bg-gray-900/60 p-6">
        <div className="flex items-center gap-3 border-b border-gray-800 pb-5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10">
            <Layers className="h-5 w-5 text-purple-400" />
          </div>

          <div>
            <h2 className="font-bold text-white">Skill Gap Matrix</h2>
            <p className="mt-0.5 text-xs text-gray-500">
              {isJobSpecific
                ? "What GitVia sees against this specific job."
                : "What GitVia sees in your current profile."}
            </p>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-xl border border-emerald-500/20 bg-emerald-950/10 p-5">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                Strong
              </span>
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              {strongSkills.length > 0 ? (
                strongSkills.map((skill) => (
                  <span
                    key={skill}
                    className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 px-3 py-1.5 text-xs text-emerald-300"
                  >
                    {skill}
                  </span>
                ))
              ) : (
                <span className="text-xs text-gray-500">
                  No strong job-relevant skills identified.
                </span>
              )}
            </div>
          </div>

          <div className="rounded-xl border border-amber-500/20 bg-amber-950/10 p-5">
            <div className="flex items-center gap-2">
              <Wrench className="h-4 w-4 text-amber-400" />
              <span className="text-xs font-bold uppercase tracking-wider text-amber-400">
                Improving
              </span>
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              {improvingSkills.length > 0 ? (
                improvingSkills.map((skill) => (
                  <span
                    key={skill}
                    className="rounded-lg border border-amber-500/20 bg-amber-500/5 px-3 py-1.5 text-xs text-amber-300"
                  >
                    {skill}
                  </span>
                ))
              ) : (
                <span className="text-xs text-gray-500">
                  No improvement areas identified.
                </span>
              )}
            </div>
          </div>

          <div className="rounded-xl border border-rose-500/20 bg-rose-950/10 p-5">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-rose-400" />
              <span className="text-xs font-bold uppercase tracking-wider text-rose-400">
                Missing
              </span>
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              {missingSkills.length > 0 ? (
                missingSkills.map((skill) => (
                  <span
                    key={skill}
                    className="rounded-lg border border-rose-500/20 bg-rose-500/5 px-3 py-1.5 text-xs text-rose-300"
                  >
                    {skill}
                  </span>
                ))
              ) : (
                <span className="text-xs text-gray-500">
                  No missing skills identified.
                </span>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* EXECUTION PLAN */}
      <section>
        <div className="mb-5 flex items-end justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Flag className="h-5 w-5 text-cyan-400" />
              <h2 className="text-xl font-bold text-white">
                Execution Plan
              </h2>
            </div>

            <p className="mt-1 text-xs text-gray-500">
              Close the gaps. Build the evidence. Make the GitHub profile
              stronger.
            </p>
          </div>

          <div className="hidden items-center gap-2 text-xs text-gray-500 sm:flex">
            <Terminal className="h-4 w-4" />
            {totalTasks} actionable tasks
          </div>
        </div>

        <div className="space-y-4">
          {weeks.length === 0 ? (
            <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-8 text-center">
              <Code2 className="mx-auto h-8 w-8 text-gray-600" />
              <p className="mt-3 text-sm font-semibold text-gray-300">
                No roadmap tasks were returned.
              </p>
              <p className="mt-1 text-xs text-gray-500">
                Analyze a job from Career & Jobs and build its roadmap again.
              </p>
            </div>
          ) : (
            weeks.map((week, index) => {
              const weekNumber = week.week || index + 1;
              const isOpen = expandedWeek === weekNumber;
              const weekTasks = week.tasks || [];

              const weekCompleted = weekTasks.filter(
                (_, taskIndex) =>
                  completedTasks[`${weekNumber}-${taskIndex}`]
              ).length;

              return (
                <div
                  key={weekNumber}
                  className={`overflow-hidden rounded-2xl border transition-all ${
                    isOpen
                      ? "border-cyan-500/30 bg-gray-900/70"
                      : "border-gray-800 bg-gray-900/40"
                  }`}
                >
                  <button
                    type="button"
                    onClick={() =>
                      setExpandedWeek(isOpen ? null : weekNumber)
                    }
                    className="w-full px-6 py-5 text-left"
                  >
                    <div className="flex items-center gap-4">
                      <div
                        className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border text-sm font-extrabold ${
                          isOpen
                            ? "border-cyan-500/30 bg-cyan-500/10 text-cyan-400"
                            : "border-gray-700 bg-gray-950 text-gray-400"
                        }`}
                      >
                        {String(weekNumber).padStart(2, "0")}
                      </div>

                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="font-bold text-white">
                            {week.title}
                          </h3>

                          {weekCompleted > 0 && (
                            <span className="rounded-full border border-emerald-500/20 bg-emerald-500/5 px-2 py-0.5 text-[10px] font-semibold text-emerald-400">
                              {weekCompleted}/{weekTasks.length} done
                            </span>
                          )}
                        </div>

                        <p className="mt-1 text-xs leading-5 text-gray-500">
                          {week.description}
                        </p>
                      </div>

                      {isOpen ? (
                        <ChevronUp className="h-5 w-5 shrink-0 text-gray-500" />
                      ) : (
                        <ChevronDown className="h-5 w-5 shrink-0 text-gray-500" />
                      )}
                    </div>
                  </button>

                  {isOpen && (
                    <div className="border-t border-gray-800 px-6 pb-6 pt-5">
                      <div className="space-y-3">
                        {weekTasks.map((task, taskIndex) => {
                          const taskKey = `${weekNumber}-${taskIndex}`;
                          const completed = completedTasks[taskKey] || false;

                          const taskSkills =
                            task.skills ||
                            (task.skill ? [task.skill] : []);

                          return (
                            <div
                              key={taskKey}
                              className={`rounded-xl border p-4 transition-all ${
                                completed
                                  ? "border-emerald-500/20 bg-emerald-950/10"
                                  : "border-gray-800 bg-black/20 hover:border-gray-700"
                              }`}
                            >
                              <div className="flex items-start gap-4">
                                <button
                                  type="button"
                                  onClick={() =>
                                    toggleTask(weekNumber, taskIndex)
                                  }
                                  className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border transition-all ${
                                    completed
                                      ? "border-emerald-400 bg-emerald-400 text-black"
                                      : "border-gray-600 hover:border-cyan-400"
                                  }`}
                                  aria-label={
                                    completed
                                      ? "Mark task incomplete"
                                      : "Mark task complete"
                                  }
                                >
                                  {completed && (
                                    <CheckCircle2 className="h-4 w-4" />
                                  )}
                                </button>

                                <div className="min-w-0 flex-1">
                                  <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                                    <div>
                                      <h4
                                        className={`text-sm font-bold ${
                                          completed
                                            ? "text-emerald-300 line-through"
                                            : "text-white"
                                        }`}
                                      >
                                        {task.title}
                                      </h4>

                                      <p className="mt-1 text-xs leading-5 text-gray-500">
                                        {task.description}
                                      </p>
                                    </div>

                                    {task.estimated_hours && (
                                      <span className="inline-flex shrink-0 items-center gap-1 rounded-lg border border-gray-800 bg-gray-950 px-2 py-1 text-[10px] text-gray-400">
                                        <Clock3 className="h-3 w-3" />
                                        {task.estimated_hours}h
                                      </span>
                                    )}
                                  </div>

                                  {taskSkills.length > 0 && (
                                    <div className="mt-3 flex flex-wrap gap-2">
                                      {taskSkills.map((skill) => (
                                        <span
                                          key={skill}
                                          className="rounded-md border border-cyan-500/10 bg-cyan-500/5 px-2 py-1 text-[10px] font-medium text-cyan-300"
                                        >
                                          {skill}
                                        </span>
                                      ))}
                                    </div>
                                  )}
                                </div>

                                <ArrowRight className="mt-1 hidden h-4 w-4 shrink-0 text-gray-700 sm:block" />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </section>

      {/* FINAL CALLOUT */}
      <section className="relative overflow-hidden rounded-2xl border border-cyan-500/20 bg-gradient-to-r from-cyan-950/20 via-gray-900 to-purple-950/20 p-6 md:p-8">
        <div className="relative flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-cyan-400" />
              <h2 className="font-bold text-white">
                Turn roadmap items into GitHub evidence.
              </h2>
            </div>

            <p className="mt-2 max-w-2xl text-xs leading-5 text-gray-500">
              The goal is not to collect tutorials. Build projects, write
              tests, deploy them, and leave measurable evidence that GitVia
              can detect.
            </p>
          </div>

          <div className="flex shrink-0 items-center gap-2 rounded-xl border border-cyan-500/20 bg-cyan-500/5 px-4 py-3 text-xs font-semibold text-cyan-300">
            <Cpu className="h-4 w-4" />
            Build → Ship → Measure
          </div>
        </div>
      </section>
    </div>
  );
}
