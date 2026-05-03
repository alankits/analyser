import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Providers from "./providers";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "ResumeAI — AI-Powered Resume Analysis",
  description:
    "Upload your resume and receive an ATS score, section-by-section rewrite suggestions, career role matches, and a personalised learning roadmap — powered by AI.",
  keywords: ["resume analyzer", "ATS score", "AI resume", "career advice", "resume builder"],
  openGraph: {
    title: "ResumeAI — AI-Powered Resume Analysis",
    description: "Get your ATS score, resume fixes, career matches, and a learning roadmap in seconds.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} dark`}>
      <body className="bg-base font-sans text-primary antialiased">
        <Providers>
          <Navbar />
          <main className="min-h-screen pt-16">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
