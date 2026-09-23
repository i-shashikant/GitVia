"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  GitBranch, 
  LayoutDashboard, 
  Code2, 
  Briefcase, 
  Map, 
  MessageSquareCode, 
  Sparkles
} from "lucide-react";
import { GithubIcon } from "@/components/icons/GithubIcon";

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Repositories", href: "/repositories", icon: Code2 },
    { name: "Career & Jobs", href: "/career", icon: Briefcase },
    { name: "Roadmap", href: "/roadmap", icon: Map },
    { name: "AI Assistant", href: "/chat", icon: MessageSquareCode },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-gray-800 bg-[#0d1117]/95 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Brand */}
        <Link href="/dashboard" className="flex items-center gap-3 group">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/20 group-hover:scale-105 transition-transform">
            <GitBranch className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-1.5 font-bold text-lg text-white">
              GitVia <Sparkles className="h-3.5 w-3.5 text-cyan-400 fill-cyan-400" />
            </div>
            <span className="text-[10px] text-gray-400 tracking-wide uppercase font-semibold">AI Career Copilot</span>
          </div>
        </Link>

        {/* Nav Links */}
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 rounded-lg px-3.5 py-2 text-sm font-medium transition-all ${
                  isActive
                    ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm shadow-cyan-500/10"
                    : "text-gray-300 hover:bg-gray-800/60 hover:text-white"
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? "text-cyan-400" : "text-gray-400"}`} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* User / Connect Button */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2.5 rounded-full border border-gray-700 bg-gray-900/80 px-3 py-1 text-xs">
            <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-gray-300 font-medium">Shashikant</span>
            <span className="rounded bg-cyan-950 px-1.5 py-0.5 text-[10px] font-semibold text-cyan-300 border border-cyan-800">PRO</span>
          </div>
          <Link
            href="/auth/success"
            className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-gray-800 to-gray-900 px-3.5 py-2 text-xs font-semibold text-white border border-gray-700 hover:border-gray-600 transition-all shadow-sm"
          >
            <GithubIcon className="h-4 w-4" />
            <span>Connected</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
