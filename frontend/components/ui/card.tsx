import { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-4xl border border-white/60 bg-white/75 shadow-panel backdrop-blur-xl dark:border-sage-800/80 dark:bg-sage-950/70 dark:shadow-[0_24px_80px_rgba(0,0,0,0.35)]",
        className
      )}
      {...props}
    />
  );
}
