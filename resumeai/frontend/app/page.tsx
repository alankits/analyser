import Link from "next/link";
import { Sparkles, FileText, BarChart3, Map, ArrowRight, CheckCircle2 } from "lucide-react";

const FEATURES = [
  {
    icon: BarChart3,
    title: "ATS Score Analysis",
    description:
      "Know exactly how your resume performs against Applicant Tracking Systems. Get keyword-level matching, section scores, and actionable fixes.",
    accent: "text-indigo-400",
    bg: "bg-indigo-500/10",
    border: "border-indigo-500/20",
  },
  {
    icon: FileText,
    title: "Resume Rewrites",
    description:
      "Every weak bullet point rewritten into STAR format with measurable outcomes. Side-by-side Before/After comparisons with clear reasons.",
    accent: "text-emerald-400",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/20",
  },
  {
    icon: Map,
    title: "Career Roadmap",
    description:
      "A personalised 3-phase learning plan built from your skill gaps. Specific resources, estimated hours, and portfolio milestones.",
    accent: "text-amber-400",
    bg: "bg-amber-500/10",
    border: "border-amber-500/20",
  },
];

const PROOF_POINTS = [
  "No sign-up required",
  "Results in under 60 seconds",
  "PDF report included",
];

export default function LandingPage() {
  return (
    <div className="relative overflow-hidden">
      {/* Background gradient orbs */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -left-64 -top-64 h-[600px] w-[600px] rounded-full bg-accent/10 blur-[120px]" />
        <div className="absolute -right-64 top-32 h-[500px] w-[500px] rounded-full bg-indigo-900/20 blur-[100px]" />
      </div>

      {/* ── HERO ────────────────────────────────────────────────────────────── */}
      <section className="relative mx-auto max-w-5xl px-4 pb-24 pt-24 text-center sm:px-6 lg:px-8">
        {/* Badge */}
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-accent/30 bg-accent/10 px-4 py-1.5 text-sm font-medium text-accent">
          <Sparkles className="h-3.5 w-3.5" />
          AI-Powered Resume Intelligence
        </div>

        {/* Headline */}
        <h1 className="text-5xl font-bold leading-[1.1] tracking-tight text-primary sm:text-6xl lg:text-7xl">
          Your Resume.{" "}
          <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-500 bg-clip-text text-transparent">
            Rebuilt by AI.
          </span>
        </h1>

        {/* Subline */}
        <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-secondary sm:text-xl">
          Upload your resume, get an ATS score, section-by-section rewrites, career role matches,
          and a personalised learning roadmap — all in one analysis.
        </p>

        {/* Proof points */}
        <div className="mt-6 flex flex-wrap items-center justify-center gap-4">
          {PROOF_POINTS.map((point) => (
            <div key={point} className="flex items-center gap-1.5 text-sm text-secondary">
              <CheckCircle2 className="h-4 w-4 text-success" />
              {point}
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="mt-10">
          <Link
            href="/analyze"
            className="group inline-flex items-center gap-2.5 rounded-xl bg-accent px-8 py-4 text-base font-bold text-white shadow-xl shadow-accent/25 transition-all hover:bg-accent-hover hover:shadow-accent/40 active:scale-95"
          >
            Analyze My Resume Free
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </Link>
          <p className="mt-3 text-xs text-secondary">
            Trusted by <span className="font-semibold text-primary">14,200+</span> job seekers
          </p>
        </div>
      </section>

      {/* ── FEATURE CARDS ──────────────────────────────────────────────────── */}
      <section className="relative mx-auto max-w-6xl px-4 pb-28 sm:px-6 lg:px-8">
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map(({ icon: Icon, title, description, accent, bg, border }) => (
            <div
              key={title}
              className={`rounded-2xl border ${border} bg-card p-6 transition-all hover:bg-card-hover hover:-translate-y-1 hover:shadow-xl`}
            >
              <div className={`mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl ${bg}`}>
                <Icon className={`h-6 w-6 ${accent}`} />
              </div>
              <h2 className="mb-2 text-lg font-bold text-primary">{title}</h2>
              <p className="text-sm leading-relaxed text-secondary">{description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── HOW IT WORKS ───────────────────────────────────────────────────── */}
      <section className="relative border-t border-white/[0.06] bg-card/50 px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="mb-12 text-3xl font-bold tracking-tight text-primary sm:text-4xl">
            How it works
          </h2>
          <div className="grid gap-8 sm:grid-cols-3">
            {[
              { step: "1", label: "Upload", desc: "Drop your PDF or DOCX resume" },
              { step: "2", label: "Analyze", desc: "AI reads and scores every section" },
              { step: "3", label: "Download", desc: "Get your full PDF report and roadmap" },
            ].map(({ step, label, desc }) => (
              <div key={step} className="flex flex-col items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-accent text-xl font-bold text-white">
                  {step}
                </div>
                <p className="font-semibold text-primary">{label}</p>
                <p className="text-sm text-secondary">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FOOTER ─────────────────────────────────────────────────────────── */}
      <footer className="border-t border-white/[0.06] py-8 text-center text-sm text-secondary">
        <p>
          <span className="font-semibold text-primary">ResumeAI</span> — AI-Powered Resume
          Analysis ·{" "}
          <a
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
            className="text-accent hover:underline"
          >
            GitHub
          </a>
        </p>
      </footer>
    </div>
  );
}
