import type { Metadata, Viewport } from "next";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import { AuthProvider } from "@/components/auth/AuthProvider";

export const metadata: Metadata = {
  title: {
    default: "GitVia — GitHub Career Copilot",
    template: "%s | GitVia",
  },
  description:
    "GitVia analyzes your GitHub engineering evidence, compares your profile with real job descriptions, detects skill gaps, and builds a personalized career roadmap.",
  applicationName: "GitVia",
  keywords: [
    "GitHub career copilot",
    "GitHub portfolio analyzer",
    "developer career intelligence",
    "job match",
    "skill gap analysis",
    "developer roadmap",
    "GitHub resume analysis",
    "software engineering career",
  ],
  authors: [{ name: "GitVia" }],
  creator: "GitVia",
  publisher: "GitVia",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
      "max-video-preview": -1,
    },
  },
  openGraph: {
    type: "website",
    title: "GitVia — GitHub Career Copilot",
    description:
      "Turn your GitHub evidence into a measurable career strategy, job match, and personalized roadmap.",
    siteName: "GitVia",
  },
  twitter: {
    card: "summary_large_image",
    title: "GitVia — GitHub Career Copilot",
    description:
      "Analyze your GitHub, match real jobs, find skill gaps, and build your next roadmap.",
  },
};

export const viewport: Viewport = {
  themeColor: "#0b0f19",
  colorScheme: "dark",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#0b0f19] text-gray-100 antialiased selection:bg-cyan-500 selection:text-black">
        <AuthProvider>
          <Navbar />
          <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
            {children}
          </main>
        </AuthProvider>
      </body>
    </html>
  );
}
