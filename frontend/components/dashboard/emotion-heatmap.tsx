import { stressHeatmap } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

const intensityClass: Record<(typeof stressHeatmap)[number][number], string> = {
  Low: "bg-sage-100 text-sage-800",
  Moderate: "bg-sand-200 text-sand-900",
  High: "bg-coral-200 text-coral-900"
};

type EmotionHeatmapRowsProps = {
  rows?: readonly (readonly string[])[];
};

export function EmotionHeatmapRows({ rows }: EmotionHeatmapRowsProps) {
  const resolvedRows = rows ?? stressHeatmap;

  return (
    <div className="grid gap-3">
      {resolvedRows.map((row, rowIndex) => (
        <div key={rowIndex} className="grid grid-cols-7 gap-3">
          {row.map((cell, cellIndex) => (
            <div
              key={`${rowIndex}-${cellIndex}`}
              className={cn(
                "flex aspect-square items-center justify-center rounded-2xl text-[11px] font-semibold",
                intensityClass[cell as keyof typeof intensityClass]
              )}
            >
              {cell}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

export function EmotionHeatmap(props: EmotionHeatmapRowsProps) {
  return <EmotionHeatmapRows {...props} />;
}
