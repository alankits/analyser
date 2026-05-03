"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { BarChart3, FileText, Briefcase, Map, AlertTriangle, Loader2 } from "lucide-react";
import axios from "axios";
import ATSScoreCard from "@/components/ATSScoreCard";
import ResumeDiffView from "@/components/ResumeDiffView";
import CareerRoleCard from "@/components/CareerRoleCard";
import RoadmapPhase from "@/components/RoadmapPhase";
import DownloadReportBtn from "@/components/DownloadReportBtn";
import type { AnalysisData } from "@/lib/types";

const TABS = [
  { id: "ats", label: "ATS Score", icon: BarChart3 },
  { id: "fixes", label: "Resume Fixes", icon: FileText },
  { id: "careers", label: "Career Matches", icon: Briefcase },
  { id: "roadmap", label: "Roadmap", icon: Map },
] as const;

type TabId = (typeof TABS)[number]["id"];

function SkeletonBlock({ className = "" }: { className?: string }) {
  return (
    <div className={`animate-pulse rounded-2xl bg-card/80 ${className}`} />
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <SkeletonBlock className="h-64" />
      <SkeletonBlock className="h-40" />
      <SkeletonBlock className="h-48" />
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center gap-4 rounded-2xl border border-danger/20 bg-danger/5 p-10 text-center">
      <AlertTriangle className="h-10 w-10 text-danger" />
      <h2 className="text-lg font-semibold text-primary">Analysis Unavailable</h2>
      <p className="text-sm text-secondary max-w-md">{message}</p>
    </div>
  );
}

async function fetchAnalysisFromRoute(id: string): Promise<AnalysisData> {
  const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const res = await axios.get(`${BASE}/api/v1/analysis/${id}`);
  if (!res.data.success) {
    throw new Error(res.data.error || "Failed to load analysis");
  }
  return res.data.data as AnalysisData;
}

export default function ResultsPage() {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<TabId>("ats");

  const { data, isLoading, error } = useQuery<AnalysisData, Error>({
    queryKey: ["analysis", id],
    queryFn: () => fetchAnalysisFromRoute(id),
    retry: 1,
    staleTime: Infinity,
  });

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">
            {data?.candidate_name ?? "Resume Analysis"}
          </h1>
          {data && (
            <p className="mt-1 text-sm text-secondary">
              Analysis ID: <code className="text-accent text-xs">{data.analysis_id}</code>
            </p>
          )}
        </div>
        {data && (
          <DownloadReportBtn
            analysisId={data.analysis_id}
            candidateName={data.candidate_name}
          />
        )}
      </div>

      {/* Tab navigation */}
      <div className="mb-8 flex overflow-x-auto gap-1 rounded-xl border border-white/[0.08] bg-card p-1">
        {TABS.map(({ id: tabId, label, icon: Icon }) => (
          <button
            key={tabId}
            onClick={() => setActiveTab(tabId)}
            className={`relative flex flex-1 min-w-max items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-all ${
              activeTab === tabId
                ? "bg-accent text-white shadow-lg shadow-accent/20"
                : "text-secondary hover:text-primary"
            }`}
          >
            <Icon className="h-4 w-4" />
            <span className="hidden sm:inline">{label}</span>
          </button>
        ))}
      </div>

      {/* Content */}
      {isLoading ? (
        <LoadingSkeleton />
      ) : error ? (
        <ErrorState
          message={
            error.message ||
            "Could not load this analysis. The API may be unavailable."
          }
        />
      ) : data ? (
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === "ats" && <ATSScoreCard data={data.ats_result} />}
          {activeTab === "fixes" && <ResumeDiffView fixes={data.resume_fixes} />}
          {activeTab === "careers" && (
            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {data.career_matches.map((role, i) => (
                <CareerRoleCard key={role.role_title} role={role} index={i} />
              ))}
            </div>
          )}
          {activeTab === "roadmap" && <RoadmapPhase roadmap={data.roadmap} />}
        </motion.div>
      ) : null}
    </div>
  );
}
