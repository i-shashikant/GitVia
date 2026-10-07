import Link from "next/link";
import {
  ArrowRight,
  CheckCircle2,
  FileSearch,
  Layers,
  Map,
  ShieldCheck,
  Sparkles,
  Target,
  Workflow,
  Code,
} from "lucide-react";

import { GITHUB_LOGIN_URL } from "@/lib/api";
import { GithubIcon } from "@/components/icons/GithubIcon";

export default function Home() {
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "GitVia",
    applicationCategory: "DeveloperApplication",
    operatingSystem: "Web",
    description:
      "GitVia analyzes GitHub engineering evidence, matches developers against real job descriptions, identifies skill gaps, and builds personalized career roadmaps.",
  };

  return (
    <div className="space-y-20 py-6 pb-16">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(structuredData),
        }}
      />
      {/* HERO */}
      <section className="relative overflow-hidden rounded-3xl border border-gray-800 bg-gradient-to-br from-[#101722] via-[#0b111b] to-[#080c13] px-6 py-14 text-center shadow-2xl md:px-14 md:py-20">
        <div className="pointer-events-none absolute left-1/2 top-0 h-64 w-3/4 -translate-x-1/2 rounded-full bg-cyan-500/10 blur-[120px]" />
        <div className="pointer-events-none absolute -bottom-32 right-0 h-72 w-72 rounded-full bg-indigo-500/10 blur-3xl" />

        <div className="relative">
          <div className="mx-auto inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-950/50 px-4 py-1.5 text-xs font-semibold text-cyan-300">
            <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
            Evidence-driven career intelligence
          </div>

          <h1 className="mx-auto mt-7 max-w-5xl text-4xl font-black tracking-tight text-white sm:text-6xl md:text-7xl">
            Turn your GitHub into a
            <br />
            <span className="bg-gradient-to-r from-cyan-400 via-teal-300 to-indigo-400 bg-clip-text text-transparent">
              career strategy.
            </span>
          </h1>

          <p className="mx-auto mt-7 max-w-3xl text-base leading-8 text-gray-300 md:text-lg">
            GitVia analyzes what you actually build, measures engineering
            evidence across your repositories, compares your profile with a
            real job description, and turns the gaps into a practical roadmap.
          </p>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <a
              href={GITHUB_LOGIN_URL}
              className="inline-flex items-center gap-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-7 py-3.5 text-base font-bold text-white shadow-xl shadow-cyan-500/20 transition hover:-translate-y-0.5 hover:shadow-cyan-500/30"
            >
              <GithubIcon className="h-5 w-5" />
              Continue with GitHub
            </a>

            <Link
              href="#about-gitvia"
              className="inline-flex items-center gap-2 rounded-xl border border-gray-700 bg-gray-900/80 px-6 py-3.5 text-base font-semibold text-gray-200 transition hover:border-cyan-500/30 hover:bg-gray-800"
            >
              Explore GitVia
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          <div className="mx-auto mt-12 grid max-w-4xl grid-cols-2 gap-3 border-t border-gray-800/80 pt-8 text-left sm:grid-cols-4">
            <Metric value="6" label="Engineering dimensions" />
            <Metric value="100+" label="Technical skills detected" />
            <Metric value="1 → 1" label="Job-specific matching" />
            <Metric value="6 weeks" label="Action roadmap" />
          </div>
        </div>
      </section>

      {/* WHAT IS GITVIA */}
      <section id="about-gitvia" className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-400">
            About GitVia
          </p>
          <h2 className="mt-3 text-3xl font-black tracking-tight text-white md:text-4xl">
            Your GitHub is evidence.
            <br />
            GitVia makes it useful.
          </h2>
          <p className="mt-5 max-w-2xl text-sm leading-7 text-gray-400 md:text-base">
            Most career advice starts with generic checklists. GitVia starts
            with your existing work. It inspects repository structure,
            documentation, testing, DevOps and scalability signals, builds a
            developer profile, and then connects that evidence to the roles
            you actually want.
          </p>
          <p className="mt-4 max-w-2xl text-sm leading-7 text-gray-500 md:text-base">
            The goal is not to invent impressive numbers. Scores come from
            deterministic analysis, while the roadmap tells you what evidence
            to build next.
          </p>
        </div>

        <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-6">
          <div className="space-y-5">
            <FlowRow icon={<GithubIcon className="h-4 w-4" />} title="GitHub evidence" text="Repositories, structure, code, tests, Docker and CI." />
            <FlowRow icon={<FileSearch className="h-4 w-4" />} title="Career analysis" text="Profile strengths, gaps and resume alignment." />
            <FlowRow icon={<Target className="h-4 w-4" />} title="Real job matching" text="Compare your evidence with an actual JD." />
            <FlowRow icon={<Map className="h-4 w-4" />} title="Action roadmap" text="Turn missing evidence into weekly execution." />
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="space-y-8">
        <div className="text-center">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-400">
            How it works
          </p>
          <h2 className="mt-3 text-3xl font-black text-white md:text-4xl">
            From code to a concrete next move.
          </h2>
          <p className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-gray-500">
            Four connected stages turn scattered GitHub activity into a career
            workflow.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          <FeatureCard number="01" icon={<GithubIcon className="h-5 w-5" />} title="Analyze GitHub" text="Inspect repositories using a transparent engineering rubric instead of star counts." />
          <FeatureCard number="02" icon={<ShieldCheck className="h-5 w-5" />} title="Build your profile" text="Aggregate repository evidence into strengths, weaknesses and career readiness signals." />
          <FeatureCard number="03" icon={<Target className="h-5 w-5" />} title="Match a job" text="Paste a real job description and see strong, improving and missing requirements." />
          <FeatureCard number="04" icon={<Map className="h-5 w-5" />} title="Execute the roadmap" text="Get a job-specific six-week plan focused on evidence you can actually build." />
        </div>
      </section>

      {/* WHY IT IS DIFFERENT */}
      <section className="rounded-3xl border border-gray-800 bg-gray-900/40 p-7 md:p-10">
        <div className="grid gap-8 lg:grid-cols-2">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-400">
              Why GitVia
            </p>
            <h2 className="mt-3 text-3xl font-black text-white">
              Less tutorial hopping. More evidence.
            </h2>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Point text="Repository quality is measured from actual project evidence." />
            <Point text="Resume claims can be checked against GitHub evidence." />
            <Point text="Job gaps come from the requirements you paste." />
            <Point text="Roadmaps prioritize your existing projects over random new apps." />
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative overflow-hidden rounded-3xl border border-cyan-500/20 bg-gradient-to-r from-cyan-950/30 via-gray-900 to-indigo-950/30 p-8 text-center md:p-12">
        <Workflow className="mx-auto h-8 w-8 text-cyan-400" />
        <h2 className="mt-4 text-3xl font-black text-white">
          See what your code says about you.
        </h2>
        <p className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-gray-400">
          Connect GitHub, analyze your repositories, and turn your next career
          move into something measurable.
        </p>
        <a
          href={GITHUB_LOGIN_URL}
          className="mt-7 inline-flex items-center gap-2 rounded-xl bg-cyan-500 px-6 py-3 font-bold text-black transition hover:bg-cyan-400"
        >
          Start with GitHub
          <ArrowRight className="h-4 w-4" />
        </a>
      </section>
    </div>
  );
}

