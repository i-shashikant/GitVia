"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, CheckCircle2 } from "lucide-react";

export default function AuthSuccess() {
  const router = useRouter();

  useEffect(() => {
    const timer = setTimeout(() => {
      router.push("/dashboard");
    }, 1200);
    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="flex flex-col items-center justify-center py-20 text-center space-y-6">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-950 border border-emerald-500/30 text-emerald-400 animate-bounce">
        <CheckCircle2 className="h-8 w-8" />
      </div>
      <div className="space-y-2">
        <h1 className="text-2xl font-bold text-white">GitHub OAuth Connected!</h1>
        <p className="text-gray-400 text-sm">Analyzing repositories, languages, and code quality engine...</p>
      </div>
    </div>
  );
}