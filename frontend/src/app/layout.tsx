import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";

export const metadata: Metadata = {
  title: "GitVia - AI Career Intelligence Platform",
  description: "From what you build to where you go next. AI career intelligence analyzing GitHub, resumes, and job descriptions.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-[#0b0f19] text-gray-100 min-h-screen selection:bg-cyan-500 selection:text-black">
        <Navbar />
        <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
          {children}
        </main>
      </body>
    </html>
  );
}