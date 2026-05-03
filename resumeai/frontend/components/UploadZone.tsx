"use client";

import { useCallback, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { UploadCloud, FileText, FileType2, X, AlertCircle } from "lucide-react";
import { useDropzone } from "react-dropzone";

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  isProcessing?: boolean;
  error?: string | null;
}

const ACCEPTED_TYPES: Record<string, string[]> = {
  "application/pdf": [".pdf"],
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
};

function FileIcon({ type }: { type: string }) {
  if (type === "application/pdf") {
    return <FileType2 className="h-10 w-10 text-danger" />;
  }
  return <FileText className="h-10 w-10 text-accent" />;
}

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function UploadZone({
  onFileSelect,
  selectedFile,
  isProcessing = false,
  error,
}: UploadZoneProps) {
  const [rejectionError, setRejectionError] = useState<string | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[], fileRejections: any[]) => {
      setRejectionError(null);
      if (fileRejections.length > 0) {
        const errCode = fileRejections[0]?.errors?.[0]?.code;
        if (errCode === "file-too-large") {
          setRejectionError("File exceeds 5 MB limit. Please use a smaller file.");
        } else if (errCode === "file-invalid-type") {
          setRejectionError("Only PDF and DOCX files are accepted.");
        } else {
          setRejectionError("Invalid file. Please upload a PDF or DOCX.");
        }
        return;
      }
      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024,
    disabled: isProcessing,
  });

  const displayError = error || rejectionError;

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          relative cursor-pointer rounded-2xl border-2 border-dashed p-8 transition-all duration-300
          ${isDragActive
            ? "border-accent bg-accent/10 scale-[1.01]"
            : selectedFile
            ? "border-success/50 bg-success/5"
            : "border-white/10 bg-card hover:border-accent/40 hover:bg-card-hover"
          }
          ${isProcessing ? "cursor-not-allowed opacity-60" : ""}
        `}
      >
        <input {...getInputProps()} />

        {/* Shimmer overlay when processing */}
        {isProcessing && (
          <div className="absolute inset-0 overflow-hidden rounded-2xl">
            <div className="shimmer absolute inset-0" />
          </div>
        )}

        <AnimatePresence mode="wait">
          {selectedFile ? (
            <motion.div
              key="selected"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="flex flex-col items-center gap-3 text-center"
            >
              <FileIcon type={selectedFile.type} />
              <div>
                <p className="font-semibold text-primary">{selectedFile.name}</p>
                <p className="text-sm text-secondary">{formatBytes(selectedFile.size)}</p>
              </div>
              {!isProcessing && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setRejectionError(null);
                    onFileSelect(null as unknown as File);
                  }}
                  className="mt-1 flex items-center gap-1 rounded-full border border-white/10 px-3 py-1 text-xs text-secondary hover:text-primary hover:border-white/20 transition-all"
                >
                  <X className="h-3 w-3" /> Remove
                </button>
              )}
              {isProcessing && (
                <p className="text-sm text-accent animate-pulse">Analysing your resume…</p>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="flex flex-col items-center gap-4 text-center"
            >
              <motion.div
                animate={isDragActive ? { scale: 1.15, rotate: 5 } : { scale: 1, rotate: 0 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <UploadCloud
                  className={`h-12 w-12 transition-colors ${
                    isDragActive ? "text-accent" : "text-secondary"
                  }`}
                />
              </motion.div>
              <div>
                <p className="font-semibold text-primary">
                  {isDragActive ? "Drop your resume here" : "Drag & drop your resume"}
                </p>
                <p className="mt-1 text-sm text-secondary">
                  PDF or DOCX · Max 5 MB · or{" "}
                  <span className="text-accent">click to browse</span>
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <AnimatePresence>
        {displayError && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-2 flex items-center gap-2 text-sm text-danger"
          >
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            {displayError}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
