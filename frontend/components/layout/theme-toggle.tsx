"use client";

import { MoonStar, SunMedium } from "lucide-react";

import { useTheme } from "@/components/providers/theme-provider";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="flex h-11 items-center gap-2 rounded-full border border-white/70 bg-white/85 px-4 text-sm font-semibold text-sage-800 shadow-soft transition hover:bg-white dark:border-sage-700 dark:bg-sage-900/80 dark:text-sand-50 dark:hover:bg-sage-900"
    >
      {isDark ? <SunMedium className="h-4 w-4" /> : <MoonStar className="h-4 w-4" />}
      {isDark ? "Light mode" : "Dark mode"}
    </button>
  );
}
