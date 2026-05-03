"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Download, Loader2 } from "lucide-react";
import { downloadReport } from "@/lib/api";

interface DownloadReportBtnProps {
  analysisId: string;
  candidateName?: string;
}

export default function DownloadReportBtn({
  analysisId,
  candidateName = "Resume",
}: DownloadReportBtnProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleDownload() {
    setLoading(true);
    setError(null);
    try {
      const blob = await downloadReport(analysisId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ResumeAI_${candidateName.replace(/\s+/g, "_")}_Report.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setError("Download failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-start gap-1">
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.97 }}
        onClick={handleDownload}
        disabled={loading}
        className="inline-flex items-center gap-2.5 rounded-xl bg-accent px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-accent/20 transition-all hover:bg-accent-hover disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {loading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Download className="h-4 w-4" />
        )}
        {loading ? "Generating PDF…" : "Download Full Report"}
      </motion.button>
      {error && (
        <p className="text-xs text-danger mt-1">{error}</p>
      )}
    </div>
  );
}
