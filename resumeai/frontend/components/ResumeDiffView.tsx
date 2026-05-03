"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronUp } from "lucide-react";
import type { ResumeSectionFix } from "@/lib/types";

interface ResumeDiffViewProps {
  fixes: ResumeSectionFix[];
}

function FixPair({
  original,
  rewritten,
  reason,
}: {
  original: string;
  rewritten: string;
  reason: string;
}) {
  return (
    <div className="space-y-2">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {/* Before */}
        <div className="rounded-xl border border-danger/20 bg-danger/5 p-4">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-danger/70">
            Before
          </p>
          <p className="text-sm leading-relaxed text-red-200">{original}</p>
        </div>
        {/* After */}
        <div className="rounded-xl border border-success/20 bg-success/5 p-4">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-success/70">
            After
          </p>
          <p className="text-sm leading-relaxed text-green-200">{rewritten}</p>
        </div>
      </div>
      {reason && (
        <div className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-3 py-1">
          <span className="text-xs text-secondary">{reason}</span>
        </div>
      )}
    </div>
  );
}

function SectionAccordion({ section }: { section: ResumeSectionFix }) {
  const [open, setOpen] = useState(true);

  return (
    <div className="rounded-2xl border border-white/[0.08] bg-card overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-6 py-4 hover:bg-card-hover transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="font-semibold text-primary">{section.section_name}</span>
          {section.fixes.length > 0 && (
            <span className="rounded-full bg-accent/10 border border-accent/20 px-2 py-0.5 text-xs text-accent">
              {section.fixes.length} fix{section.fixes.length > 1 ? "es" : ""}
            </span>
          )}
        </div>
        {open ? (
          <ChevronUp className="h-4 w-4 text-secondary" />
        ) : (
          <ChevronDown className="h-4 w-4 text-secondary" />
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
            <div className="space-y-4 px-6 pb-6">
              {/* Issues */}
              {section.issues.length > 0 && (
                <ul className="space-y-1">
                  {section.issues.map((issue, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-secondary">
                      <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-warning" />
                      {issue}
                    </li>
                  ))}
                </ul>
              )}

              {/* Fix pairs */}
              {section.fixes.length > 0 ? (
                <div className="space-y-5">
                  {section.fixes.map((fix, i) => (
                    <FixPair
                      key={i}
                      original={fix.original}
                      rewritten={fix.rewritten}
                      reason={fix.reason}
                    />
                  ))}
                </div>
              ) : (
                <p className="text-sm text-secondary italic">No rewrite suggestions for this section.</p>
              )}

              {/* Missing elements */}
              {section.missing_elements.length > 0 && (
                <div>
                  <p className="mb-2 text-sm font-semibold text-primary">Missing elements</p>
                  <div className="flex flex-wrap gap-2">
                    {section.missing_elements.map((el, i) => (
                      <span
                        key={i}
                        className="rounded-full border border-warning/20 bg-warning/10 px-3 py-1 text-xs text-warning"
                      >
                        {el}
                      </span>
                    ))}
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

export default function ResumeDiffView({ fixes }: ResumeDiffViewProps) {
  if (fixes.length === 0) {
    return (
      <div className="rounded-2xl border border-white/[0.08] bg-card p-8 text-center text-secondary">
        No fix suggestions available.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {fixes.map((section, i) => (
        <SectionAccordion key={i} section={section} />
      ))}
    </div>
  );
}
