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
  Sparkles,
  LogOut,
} from "lucide-react";
import { GithubIcon } from "@/components/icons/GithubIcon";
import { useAuth } from "@/components/auth/AuthProvider";
import { GITHUB_LOGIN_URL } from "@/lib/api";

export default function Navbar() {
  const pathname = usePathname();
  const { user, loading, logout } = useAuth();

  const navItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Repositories", href: "/repositories", icon: Code2 },
    { name: "Career & Jobs", href: "/career", icon: Briefcase },
    { name: "Roadmap", href: "/roadmap", icon: Map },
    { name: "Assistant", href: "/chat", icon: MessageSquareCode },
  ];

  const displayName = user?.name || user?.github_username || "Developer";

  return (
    <header className="sticky top-0 z-50 border-b border-gray-800 bg-[#0d1117]/95 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/20 group-hover:scale-105 transition-transform">
            <GitBranch className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-1.5 font-bold text-lg text-white">
              GitVia <Sparkles className="h-3.5 w-3.5 text-cyan-400 fill-cyan-400" />
            </div>
            <span className="text-[10px] text-gray-400 tracking-wide uppercase font-semibold">
              Career Copilot
            </span>
          </div>
        </Link>

        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname.startsWith(item.href));

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

        <div className="flex items-center gap-3">
          {loading ? (
            <div className="h-8 w-28 animate-pulse rounded-full bg-gray-800" />
          ) : user ? (
            <>
              <div className="hidden sm:flex items-center gap-2.5 rounded-full border border-gray-700 bg-gray-900/80 px-3 py-1 text-xs">
                <div className="h-2 w-2 rounded-full bg-emerald-400" />
                <span className="text-gray-300 font-medium">{displayName}</span>
              </div>
              <button
                type="button"
                onClick={() => logout()}
                className="flex items-center gap-2 rounded-lg border border-gray-700 bg-gray-900 px-3.5 py-2 text-xs font-semibold text-white hover:border-gray-600"
              >
                <LogOut className="h-4 w-4" />
                <span>Log out</span>
              </button>
            </>
          ) : (
            <a
              href={GITHUB_LOGIN_URL}
              className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 px-3.5 py-2 text-xs font-semibold text-white"
            >
              <GithubIcon className="h-4 w-4" />
              <span>Connect GitHub</span>
            </a>
          )}
        </div>
      </div>
    </header>
  );
}
