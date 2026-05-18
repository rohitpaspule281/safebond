import { ArrowRightCircle, Compass, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

import { chatMessages } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import type { Message } from "@/lib/types";

type ChatThreadProps = {
  messages?: { id: string; role: string; text?: string; content?: string }[] | Message[];
};

function getAssistantSegmentMeta(segment: string, index: number, total: number) {
  const normalized = segment.toLowerCase();

  if (index === 0) {
    return {
      title: "✨ What I’m noticing",
      icon: Sparkles,
      wrapperClass:
        "border-sage-200/90 bg-gradient-to-br from-white via-sage-50/70 to-sand-50/60 dark:border-sage-800 dark:from-sage-950 dark:via-sage-900/90 dark:to-sage-950",
      iconClass: "bg-sage-100 text-sage-800 dark:bg-sage-800 dark:text-sand-50"
    };
  }

  if (
    normalized.includes("next step") ||
    normalized.includes("try ") ||
    normalized.includes("for tonight") ||
    normalized.includes("for the next few minutes") ||
    normalized.includes("a helpful next step")
  ) {
    return {
      title: "🧭 Try this",
      icon: Compass,
      wrapperClass:
        "border-sand-200/90 bg-gradient-to-br from-white via-sand-50/80 to-coral-50/50 dark:border-sand-800/80 dark:from-sage-950 dark:via-sand-950/40 dark:to-coral-950/20",
      iconClass: "bg-sand-100 text-sand-900 dark:bg-sand-900 dark:text-sand-50"
    };
  }

  if (segment.trim().endsWith("?") || index === total - 1) {
    return {
      title: "💬 Let’s keep going",
      icon: ArrowRightCircle,
      wrapperClass:
        "border-coral-200/90 bg-gradient-to-br from-white via-coral-50/65 to-sand-50/40 dark:border-coral-900/70 dark:from-sage-950 dark:via-coral-950/25 dark:to-sand-950/30",
      iconClass: "bg-coral-100 text-coral-700 dark:bg-coral-900/80 dark:text-coral-100"
    };
  }

  return {
    title: "🌿 Support note",
    icon: Sparkles,
    wrapperClass:
      "border-sage-200/90 bg-gradient-to-br from-white via-sage-50/60 to-white dark:border-sage-800 dark:from-sage-950 dark:via-sage-900/80 dark:to-sage-950",
    iconClass: "bg-sage-100 text-sage-800 dark:bg-sage-800 dark:text-sand-50"
  };
}

export function ChatThread({ messages = chatMessages }: ChatThreadProps) {
  if (messages.length === 0) {
    return (
      <div className="rounded-[2rem] border border-dashed border-sage-200 bg-sage-50/50 p-8 text-sm leading-7 text-sage-800/78">
        Start with one short reflection. Safebond will analyze the emotional signal, check safety,
        store memory, and reply with context-aware support.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {messages.map((message) => {
        const rawText = "content" in message ? message.content : message.text;
        const segments =
          message.role === "assistant"
            ? (rawText ?? "")
                .split(/\n\s*\n/)
                .map((segment) => segment.trim())
                .filter(Boolean)
                .slice(0, 3)
            : [];

        if (message.role === "assistant") {
          return (
            <div
              key={message.id}
              className={cn("max-w-3xl transition-opacity", message.id.startsWith("pending-") && "opacity-80")}
            >
              <div className="mb-3 flex items-center gap-3 px-2">
                <div className="rounded-full bg-sage-100 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-sage-900/72 dark:bg-sage-900 dark:text-sand-50/82">
                  Safebond
                </div>
                <div className="h-px flex-1 bg-gradient-to-r from-sage-200 via-sage-100 to-transparent dark:from-sage-800 dark:via-sage-900" />
              </div>
              <div className="space-y-3">
                {(segments.length ? segments : [rawText ?? ""]).map((segment, index, source) => {
                  const meta = getAssistantSegmentMeta(segment, index, source.length);
                  const Icon = meta.icon;

                  return (
                    <motion.div
                      key={`${message.id}-${index}`}
                      initial={{ opacity: 0, y: 20, scale: 0.98 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      transition={{
                        duration: 0.48,
                        delay: index * 0.12,
                        ease: [0.22, 1, 0.36, 1]
                      }}
                      className={cn(
                        "group relative overflow-hidden rounded-[1.55rem] border px-4 py-3 text-sm leading-6 text-sage-900 shadow-soft backdrop-blur-sm dark:text-sand-50",
                        meta.wrapperClass
                      )}
                    >
                      <div className="absolute inset-y-0 left-0 w-1 rounded-full bg-gradient-to-b from-sage-300 via-sand-300 to-coral-300 opacity-70 dark:from-sage-500 dark:via-sand-500 dark:to-coral-500" />
                      <div className="relative pl-2">
                        <div className="mb-3 flex items-center gap-3">
                          <div
                            className={cn(
                              "rounded-2xl p-2 shadow-[inset_0_1px_0_rgba(255,255,255,0.35)] dark:shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]",
                              meta.iconClass
                            )}
                          >
                            <Icon className="h-4 w-4" />
                          </div>
                          <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-sage-900/60 dark:text-sand-50/56">
                            {meta.title}
                          </p>
                        </div>
                        <div className="whitespace-pre-line text-[14px] leading-6 text-sage-950 dark:text-sand-50">
                          {segment}
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          );
        }

        return (
          <div
            key={message.id}
            className={cn(
              "ml-auto max-w-3xl rounded-[2rem] bg-sage-800 px-5 py-4 text-sm leading-7 text-white shadow-soft transition-opacity dark:bg-sand-100 dark:text-sage-950",
              message.id.startsWith("pending-") && "opacity-80"
            )}
          >
            <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.24em] opacity-70">
              You
            </p>
            <div className="whitespace-pre-line">{rawText}</div>
          </div>
        );
      })}
    </div>
  );
}
