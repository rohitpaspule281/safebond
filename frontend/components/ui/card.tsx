import { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-4xl border border-white/60 bg-white/75 shadow-panel backdrop-blur-xl dark:border-sage-700/70 dark:bg-[#182323]/92 dark:shadow-[0_24px_80px_rgba(0,0,0,0.45)]",
        className
      )}
      {...props}
    />
  );
}
