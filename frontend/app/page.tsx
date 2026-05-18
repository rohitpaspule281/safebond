import Link from "next/link";
import {
  ArrowRight,
  BrainCircuit,
  ClipboardList,
  ShieldCheck,
  Sparkles,
  Waves
} from "lucide-react";

import { FadeIn } from "@/components/motion/fade-in";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { SectionHeading } from "@/components/ui/section-heading";

const pillars = [
  {
    icon: ClipboardList,
    title: "10-question intake",
    body: "Every user begins with a structured psychological check-in so Safebond can infer distress, pressure, withdrawal, and support needs before the first live response."
  },
  {
    icon: BrainCircuit,
    title: "Emotion intelligence",
    body: "Transformer-based affect analysis tuned for stress, anxiety, loneliness, burnout, and recovery patterns."
  },
  {
    icon: Waves,
    title: "Contextual memory",
    body: "Longitudinal conversation memory and semantic recall bring continuity into every supportive exchange."
  },
  {
    icon: ShieldCheck,
    title: "Safety-first orchestration",
    body: "Risk-aware routing, escalation policies, and moderated responses keep the experience ethically bounded."
  }
] as const;

const intakePreview = [
  "How often have you felt emotionally overwhelmed by daily life recently?",
  "How difficult has it been to calm your mind enough to rest or sleep well?",
  "How often have you pulled away from people who usually feel safe or supportive?",
  "How hard has it been to imagine things improving in the near future?",
  "When distress spikes, how hard is it to stay grounded, regulated, and safe?"
] as const;

