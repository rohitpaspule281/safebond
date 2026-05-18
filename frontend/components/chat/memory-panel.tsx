import { recentMemories } from "@/lib/mock-data";
import type { MemoryResult } from "@/lib/types";

type MemoryPanelProps = {
  memories?: MemoryResult[];
};

export function MemoryPanel({ memories }: MemoryPanelProps) {
  if (memories && memories.length === 0) {
    return (
      <div className="rounded-[1.75rem] border border-dashed border-sage-200 bg-sage-50/45 p-5 text-sm leading-6 text-sage-800/75 dark:border-sage-700/70 dark:bg-sage-900/72 dark:text-sand-50/84">
        Safebond has not retrieved any strong memory matches yet. After a few exchanges, this panel
        will surface the most relevant prior reflections.
      </div>
    );
  }

  const items =
    memories && memories.length > 0
      ? memories.map((memory) => ({
          title: memory.content.slice(0, 42),
          detail: memory.created_at
            ? `Retrieved ${new Date(memory.created_at).toLocaleString()}`
            : "Retrieved from conversational memory",
          score: memory.final_score.toFixed(2),
          tag: memory.role
        }))
      : recentMemories;

  return (
    <div className="space-y-4">
      {items.map((memory) => (
        <div
          key={memory.title}
          className="rounded-[1.75rem] border border-white/70 bg-white/80 p-4 shadow-soft dark:border-sage-700/70 dark:bg-[#182323]/90"
        >
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="font-semibold text-ink dark:text-sand-50">{memory.title}</p>
              <p className="mt-1 text-sm text-sage-800/72 dark:text-sand-50/80">{memory.detail}</p>
            </div>
            <span className="rounded-full bg-sage-100 px-3 py-1 text-xs font-semibold text-sage-800 dark:bg-sage-900 dark:text-sand-50">
              {memory.score}
            </span>
          </div>
          <div className="mt-4 inline-flex rounded-full bg-sand-100 px-3 py-1 text-xs font-semibold text-sand-900 dark:bg-sand-900 dark:text-sand-50">
            {memory.tag}
          </div>
        </div>
      ))}
    </div>
  );
}
