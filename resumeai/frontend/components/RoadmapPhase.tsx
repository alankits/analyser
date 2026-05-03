"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronUp, Clock, Target } from "lucide-react";
import type { Roadmap, RoadmapPhaseData } from "@/lib/types";

interface RoadmapPhaseProps {
  roadmap: Roadmap;
}

const PHASE_STYLES = [
  {
    badge: "bg-accent text-white",
    border: "border-indigo-500/20",
    milestone: "border-l-accent",
    tag: "bg-accent/10 text-accent border-accent/20",
    hours: "bg-indigo-900/40 text-indigo-300",
  },
  {
    badge: "bg-success text-white",
    border: "border-emerald-500/20",
    milestone: "border-l-success",
    tag: "bg-success/10 text-success border-success/20",
    hours: "bg-emerald-900/40 text-emerald-300",
  },
  {
    badge: "bg-warning text-black",
    border: "border-amber-500/20",
    milestone: "border-l-warning",
    tag: "bg-warning/10 text-warning border-warning/20",
    hours: "bg-amber-900/40 text-amber-300",
  },
];

function PhasePanel({
  phase,
  phaseIndex,
}: {
  phase: RoadmapPhaseData;
  phaseIndex: number;
}) {
  const [open, setOpen] = useState(phaseIndex === 0);
  const style = PHASE_STYLES[phaseIndex % PHASE_STYLES.length];

  const phaseHours = phase.skills.reduce((sum, s) => sum + s.estimated_hours, 0);

  return (
    <div className={`rounded-2xl border ${style.border} bg-card overflow-hidden`}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-4 px-6 py-4 hover:bg-card-hover transition-colors"
      >
        {/* Phase badge */}
        <span
          className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-sm font-bold ${style.badge}`}
        >
          {phase.phase_number}
        </span>

        <div className="flex-1 text-left">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-semibold text-primary">{phase.duration}</span>
            <span className="hidden sm:inline text-secondary">·</span>
            <span className="hidden sm:inline text-sm text-secondary">{phaseHours}h estimated</span>
          </div>
          <p className="mt-0.5 text-sm text-secondary leading-snug">{phase.goal}</p>
        </div>

        {open ? (
          <ChevronUp className="h-4 w-4 flex-shrink-0 text-secondary" />
        ) : (
          <ChevronDown className="h-4 w-4 flex-shrink-0 text-secondary" />
        )}
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="space-y-3 px-6 pb-6">
              {/* Skills table */}
              {phase.skills.length > 0 && (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/[0.06]">
                        <th className="py-2 text-left text-xs font-semibold uppercase tracking-wider text-secondary">Skill</th>
                        <th className="py-2 text-left text-xs font-semibold uppercase tracking-wider text-secondary">Why It Matters</th>
                        <th className="py-2 text-left text-xs font-semibold uppercase tracking-wider text-secondary">Resource</th>
                        <th className="py-2 text-right text-xs font-semibold uppercase tracking-wider text-secondary">Hours</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/[0.04]">
                      {phase.skills.map((skill, i) => (
                        <tr key={i} className="group">
                          <td className="py-3 pr-4 font-medium text-primary align-top">{skill.skill_name}</td>
                          <td className="py-3 pr-4 text-secondary leading-relaxed align-top max-w-[280px]">
                            {skill.why_it_matters}
                          </td>
                          <td className="py-3 pr-4 align-top">
                            <span className={`rounded-full border px-2.5 py-0.5 text-xs ${style.tag}`}>
                              {skill.resource_type}
                            </span>
                          </td>
                          <td className="py-3 text-right align-top">
                            <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${style.hours}`}>
                              {skill.estimated_hours}h
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Milestone */}
              {phase.milestone && (
                <div
                  className={`mt-4 rounded-r-xl border-l-4 ${style.milestone} bg-accent/5 px-4 py-3`}
                >
                  <div className="flex items-start gap-2">
                    <Target className="mt-0.5 h-4 w-4 flex-shrink-0 text-accent" />
                    <div>
                      <p className="text-xs font-semibold text-accent mb-1">Phase Milestone</p>
                      <p className="text-sm text-secondary leading-relaxed">{phase.milestone}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function RoadmapPhase({ roadmap }: RoadmapPhaseProps) {
  return (
    <div className="space-y-4">
      {/* Header stats */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-white/[0.08] bg-card px-5 py-4">
        <div>
          <p className="text-sm text-secondary">Target Role</p>
          <p className="font-bold text-primary">{roadmap.target_role}</p>
        </div>
        <div>
          <p className="text-sm text-secondary">Current Level</p>
          <p className="font-bold text-primary">{roadmap.current_level}</p>
        </div>
        <div className="flex items-center gap-2 rounded-xl border border-accent/20 bg-accent/10 px-4 py-2">
          <Clock className="h-4 w-4 text-accent" />
          <span className="font-bold text-accent">{roadmap.total_estimated_hours}h</span>
          <span className="text-xs text-secondary">total</span>
        </div>
      </div>

      {/* Phase accordions */}
      {roadmap.phases.map((phase, i) => (
        <PhasePanel key={phase.phase_number} phase={phase} phaseIndex={i} />
      ))}
    </div>
  );
}
