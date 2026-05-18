import { Bell, Search, Sparkles } from "lucide-react";

import { ThemeToggle } from "@/components/layout/theme-toggle";

export function Topbar() {
  return (
    <header className="flex flex-col gap-4 rounded-[2rem] border border-white/60 bg-white/75 px-5 py-4 shadow-soft backdrop-blur-xl dark:border-sage-700/70 dark:bg-[#182323]/92 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p className="text-xs uppercase tracking-[0.24em] text-sage-700/70 dark:text-sand-50/72">
          Research Workspace
        </p>
        <h1 className="mt-1 font-serif-display text-2xl text-ink dark:text-sand-50">
          Emotion-aware support intelligence
        </h1>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 rounded-full border border-sage-200 bg-sage-50/70 px-4 py-2 text-sm text-sage-800 dark:border-sage-700 dark:bg-sage-900/90 dark:text-sand-50">
          <Search className="h-4 w-4" />
          Search memories, trends, or sessions
        </div>
        <ThemeToggle />
        <button className="flex h-11 w-11 items-center justify-center rounded-full border border-white/70 bg-white/85 text-sage-800 shadow-soft dark:border-sage-700 dark:bg-sage-900/90 dark:text-sand-50">
          <Bell className="h-4 w-4" />
        </button>
        <div className="flex items-center gap-2 rounded-full bg-sage-800 px-4 py-2 text-sm text-white shadow-soft dark:bg-sand-100 dark:text-sage-950">
          <Sparkles className="h-4 w-4" />
          AI orchestration live
        </div>
      </div>
    </header>
  );
}
