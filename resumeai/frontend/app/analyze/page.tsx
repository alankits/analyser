"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { Sparkles, Loader2, AlertCircle } from "lucide-react";
import UploadZone from "@/components/UploadZone";
import { analyzeResume } from "@/lib/api";

const schema = z.object({
  target_role: z.string().max(120, "Max 120 characters").optional(),
  job_description: z.string().max(5000, "Max 5000 characters").optional(),
});

type FormValues = z.infer<typeof schema>;

export default function AnalyzePage() {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  function handleFileSelect(file: File | null) {
    setSelectedFile(file);
    setFileError(null);
  }

  async function onSubmit(values: FormValues) {
    if (!selectedFile) {
      setFileError("Please upload your resume before submitting.");
      return;
    }
    setApiError(null);
    setIsSubmitting(true);
    setUploadProgress(0);

    try {
      const response = await analyzeResume(
        selectedFile,
        values.target_role || "",
        values.job_description || "",
        setUploadProgress
      );

      if (!response.success || !response.data) {
        throw new Error(response.error || "Analysis failed. Please try again.");
      }

      router.push(`/results/${response.data.analysis_id}`);
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        err?.message ||
        "Something went wrong. Please check your connection and try again.";
      setApiError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-10 text-center">
        <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-accent/10">
          <Sparkles className="h-6 w-6 text-accent" />
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-primary sm:text-4xl">
          Analyze Your Resume
        </h1>
        <p className="mt-3 text-secondary">
          Upload your resume and optionally add a target role or job description for a more
          tailored analysis.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* File upload */}
        <div className="rounded-2xl border border-white/[0.08] bg-card p-6">
          <label className="mb-3 block text-sm font-semibold text-primary">
            Your Resume <span className="text-danger">*</span>
          </label>
          <UploadZone
            onFileSelect={handleFileSelect}
            selectedFile={selectedFile}
            isProcessing={isSubmitting}
            error={fileError}
          />
        </div>

        {/* Target role */}
        <div className="rounded-2xl border border-white/[0.08] bg-card p-6 space-y-4">
          <div>
            <label
              htmlFor="target_role"
              className="mb-1.5 block text-sm font-semibold text-primary"
            >
              Target Role{" "}
              <span className="text-xs font-normal text-secondary">(optional)</span>
            </label>
            <input
              id="target_role"
              type="text"
              placeholder="e.g. Senior Data Engineer, Product Manager"
              {...register("target_role")}
              className="w-full rounded-xl border border-white/10 bg-base px-4 py-2.5 text-sm text-primary placeholder:text-secondary/50 focus:border-accent/50 focus:outline-none focus:ring-1 focus:ring-accent/30 transition-colors"
            />
            {errors.target_role && (
              <p className="mt-1 text-xs text-danger">{errors.target_role.message}</p>
            )}
          </div>

          {/* Job description */}
          <div>
            <label
              htmlFor="job_description"
              className="mb-1.5 block text-sm font-semibold text-primary"
            >
              Job Description{" "}
              <span className="text-xs font-normal text-secondary">(optional — improves ATS accuracy)</span>
            </label>
            <textarea
              id="job_description"
              rows={6}
              placeholder="Paste the full job description here for keyword-level ATS matching..."
              {...register("job_description")}
              className="w-full rounded-xl border border-white/10 bg-base px-4 py-3 text-sm text-primary placeholder:text-secondary/50 focus:border-accent/50 focus:outline-none focus:ring-1 focus:ring-accent/30 transition-colors resize-none"
            />
            {errors.job_description && (
              <p className="mt-1 text-xs text-danger">{errors.job_description.message}</p>
            )}
          </div>
        </div>

        {/* API error */}
        {apiError && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-start gap-3 rounded-xl border border-danger/20 bg-danger/10 p-4"
          >
            <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-danger" />
            <p className="text-sm text-danger">{apiError}</p>
          </motion.div>
        )}

        {/* Upload progress */}
        {isSubmitting && uploadProgress > 0 && uploadProgress < 100 && (
          <div>
            <div className="flex justify-between text-xs text-secondary mb-1">
              <span>Uploading…</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/5">
              <motion.div
                className="h-full rounded-full bg-accent"
                animate={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Submit */}
        <motion.button
          type="submit"
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.98 }}
          disabled={isSubmitting}
          className="w-full inline-flex items-center justify-center gap-2.5 rounded-xl bg-accent py-4 text-base font-bold text-white shadow-xl shadow-accent/20 transition-all hover:bg-accent-hover disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Analysing with AI… this may take up to 60 seconds
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4" />
              Run Full AI Analysis
            </>
          )}
        </motion.button>
      </form>
    </div>
  );
}
