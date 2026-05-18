import { emotionPulse } from "@/lib/mock-data";

type EmotionPulseProps = {
  items?: { label: string; value: number }[];
};

const palette: Record<string, string> = {
  stress: "from-amber-600 via-orange-400 to-yellow-200",
  anxiety: "from-coral-700 via-coral-500 to-rose-200",
  loneliness: "from-sky-700 via-sky-400 to-cyan-200",
  calm: "from-emerald-700 via-sage-500 to-sand-200",
  safety: "from-violet-700 via-purple-400 to-pink-200",
  confidence: "from-indigo-700 via-blue-400 to-sky-200",
  anger: "from-fuchsia-700 via-rose-500 to-orange-200",
  burnout: "from-stone-700 via-amber-500 to-yellow-200",
  sadness: "from-slate-700 via-blue-500 to-sky-200"
};

export function EmotionPulse({ items = emotionPulse }: EmotionPulseProps) {
  return (
    <div className="space-y-4">
      {items.map((item) => (
        <div key={item.label} className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-sage-900/80">{item.label}</span>
            <span className="font-semibold text-ink">{item.value}%</span>
          </div>
          <div className="h-3 rounded-full bg-sage-100">
            <div
              className={`h-3 rounded-full bg-gradient-to-r ${
                palette[item.label.toLowerCase()] ?? "from-sage-600 via-sage-400 to-sand-300"
              }`}
              style={{ width: `${item.value}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
