import { ArrowUpRight } from "lucide-react";

import { Card } from "@/components/ui/card";

type AnalyticsCardProps = {
  title: string;
  value: string;
  trend: string;
  detail: string;
  accent: string;
};

export function AnalyticsCard({
  title,
  value,
  trend,
  detail,
  accent
}: AnalyticsCardProps) {
  return (
    <Card className={`overflow-hidden bg-gradient-to-br ${accent} p-6`}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-sage-900/70">{title}</p>
          <p className="mt-4 font-serif-display text-4xl text-ink">{value}</p>
        </div>
        <div className="rounded-full bg-white/70 p-2 text-sage-800">
          <ArrowUpRight className="h-4 w-4" />
        </div>
      </div>
      <div className="mt-8 space-y-1">
        <p className="text-sm font-semibold text-sage-900">{trend}</p>
        <p className="text-sm leading-6 text-sage-800/76">{detail}</p>
      </div>
    </Card>
  );
}
