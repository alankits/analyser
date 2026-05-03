import axios from "axios";
import type { AnalysisResponse } from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 180_000, // 3 minutes — LLM calls can be slow
});

/**
 * POST /analyze
 * Upload a resume file with optional target role and job description.
 */
export async function analyzeResume(
  file: File,
  targetRole: string,
  jobDescription: string,
  onUploadProgress?: (pct: number) => void
): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("target_role", targetRole);
  formData.append("job_description", jobDescription);

  const response = await apiClient.post<AnalysisResponse>("/analyze", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (progressEvent) => {
      if (onUploadProgress && progressEvent.total) {
        const pct = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onUploadProgress(pct);
      }
    },
  });

  return response.data;
}

/**
 * GET /report/{id}
 * Download the PDF report for a completed analysis.
 */
export async function downloadReport(analysisId: string): Promise<Blob> {
  const response = await apiClient.get(`/report/${analysisId}`, {
    responseType: "blob",
  });
  return response.data;
}
