"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Activity, BadgeAlert, Clock3, Sparkles } from "lucide-react";

import { useAuth } from "@/components/providers/auth-provider";
import { AnalyticsCard } from "@/components/dashboard/analytics-card";
import { EmotionDistributionChart } from "@/components/dashboard/emotion-distribution-chart";
import { EmotionHeatmap } from "@/components/dashboard/emotion-heatmap";
import { MoodTrendChart } from "@/components/dashboard/mood-trend-chart";
import { RiskTimelineChart } from "@/components/dashboard/risk-timeline-chart";
import { SessionActivityChart } from "@/components/dashboard/session-activity-chart";
import { FadeIn } from "@/components/motion/fade-in";
import { Card } from "@/components/ui/card";
import { SectionHeading } from "@/components/ui/section-heading";
import { ApiError, api } from "@/lib/api";
import type { DashboardAnalytics } from "@/lib/types";

export function DashboardClient() {
  const router = useRouter();
  const { token, signOut } = useAuth();
  const [data, setData] = useState<DashboardAnalytics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const loadedTokenRef = useRef<string | null>(null);

  useEffect(() => {
    if (!token || loadedTokenRef.current === token) {
      return;
    }
    loadedTokenRef.current = token;
    api.dashboard(token)
      .then(setData)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 401) {
          signOut();
          router.replace("/login");
          return;
        }
        setError(err.message);
      });
  }, [router, signOut, token]);

  if (error) {
    return <Card className="p-6 text-sm text-coral-700">{error}</Card>;
  }

  if (!data) {
    return <Card className="p-6 text-sm text-sage-800">Loading analytics...</Card>;
  }

  return (
    <main className="space-y-4">
      <FadeIn>
        <Card className="overflow-hidden bg-wellness-radial p-7">
          <div className="grid gap-8 xl:grid-cols-[1.2fr_0.8fr]">
            <SectionHeading
              eyebrow="Weekly System Overview"
              title={`${data.hero.dominant_emotion} is currently the dominant signal.`}
              description={data.hero.weekly_summary}
            />
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-[1.75rem] bg-white/82 p-5 shadow-soft">
                <p className="text-xs uppercase tracking-[0.2em] text-sage-700/70">
                  Dominant Emotion
                </p>
                <p className="mt-4 font-serif-display text-4xl text-ink">{data.hero.dominant_emotion}</p>
              </div>
              <div className="rounded-[1.75rem] bg-sage-900 p-5 text-white shadow-soft">
                <p className="text-xs uppercase tracking-[0.2em] text-white/60">
                  Safety Status
                </p>
                <p className="mt-4 font-serif-display text-4xl">{data.hero.safety_status}</p>
              </div>
            </div>
          </div>
        </Card>
      </FadeIn>

      <section className="grid gap-4 xl:grid-cols-4">
        {data.stats.map((stat, index) => (
          <FadeIn key={stat.title} delay={0.08 + index * 0.06}>
            <AnalyticsCard {...stat} />
          </FadeIn>
        ))}
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
        <FadeIn delay={0.16}>
          <Card className="p-6">
            <SectionHeading
              eyebrow="Mood Analytics"
              title="Emotional balance over the week"
              description="Calm, stress, and loneliness are computed from recent user messages and emotional intensity."
            />
            <div className="mt-6">
              <MoodTrendChart data={data.mood_trend} />
            </div>
          </Card>
        </FadeIn>
        <FadeIn delay={0.22}>
          <Card className="p-6">
            <SectionHeading
              eyebrow="Emotion Distribution"
              title="Which emotional classes appear most often"
              description="Share-of-window distribution estimated from the transformer emotion pipeline."
            />
            <div className="mt-6">
              <EmotionDistributionChart data={data.emotion_distribution} />
            </div>
          </Card>
        </FadeIn>
      </section>

      <section className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <FadeIn delay={0.28}>
          <Card className="p-6">
            <SectionHeading
              eyebrow="Risk Timeline"
              title="Safety signals across recent reflections"
              description="Average risk score with elevated and higher-alert counts over the weekly window."
            />
            <div className="mt-6">
              <RiskTimelineChart data={data.risk_trend} />
            </div>
          </Card>
        </FadeIn>
        <FadeIn delay={0.34}>
          <Card className="p-6">
            <SectionHeading
              eyebrow="Reflection Activity"
              title="How deeply and how often the user is checking in"
              description="Message volume and reflection depth derived from message length and emotional context."
            />
            <div className="mt-6">
              <SessionActivityChart data={data.session_activity} />
            </div>
          </Card>
        </FadeIn>
      </section>

      <section className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
        <FadeIn delay={0.4}>
          <Card className="p-6">
            <SectionHeading
              eyebrow="Stress Heatmap"
              title="Temporal load signature"
              description="A compact weekly view of emotional intensity pockets."
            />
            <div className="mt-6">
              <EmotionHeatmap rows={data.heatmap.map((row) => row.map((cell) => cell.value))} />
            </div>
          </Card>
        </FadeIn>
        <FadeIn delay={0.46}>
          <Card className="p-6">
            <SectionHeading
              eyebrow="Operational Notes"
              title="Signals worth watching"
              description="Live backend analytics translated into product-facing insights."
            />
            <div className="mt-6 grid gap-4">
              {data.insights.map((item, index) => {
                const Icon = [Clock3, Activity, BadgeAlert, Sparkles][index % 4];
                return (
                  <div
                    key={item.title}
                    className="rounded-[1.5rem] border border-sage-100 bg-sage-50/55 p-4"
                  >
                    <div className="flex items-start gap-3">
                      <div className="mt-1 rounded-2xl bg-white p-2 text-sage-800 shadow-soft">
                        <Icon className="h-4 w-4" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-ink">{item.title}</h3>
                        <p className="mt-2 text-sm leading-6 text-sage-800/76">{item.body}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        </FadeIn>
      </section>
    </main>
  );
}
