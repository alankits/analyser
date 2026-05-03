"use client";

import { motion } from "framer-motion";
import { Briefcase, Clock, BookOpen } from "lucide-react";
import type { CareerRole } from "@/lib/types";

interface CareerRoleCardProps {
  role: CareerRole;
  index: number;
}

const CARD_ACCENT_COLORS = [
  { bar: "from-indigo-500 to-indigo-700", score: "text-indigo-400", border: "border-indigo-500/20" },
  { bar: "from-teal-500 to-emerald-600", score: "text-teal-400", border: "border-teal-500/20" },
  { bar: "from-purple-500 to-violet-700", score: "text-purple-400", border: "border-purple-500/20" },
];

export default function CareerRoleCard({ role, index }: CareerRoleCardProps) {
  const accent = CARD_ACCENT_COLORS[index % CARD_ACCENT_COLORS.length];

  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
      className={`relative rounded-2xl border ${accent.border} bg-card overflow-hidden shadow-lg hover:shadow-xl hover:shadow-accent/5 transition-shadow`}
    >
      {/* Top color bar */}
      <div className={`h-1 w-full bg-gradient-to-r ${accent.bar}`} />

      <div className="p-5 space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="font-bold text-primary text-lg leading-tight">{role.role_title}</h3>
            <span className="mt-1 inline-block rounded-full border border-white/10 bg-white/5 px-2.5 py-0.5 text-xs text-secondary">
              {role.seniority_target}
            </span>
          </div>
          <span className={`text-2xl font-bold ${accent.score}`}>{role.match_score}%</span>
        </div>

        {/* Match bar */}
        <div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-white/5">
            <motion.div
              className={`h-full rounded-full bg-gradient-to-r ${accent.bar}`}
              initial={{ width: 0 }}
              animate={{ width: `${role.match_score}%` }}
              transition={{ duration: 1, ease: "easeOut", delay: 0.1 * index }}
            />
          </div>
          <p className="mt-1 text-right text-xs text-secondary">Match score</p>
        </div>

        {/* Match reasons */}
        {role.match_reasons.length > 0 && (
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-secondary">
              Why you match
            </p>
            <ul className="space-y-1.5">
              {role.match_reasons.map((reason, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-secondary">
                  <span className="mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-success" />
                  {reason}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Skill gaps */}
        {role.skill_gaps.length > 0 && (
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-secondary">
              Skill gaps
            </p>
            <div className="flex flex-wrap gap-1.5">
              {role.skill_gaps.map((gap, i) => (
                <span
                  key={i}
                  className="rounded-full border border-danger/20 bg-danger/10 px-2.5 py-1 text-xs text-danger"
                >
                  {gap}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Time to ready */}
        <div className="flex items-center gap-2 text-sm text-secondary">
          <Clock className="h-3.5 w-3.5 flex-shrink-0" />
          {role.time_to_ready}
        </div>

        {/* Recommended project */}
        {role.recommended_project && (
          <div className="rounded-xl border border-accent/20 bg-accent/5 p-3">
            <div className="flex items-start gap-2">
              <BookOpen className="mt-0.5 h-4 w-4 flex-shrink-0 text-accent" />
              <div>
                <p className="text-xs font-semibold text-accent mb-1">Recommended Project</p>
                <p className="text-xs text-secondary leading-relaxed">{role.recommended_project}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
