// All TypeScript interfaces matching backend Pydantic schemas exactly

export interface KeywordItem {
  keyword: string;
  present: boolean;
  importance: "high" | "medium" | "low";
}

export interface SectionScores {
  summary: number;
  experience: number;
  skills: number;
  education: number;
  projects: number;
}

export interface ATSResult {
  overall_score: number;
  grade: string;
  keyword_analysis: KeywordItem[];
  section_scores: SectionScores;
  missing_sections: string[];
  top_issues: string[];
}

export interface FixItem {
  original: string;
  rewritten: string;
  reason: string;
}

export interface ResumeSectionFix {
  section_name: string;
  issues: string[];
  fixes: FixItem[];
  missing_elements: string[];
}

export interface CareerRole {
  role_title: string;
  match_score: number;
  match_reasons: string[];
  skill_gaps: string[];
  time_to_ready: string;
  recommended_project: string;
  seniority_target: string;
}

export interface SkillItem {
  skill_name: string;
  why_it_matters: string;
  resource_type: string;
  estimated_hours: number;
}

export interface RoadmapPhaseData {
  phase_number: number;
  duration: string;
  goal: string;
  skills: SkillItem[];
  milestone: string;
}

export interface Roadmap {
  target_role: string;
  current_level: string;
  phases: RoadmapPhaseData[];
  total_estimated_hours: number;
}

export interface AnalysisData {
  analysis_id: string;
  candidate_name: string;
  ats_result: ATSResult;
  resume_fixes: ResumeSectionFix[];
  career_matches: CareerRole[];
  roadmap: Roadmap;
  created_at: string;
}

export interface AnalysisResponse {
  success: boolean;
  data: AnalysisData | null;
  error: string | null;
}

export interface AnalyzeFormValues {
  file: File;
  target_role: string;
  job_description: string;
}