function Metric({ value, label }: { value: string; label: string }) {
  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-4">
      <div className="text-2xl font-black text-cyan-400">{value}</div>
      <div className="mt-1 text-xs text-gray-500">{label}</div>
    </div>
  );
}

function FlowRow({ icon, title, text }: { icon: React.ReactNode; title: string; text: string }) {
  return (
    <div className="flex gap-3">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-cyan-500/20 bg-cyan-500/10 text-cyan-400">
        {icon}
      </div>
      <div>
        <h3 className="text-sm font-bold text-white">{title}</h3>
        <p className="mt-1 text-xs leading-5 text-gray-500">{text}</p>
      </div>
    </div>
  );
}

function FeatureCard({ number, icon, title, text }: { number: string; icon: React.ReactNode; title: string; text: string }) {
  return (
    <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-6 transition hover:-translate-y-0.5 hover:border-cyan-500/30">
      <div className="flex items-center justify-between">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-cyan-500/20 bg-cyan-500/10 text-cyan-400">
          {icon}
        </div>
        <span className="font-mono text-xs text-gray-700">{number}</span>
      </div>
      <h3 className="mt-5 text-lg font-bold text-white">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-gray-500">{text}</p>
    </div>
  );
}

function Point({ text }: { text: string }) {
  return (
    <div className="flex gap-2 text-sm leading-6 text-gray-400">
      <CheckCircle2 className="mt-1 h-4 w-4 shrink-0 text-emerald-400" />
      <span>{text}</span>
    </div>
  );
}
