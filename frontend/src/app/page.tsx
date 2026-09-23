"use client";

import Link from "next/link";
import { 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRight, 
  ShieldCheck, 
  Terminal, 
  Layers, 
  Cpu, 
  Compass
} from "lucide-react";
import { GITHUB_LOGIN_URL } from "@/lib/api";
import { GithubIcon } from "@/components/icons/GithubIcon";

export default function Home() {
  return (
    <div className="space-y-16 py-6">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl border border-gray-800 bg-gradient-to-b from-gray-900/90 via-gray-900/50 to-[#0b0f19] p-8 md:p-14 text-center shadow-2xl">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-32 bg-cyan-500/10 blur-[120px] pointer-events-none" />

        <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-950/60 px-4 py-1.5 text-xs font-semibold text-cyan-300 backdrop-blur-md mb-6">
          <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
          <span>Evidence from GitHub structure — README, tests, Docker, CI — not star counts</span>
        </div>

        <h1 className="mx-auto max-w-4xl text-4xl font-extrabold tracking-tight text-white sm:text-6xl leading-tight">
          From what you build to <br />
          <span className="bg-gradient-to-r from-cyan-400 via-teal-300 to-indigo-400 bg-clip-text text-transparent">
            where you go next.
          </span>
        </h1>

        <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-300 leading-relaxed">
          GitVia scores your <strong>GitHub repositories</strong> with a documented rubric, compares that evidence to your <strong>resume</strong> and a <strong>job description</strong>, then builds a week-by-week plan. Scores are deterministic heuristics — not an LLM inventing a 92/100.
        </p>

        {/* CTA Buttons */}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <a
            href={GITHUB_LOGIN_URL}
            className="flex items-center gap-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-7 py-3.5 text-base font-bold text-white shadow-xl shadow-cyan-500/25 hover:scale-105 transition-all"
          >
            <GithubIcon className="h-5 w-5" />
            <span>Continue with GitHub</span>
          </a>

          <Link
            href="/dashboard"
            className="flex items-center gap-2 rounded-xl border border-gray-700 bg-gray-800/80 px-6 py-3.5 text-base font-semibold text-gray-200 hover:bg-gray-700 transition-all"
          >
            <span>Open dashboard</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>

        {/* Floating Metrics Showcase */}
        <div className="mt-14 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-4xl mx-auto border-t border-gray-800/80 pt-8 text-left">
          <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-4">
            <div className="text-2xl font-bold text-cyan-400">81 / 100</div>
            <div className="text-xs text-gray-400 mt-1">Portfolio Score</div>
          </div>
          <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-4">
            <div className="text-2xl font-bold text-emerald-400">82%</div>
            <div className="text-xs text-gray-400 mt-1">Project Quality Score</div>
          </div>
          <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-4">
            <div className="text-2xl font-bold text-amber-400">76%</div>
            <div className="text-xs text-gray-400 mt-1">Internship Match</div>
          </div>
          <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-4">
            <div className="text-2xl font-bold text-purple-400">6 Weeks</div>
            <div className="text-xs text-gray-400 mt-1">Action Roadmap</div>
          </div>
        </div>
      </section>

      {/* Differentiators Grid */}
      <section className="space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-bold text-white">What makes GitVia outstanding</h2>
          <p className="text-gray-400 text-sm">Deep inspection beyond surface commit counts or star counts.</p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {/* Card 1 */}
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-6 space-y-4 hover:border-cyan-500/50 transition-all">
            <div className="h-10 w-10 rounded-lg bg-cyan-950 border border-cyan-800 flex items-center justify-center text-cyan-400">
              <Cpu className="h-5 w-5" />
            </div>
            <h3 className="text-xl font-semibold text-white">Repository Quality Analyzer ⭐</h3>
            <p className="text-sm text-gray-400 leading-relaxed">
              Analyzes architecture, modularity, test coverage, Docker containerization, CI/CD pipelines, and README completeness to generate a 0-100 Quality Score.
            </p>
          </div>

          {/* Card 2 */}
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-6 space-y-4 hover:border-cyan-500/50 transition-all">
            <div className="h-10 w-10 rounded-lg bg-amber-950 border border-amber-800 flex items-center justify-center text-amber-400">
              <AlertTriangle className="h-5 w-5" />
            </div>
            <h3 className="text-xl font-semibold text-white">Resume ↔ GitHub Mismatch</h3>
            <p className="text-sm text-gray-400 leading-relaxed">
              Cross-references self-declared resume claims against actual GitHub repository code. Flags claims lacking empirical code evidence before recruiters do.
            </p>
          </div>

          {/* Card 3 */}
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-6 space-y-4 hover:border-cyan-500/50 transition-all">
            <div className="h-10 w-10 rounded-lg bg-purple-950 border border-purple-800 flex items-center justify-center text-purple-400">
              <Compass className="h-5 w-5" />
            </div>
            <h3 className="text-xl font-semibold text-white">Personalized Project Roadmap</h3>
            <p className="text-sm text-gray-400 leading-relaxed">
              Forget generic tutorial lists. Tells you: <em>"Don't build another Todo app. Add Docker + CI/CD to your existing project X."</em>
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
