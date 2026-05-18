"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { EmotionHeatmap } from "@/components/dashboard/emotion-heatmap";
import { EmotionDistributionChart } from "@/components/dashboard/emotion-distribution-chart";
import { MoodTrendChart } from "@/components/dashboard/mood-trend-chart";
import { RiskTimelineChart } from "@/components/dashboard/risk-timeline-chart";
import { SessionActivityChart } from "@/components/dashboard/session-activity-chart";
import { useAuth } from "@/components/providers/auth-provider";
import { FadeIn } from "@/components/motion/fade-in";
import { Card } from "@/components/ui/card";
import { SectionHeading } from "@/components/ui/section-heading";
import { ApiError, api } from "@/lib/api";
import type { InsightsAnalytics } from "@/lib/types";

export function InsightsClient() {
  const router = useRouter();
  const { token, signOut } = useAuth();
  const [data, setData] = useState<InsightsAnalytics | null>(null);
  const loadedTokenRef = useRef<string | null>(null);

  useEffect(() => {
    if (!token || loadedTokenRef.current === token) {
      return;
    }
    loadedTokenRef.current = token;
    api.insights(token)
      .then(setData)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401) {
          signOut();
          router.replace("/login");
          return;
        }
        setData(null);
      });
  }, [router, signOut, token]);

  if (!data) {
    return <Card className="p-6 text-sm text-sage-800">Loading insights...</Card>;
  }

  return (
    <main className="space-y-4">
      <FadeIn>
        <Card className="p-6">
          <SectionHeading
            eyebrow="Mood Intelligence"
            title="Longitudinal emotional analytics"
            description="Backend-generated insight summaries, stress heatmaps, and mood trajectories."
          />
        </Card>
      </FadeIn>

      <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <FadeIn delay={0.1}>
          <Card className="p-6">
            <SectionHeading
              eyebrow="Trendline"
              title="Weekly pattern shifts"
              description="Real dashboard series from backend analytics."
            />
            <div className="mt-6">
              <MoodTrendChart data={data.trend} />
            </div>
          </Card>
        </FadeIn>
        <FadeIn delay={0.16}>
          <Card className="p-6">
            <SectionHeading
              eyebrow="Emotion Share"
              title="Distribution across emotion classes"
              description="A class-level snapshot of the dominant emotional mix across the active analysis window."
            />
            <div className="mt-6">
              <EmotionDistributionChart data={data.emotion_distribution} />
            </div>
          </Card>
        </FadeIn>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.05fr_0.95fr]">
        <FadeIn delay={0.22}>
          <Card className="p-6">
            <SectionHeading
              eyebrow="Risk and Escalation"
              title="How safety pressure is moving over time"
              description="This view tracks average risk, elevated messages, and higher-alert safety events."
            />
            <div className="mt-6">
              <RiskTimelineChart data={data.risk_trend} />
            </div>
          </Card>
        </FadeIn>
        <FadeIn delay={0.28}>
          <Card className="p-6">
            <SectionHeading
              eyebrow="Session Activity"
              title="Reflection depth and cadence"
              description="Message volume and reflection depth show whether sessions are becoming more expressive or more compressed."
            />
            <div className="mt-6">
              <SessionActivityChart data={data.session_activity} />
            </div>
          </Card>
        </FadeIn>
      </section>

      <section className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
        <FadeIn delay={0.34}>
          <Card className="p-6">
            <SectionHeading
              eyebrow="Heatmap"
              title="Intensity pockets"
              description="Backend-derived intensity categories grouped into a compact weekly grid."
            />
            <div className="mt-6">
              <EmotionHeatmap rows={data.heatmap.map((row) => row.map((cell) => cell.value))} />
            </div>
          </Card>
        </FadeIn>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {data.summaries.map((summary, index) => (
          <FadeIn key={summary.title} delay={0.4 + index * 0.06}>
            <Card className="p-6">
              <h3 className="font-serif-display text-2xl text-ink">{summary.title}</h3>
              <p className="mt-3 text-sm leading-7 text-sage-800/76">{summary.body}</p>
            </Card>
          </FadeIn>
        ))}
      </section>
    </main>
  );
}
