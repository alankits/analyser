"use client";

import { useEffect, useRef, useState } from "react";
import { motion, useSpring, useTransform } from "framer-motion";
import { ChevronDown, ChevronUp } from "lucide-react";
import type { ATSResult } from "@/lib/types";

interface ATSScoreCardProps {
  data: ATSResult;
}

const GRADE_COLORS: Record<string, string> = {
  A: "text-success",
  B: "text-success",
  C: "text-warning",
  D: "text-warning",
  F: "text-danger",
};

const GRADE_BG: Record<string, string> = {
  A: "bg-success/10 border-success/30",
  B: "bg-success/10 border-success/30",
  C: "bg-warning/10 border-warning/30",
  D: "bg-warning/10 border-warning/30",
  F: "bg-danger/10 border-danger/30",
};

function ScoreRing({ score }: { score: number }) {
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const springScore = useSpring(0, { stiffness: 60, damping: 20 });
  const strokeDashoffset = useTransform(
    springScore,
    [0, 100],
    [circumference, circumference - (circumference * score) / 100]
  );

  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    springScore.set(score);
    const unsub = springScore.onChange((v) => setDisplayScore(Math.round(v)));
    return unsub;
  }, [score, springScore]);

  const color =
    score >= 80 ? "#10B981" : score >= 60 ? "#F59E0B" : "#EF4444";

  return (
    <div className="relative flex items-center justify-center">
      <svg width="180" height="180" className="-rotate-90">
        {/* Track */}
        <circle
          cx="90"
          cy="90"
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth="12"
        />
        {/* Progress */}
        <motion.circle
          cx="90"
          cy="90"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={circumference}
          style={{ strokeDashoffset }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-4xl font-bold text-primary">{displayScore}</span>
        <span className="text-xs text-secondary mt-0.5">/ 100</span>
      </div>
    </div>
  );
}

export default function ATSScoreCard({ data }: ATSScoreCardProps) {
  const [keywordsExpanded, setKeywordsExpanded] = useState(false);

  const presentKws = data.keyword_analysis.filter((k) => k.present);
  const missingKws = data.keyword_analysis.filter((k) => !k.present);

  return (
    <div className="rounded-2xl border border-white/[0.08] bg-card p-6 space-y-6">
      {/* Score ring + grade */}
      <div className="flex flex-col items-center sm:flex-row sm:items-start gap-6">
        <ScoreRing score={data.overall_score} />

        <div className="flex-1 space-y-4">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold text-primary">ATS Score</h2>
            <span
              className={`rounded-full border px-3 py-0.5 text-sm font-bold ${GRADE_COLORS[data.grade] || "text-secondary"} ${GRADE_BG[data.grade] || "bg-white/5 border-white/10"}`}
            >
              Grade {data.grade}
            </span>
          </div>

          {/* Section scores */}
          <div className="space-y-2">
            {Object.entries(data.section_scores).map(([section, score]) => (
              <div key={section} className="flex items-center gap-3">
                <span className="w-24 text-xs text-secondary capitalize">{section}</span>
                <div className="flex-1 h-2 rounded-full bg-white/5 overflow-hidden">
                  <motion.div
                    className="h-full rounded-full"
                    style={{
                      background:
                        score >= 75
                          ? "#10B981"
                          : score >= 50
                          ? "#F59E0B"
                          : "#EF4444",
                    }}
                    initial={{ width: 0 }}
                    animate={{ width: `${score}%` }}
                    transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
                  />
                </div>
                <span className="w-8 text-right text-xs text-secondary">{score}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Top issues */}
      {data.top_issues.length > 0 && (
        <div>
          <h3 className="mb-2 text-sm font-semibold text-primary">Top Issues</h3>
          <ul className="space-y-1.5">
            {data.top_issues.map((issue, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-secondary">
                <span className="mt-0.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-warning" />
                {issue}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Missing sections */}
      {data.missing_sections.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {data.missing_sections.map((s) => (
            <span
              key={s}
              className="rounded-full border border-danger/30 bg-danger/10 px-3 py-1 text-xs font-medium text-danger"
            >
              Missing: {s}
            </span>
          ))}
        </div>
      )}

      {/* Keyword grid */}
      {data.keyword_analysis.length > 0 && (
        <div>
          <button
            onClick={() => setKeywordsExpanded((v) => !v)}
            className="flex w-full items-center justify-between rounded-lg border border-white/[0.08] bg-card-hover px-4 py-2.5 text-sm font-medium text-primary hover:border-accent/30 transition-colors"
          >
            <span>
              Keyword Analysis · {presentKws.length} present, {missingKws.length} missing
            </span>
            {keywordsExpanded ? (
              <ChevronUp className="h-4 w-4 text-secondary" />
            ) : (
              <ChevronDown className="h-4 w-4 text-secondary" />
            )}
          </button>

          {keywordsExpanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="flex flex-wrap gap-2 pt-4"
            >
              {data.keyword_analysis.map((kw) => (
                <span
                  key={kw.keyword}
                  className={`rounded-full px-3 py-1 text-xs font-medium border ${
                    kw.present
                      ? "bg-success/10 text-success border-success/20"
                      : "bg-danger/10 text-danger border-danger/20"
                  }`}
                >
                  {kw.present ? "✓" : "✗"} {kw.keyword}
                  {kw.importance === "high" && (
                    <span className="ml-1 opacity-60">•••</span>
                  )}
                </span>
              ))}
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
}