export default function HomePage() {
  return (
    <main className="relative overflow-hidden px-5 py-6 sm:px-8 lg:px-12">
      <div className="mx-auto max-w-7xl">
        <FadeIn className="rounded-[2rem] border border-white/60 bg-white/70 px-6 py-4 shadow-soft backdrop-blur-xl sm:px-8">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-sage-700/75">
                Safebond
              </p>
              <h1 className="mt-2 font-serif-display text-3xl text-ink sm:text-5xl">
                Emotion-aware AI support for mental wellness.
              </h1>
            </div>
            <div className="flex gap-3">
              <Link href="/login">
                <Button variant="secondary">Sign in</Button>
              </Link>
              <Link href="/signup">
                <Button>
                  Start intake
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </FadeIn>

        <section className="grid gap-10 py-12 lg:grid-cols-[1.2fr_0.8fr] lg:py-16">
          <FadeIn delay={0.1} className="space-y-8">
            <SectionHeading
              eyebrow="Wellness Intelligence Platform"
              title="A mental wellness platform that begins by understanding the user before the first chat."
              description="Safebond starts with a structured 10-question psychological intake, builds a safer support profile, records a trusted contact, and only then opens the AI conversation layer."
            />
            <div className="flex flex-wrap gap-3">
              <Link href="/signup">
                <Button className="bg-sage-700 hover:bg-sage-800">
                  Create account and begin intake
                </Button>
              </Link>
              <Link href="/onboarding">
                <Button variant="secondary">Preview the 10-question flow</Button>
              </Link>
            </div>
          </FadeIn>

          <FadeIn delay={0.2}>
            <Card className="relative overflow-hidden bg-wellness-radial p-7">
              <div className="absolute right-6 top-6 rounded-full bg-white/80 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-sage-800">
                Orchestrated AI
              </div>
              <div className="space-y-6">
                <div className="inline-flex items-center gap-2 rounded-full bg-white/80 px-4 py-2 text-sm text-sage-900 shadow-soft">
                  <Sparkles className="h-4 w-4 text-coral-500" />
                  Research-grade mental wellness assistant
                </div>
                <div className="grid gap-4">
                  <div className="rounded-[1.75rem] bg-white/80 p-5 shadow-soft">
                    <p className="text-xs uppercase tracking-[0.2em] text-sage-700/70">
                      Live System Signals
                    </p>
                    <div className="mt-4 grid grid-cols-3 gap-3">
                      <div className="rounded-2xl bg-sage-50 p-4">
                        <p className="text-xs text-sage-700/70">Emotion</p>
                        <p className="mt-2 font-serif-display text-3xl text-ink">Anxiety</p>
                      </div>
                      <div className="rounded-2xl bg-sand-50 p-4">
                        <p className="text-xs text-sage-700/70">Memory recall</p>
                        <p className="mt-2 font-serif-display text-3xl text-ink">0.91</p>
                      </div>
                      <div className="rounded-2xl bg-coral-50 p-4">
                        <p className="text-xs text-sage-700/70">Safety</p>
                        <p className="mt-2 font-serif-display text-3xl text-ink">Low</p>
                      </div>
                    </div>
                  </div>
                  <div className="rounded-[1.75rem] border border-sage-100 bg-gradient-to-br from-sky-50 via-white to-sand-50 p-5 shadow-soft">
                    <p className="text-xs uppercase tracking-[0.22em] text-sage-700/70">
                      Intake Before Chat
                    </p>
                    <div className="mt-4 space-y-3">
                      <div className="flex items-center justify-between rounded-2xl bg-white/85 px-4 py-3">
                        <span className="text-sm text-sage-900/80">Psychological check-in</span>
                        <span className="font-semibold text-ink">10 questions</span>
                      </div>
                      <div className="flex items-center justify-between rounded-2xl bg-white/85 px-4 py-3">
                        <span className="text-sm text-sage-900/80">Risk style</span>
                        <span className="font-semibold text-ink">Inferred, not asked directly</span>
                      </div>
                      <div className="flex items-center justify-between rounded-2xl bg-white/85 px-4 py-3">
                        <span className="text-sm text-sage-900/80">Trusted contact</span>
                        <span className="font-semibold text-ink">Required in onboarding</span>
                      </div>
                    </div>
                  </div>
                  <div className="rounded-[1.75rem] bg-sage-900 p-5 text-white shadow-soft">
                    <p className="text-xs uppercase tracking-[0.22em] text-white/65">
                      Product Promise
                    </p>
                    <p className="mt-3 text-sm leading-7 text-white/82">
                      Safebond is supportive, memory-aware, and ethically bounded. It is not presented as a therapist replacement.
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          </FadeIn>
        </section>

        <section className="grid gap-5 pb-12 md:grid-cols-3">
          {pillars.map((pillar, index) => (
            <FadeIn key={pillar.title} delay={0.15 + index * 0.08}>
              <Card className="h-full p-6">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-sage-100 text-sage-800">
                  <pillar.icon className="h-5 w-5" />
                </div>
                <h3 className="mt-6 font-serif-display text-2xl text-ink">
                  {pillar.title}
                </h3>
                <p className="mt-3 text-sm leading-7 text-sage-800/76">
                  {pillar.body}
                </p>
              </Card>
            </FadeIn>
          ))}
        </section>

        <section className="grid gap-8 pb-14 pt-2 lg:grid-cols-[0.95fr_1.05fr]">
          <FadeIn delay={0.26}>
            <Card className="h-full overflow-hidden bg-gradient-to-br from-sage-900 via-sage-800 to-emerald-900 p-7 text-white">
              <p className="text-xs uppercase tracking-[0.24em] text-white/60">
                Why The Questions Matter
              </p>
              <h2 className="mt-4 font-serif-display text-3xl">
                The opening questionnaire is part of the AI pipeline, not just formality.
              </h2>
              <div className="mt-6 space-y-4 text-sm leading-7 text-white/80">
                <p>
                  Safebond does not jump from sign-up to chat. It first gathers structured signals
                  about overwhelm, sleep disruption, hopelessness, panic, isolation, self-worth,
                  and regulation difficulty.
                </p>
                <p>
                  Those answers are analyzed into an inferred support profile, then used to shape
                  safety posture, conversational tone, emotional baselines, and future analytics.
                </p>
              </div>
            </Card>
          </FadeIn>

          <FadeIn delay={0.34}>
            <Card className="p-7 dark:border-sage-600/70 dark:bg-[#1d2827]">
              <p className="text-xs uppercase tracking-[0.24em] text-sage-700/72 dark:text-sand-50/86">
                Beginning Experience
              </p>
              <h2 className="mt-4 font-serif-display text-3xl text-ink dark:text-sand-50">
                The first five questions a user sees
              </h2>
              <div className="mt-6 grid gap-3">
                {intakePreview.map((question, index) => (
                  <div
                    key={question}
                    className="rounded-[1.5rem] border border-sage-100 bg-sage-50/65 px-4 py-4 dark:border-sage-600/65 dark:bg-[#2a3736]"
                  >
                    <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-sage-700/58 dark:text-sand-50/88">
                      Q{index + 1}
                    </p>
                    <p className="mt-2 text-sm leading-6 text-sage-900/84 dark:text-white">
                      {question}
                    </p>
                  </div>
                ))}
              </div>
            </Card>
          </FadeIn>
        </section>
      </div>
    </main>
  );
}
