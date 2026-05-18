"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useRouter } from "next/navigation";
import {
  BarChart3,
  BrainCircuit,
  LogOut,
  MessageCircle,
  ShieldCheck
} from "lucide-react";

import { useAuth } from "@/components/providers/auth-provider";
import { sidebarItems } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

const iconMap = {
  "/dashboard": BarChart3,
  "/chat": MessageCircle,
  "/insights": BrainCircuit
} as const;

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { signOut } = useAuth();

  return (
    <aside className="flex h-full flex-col rounded-[2rem] border border-white/60 bg-white/75 p-5 shadow-panel backdrop-blur-xl dark:border-sage-800/70 dark:bg-sage-950/70">
      <div className="mb-8 flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-sage-500 to-sage-700 text-white shadow-soft">
          <ShieldCheck className="h-6 w-6" />
        </div>
        <div>
          <p className="font-serif-display text-2xl text-ink dark:text-sand-50">Safebond</p>
          <p className="text-xs uppercase tracking-[0.22em] text-sage-700/70 dark:text-sand-100/55">
            Emotion-Aware Care
          </p>
        </div>
      </div>

      <nav className="space-y-2">
        {sidebarItems.map((item) => {
          const Icon = iconMap[item.href];
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition",
                active
                  ? "bg-sage-800 text-white shadow-soft dark:bg-sand-100 dark:text-sage-950"
                  : "text-sage-900/78 hover:bg-sage-50 dark:text-sand-50/82 dark:hover:bg-sage-900/80"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="mt-8 rounded-3xl bg-gradient-to-br from-sand-100 via-white to-mist p-5 dark:from-sage-900 dark:via-sage-950 dark:to-sage-900/80">
        <p className="text-xs uppercase tracking-[0.24em] text-sage-700/65 dark:text-sand-100/50">
          Safety Layer
        </p>
        <p className="mt-3 text-sm leading-6 text-sage-900/82 dark:text-sand-50/82">
          High-risk conversations are intercepted, escalated, and grounded in verified support pathways.
        </p>
      </div>

      <button
        className="mt-auto flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium text-sage-700 transition hover:bg-white/80 dark:text-sand-50/72 dark:hover:bg-sage-900/80"
        onClick={() => {
          signOut();
          router.push("/login");
        }}
      >
        <LogOut className="h-4 w-4" />
        Sign out
      </button>
    </aside>
  );
}
