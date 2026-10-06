"use client";

import { useState } from "react";
import { uploadResume, analyzeJobDescription } from "@/lib/api";
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
  ShieldAlert
} from "lucide-react";

export default function CareerPage() {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeResult, setResumeResult] = useState<any>(null);
  const [uploading, setUploading] = useState(false);

  const [jobTitle, setJobTitle] = useState("Amazon SDE Intern");
  const [company, setCompany] = useState("Amazon");
  const [jobText, setJobText] = useState(
    `Amazon Software Development Engineer Intern
Requirements:
- Strong fundamentals in Python, Data Structures, and Relational Databases (SQL).
- Experience building REST APIs using FastAPI or Django.
- Containerization experience with Docker and basic AWS cloud services.
- Familiarity with Pytest, CI/CD, Redis, and Kubernetes preferred.`
  );
  const [jobResult, setJobResult] = useState<any>(null);
  const [analyzingJob, setAnalyzingJob] = useState(false);

  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || !e.target.files[0]) return;
    const file = e.target.files[0];
    setResumeFile(file);
    setUploading(true);

    try {
      const data = await uploadResume(file);
      setResumeResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const handleJobAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setAnalyzingJob(true);

    try {
      const data = await analyzeJobDescription(jobTitle, company, jobText);
      setJobResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setAnalyzingJob(false);
    }
  };

  return (
    <div className="space-y-10 pb-12">
      {/* Header */}
      <div className="border-b border-gray-800 pb-6">
        <h1 className="text-3xl font-extrabold text-white">Career Intelligence & Job Matcher</h1>
        <p className="text-sm text-gray-400 mt-1">
          Upload your resume to detect claims unsupported by code, and paste target job specs for multi-factor match evaluation.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column: Resume Analyzer */}
        <div className="space-y-6">
          <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-6 space-y-6">
            <div className="border-b border-gray-800 pb-4">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <FileText className="h-5 w-5 text-cyan-400" />
                Resume Analyzer
              </h2>
              <p className="text-xs text-gray-400 mt-0.5">Upload your PDF resume to extract skills and detect GitHub code mismatches.</p>
            </div>

            {/* Upload Input */}
            <div className="relative border-2 border-dashed border-gray-700 hover:border-cyan-500/50 rounded-xl p-6 text-center space-y-3 bg-gray-900/40 transition-colors">
              <Upload className="mx-auto h-8 w-8 text-cyan-400" />
              <div className="text-xs text-gray-300">
                <label className="cursor-pointer font-bold text-cyan-400 hover:underline">
                  <span>Choose PDF file</span>
                  <input type="file" accept=".pdf" className="hidden" onChange={handleResumeUpload} />
                </label>
                <span className="text-gray-400"> or drag and drop</span>
              </div>
              <p className="text-[10px] text-gray-400">PyMuPDF structured extraction engine</p>
            </div>

            {uploading && (
              <div className="text-xs text-cyan-400 flex items-center gap-2 justify-center py-2">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
                <span>Extracting resume skills & checking GitHub code evidence...</span>
              </div>
            )}

            {/* Resume Mismatch Warnings Panel */}
            {resumeResult && (
              <div className="space-y-4 pt-2">
                <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-4 space-y-3">
                  <div className="flex items-center gap-2 text-xs font-bold text-amber-400 uppercase tracking-wider">
                    <ShieldAlert className="h-4 w-4" />
                    <span>⚠️ Resume ↔ GitHub Code Mismatch</span>
                  </div>
                  {resumeResult.mismatch_flags?.map((flag: any, idx: number) => (
                    <div key={idx} className="text-xs text-gray-300 space-y-1 border-t border-amber-800/40 pt-2">
                      <div className="font-semibold text-amber-300">{flag.message}</div>
                      <div className="text-gray-400 text-[11px]">💡 Action: {flag.action}</div>
                    </div>
                  ))}
                </div>

                {/* Bullet Optimization */}
                <div className="rounded-xl border border-gray-800 bg-gray-900/80 p-4 space-y-3">
                  <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Suggested Bullet Enhancements</span>
                  {resumeResult.bullets_suggestions?.map((b: any, idx: number) => (
                    <div key={idx} className="text-xs space-y-1 border-t border-gray-800 pt-2">
                      <div className="text-rose-400 line-through">❌ {b.original}</div>
                      <div className="text-emerald-400 font-medium">✓ {b.improved}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Job Description & Skill Gap Analyzer */}
        <div className="space-y-6">
          <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-6 space-y-6">
            <div className="border-b border-gray-800 pb-4">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Briefcase className="h-5 w-5 text-purple-400" />
                Job Description Matcher ⭐
              </h2>
              <p className="text-xs text-gray-400 mt-0.5">Paste target job description to compute percentage match score and skill gaps.</p>
            </div>

            <form onSubmit={handleJobAnalyze} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-gray-400 font-medium">Role Title</label>
                  <input
                    type="text"
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    className="mt-1 w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="text-gray-400 font-medium">Company</label>
                  <input
                    type="text"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    className="mt-1 w-full rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="text-gray-400 font-medium">Job Description Text</label>
                <textarea
                  rows={5}
                  value={jobText}
                  onChange={(e) => setJobText(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-gray-700 bg-gray-900 p-3 text-white focus:border-cyan-500 focus:outline-none font-mono text-[11px]"
                />
              </div>

              <button
                type="submit"
                disabled={analyzingJob}
                className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-4 py-3 font-bold text-white shadow-lg shadow-cyan-500/20 hover:opacity-90 transition-all"
              >
                {analyzingJob ? "Analyzing Job Requirements..." : "Calculate Job Match & Skill Gap Matrix"}
              </button>
            </form>

            {/* Job Match Result & Skill Gap Matrix ⭐ */}
            {jobResult && (
              <div className="space-y-6 pt-4 border-t border-gray-800">
                {/* Match Score Banner */}
                <div className="rounded-xl border border-cyan-500/30 bg-cyan-950/40 p-5">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
                        {jobResult.company} Match Score
                      </span>

                      <div className="text-4xl font-extrabold text-white mt-1">
                        {jobResult.overall_match_score ?? jobResult.match_score ?? 0}%
                      </div>
                    </div>

                    <div className="text-right text-xs space-y-1.5 font-mono text-gray-300">
                      <div>
                        Technical:{" "}
                        <span className="text-cyan-400 font-bold">
                          {jobResult.tech_score ?? 0}%
                        </span>
                      </div>

                      <div>
                        Projects:{" "}
                        <span className="text-emerald-400 font-bold">
                          {jobResult.project_score ?? 0}%
                        </span>
                      </div>

                      <div>
                        Experience:{" "}
                        <span className="text-purple-400 font-bold">
                          {jobResult.experience_score ?? 0}%
                        </span>
                      </div>

                      <div>
                        DevOps:{" "}
                        <span className="text-amber-400 font-bold">
                          {jobResult.devops_score ?? 0}%
                        </span>
                      </div>

                      <div>
                        Problem Solving:{" "}
                        <span className="text-rose-400 font-bold">
                          {jobResult.problem_solving_score ?? 0}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Skill Gap Matrix ⭐ */}
                <div className="space-y-3">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-cyan-400" />
                    Skill Gap Analysis Matrix ⭐
                  </h3>

                  <div className="grid grid-cols-3 gap-3 text-xs">
                    {/* Already Strong */}
                    <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-3 space-y-2">
                      <div className="font-bold text-emerald-400 flex items-center gap-1">
                        <CheckCircle2 className="h-3.5 w-3.5" />
                        Already Strong ✓
                      </div>
                      <ul className="space-y-1 text-[11px] text-gray-300">
                        {jobResult.skill_gaps?.strong?.map((s: string, i: number) => (
                          <li key={i}>• {s}</li>
                        ))}
                      </ul>
                    </div>

                    {/* Need Improvement */}
                    <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-3 space-y-2">
                      <div className="font-bold text-amber-400 flex items-center gap-1">
                        <AlertTriangle className="h-3.5 w-3.5" />
                        Need Improvement ⚠
                      </div>
                      <ul className="space-y-1 text-[11px] text-gray-300">
                        {jobResult.skill_gaps?.improving?.map((s: string, i: number) => (
                          <li key={i}>• {s}</li>
                        ))}
                      </ul>
                    </div>

                    {/* Missing */}
                    <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-3 space-y-2">
                      <div className="font-bold text-rose-400 flex items-center gap-1">
                        <XCircle className="h-3.5 w-3.5" />
                        Missing ✕
                      </div>
                      <ul className="space-y-1 text-[11px] text-gray-300">
                        {jobResult.skill_gaps?.missing?.map((s: string, i: number) => (
                          <li key={i}>• {s}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
