"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { BookHeart, Compass, Flower2, MessageCircle, MessageSquareText, PhoneCall, ShieldAlert, ShieldCheck, Sparkles, TrendingUp } from "lucide-react";

import { ChatComposer } from "@/components/chat/chat-composer";
import { ChatThread } from "@/components/chat/chat-thread";
import { MemoryPanel } from "@/components/chat/memory-panel";
import { EmotionPulse } from "@/components/dashboard/emotion-pulse";
import { useAuth } from "@/components/providers/auth-provider";
import { FadeIn } from "@/components/motion/fade-in";
import { Card } from "@/components/ui/card";
import { SectionHeading } from "@/components/ui/section-heading";
import { api } from "@/lib/api";
import type { ChatResponse, Conversation, DashboardAnalytics, HealthResponse, Message } from "@/lib/types";

export function ChatClient() {
  const { token } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [latestResponse, setLatestResponse] = useState<ChatResponse | null>(null);
  const [dashboardAnalytics, setDashboardAnalytics] = useState<DashboardAnalytics | null>(null);
  const [runtimeHealth, setRuntimeHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [loadingConversation, setLoadingConversation] = useState(true);
  const bootstrappedTokenRef = useRef<string | null>(null);
  const sendingRef = useRef(false);

  useEffect(() => {
    if (!token) {
      return;
    }
    if (bootstrappedTokenRef.current === token) {
      return;
    }

    let cancelled = false;
    bootstrappedTokenRef.current = token;
    setLoadingConversation(true);

    api.listConversations(token)
      .then(async ({ conversations: loaded }) => {
        if (cancelled) {
          return;
        }
        setConversations(loaded);
        if (loaded[0]) {
          setActiveConversationId(loaded[0].id);
          const detail = await api.getConversation(token, loaded[0].id);
          if (!cancelled) {
            setMessages(detail.messages);
          }
        } else {
          setActiveConversationId(null);
          setMessages([]);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoadingConversation(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [token]);

  useEffect(() => {
    let cancelled = false;
    let pollTimer: ReturnType<typeof setTimeout> | null = null;

    const loadHealth = async () => {
      try {
        const health = await api.health();
        if (cancelled) {
          return;
        }
        setRuntimeHealth(health);
        if (health.runtime.some((component) => component.status === "pending" || component.status === "warming")) {
          pollTimer = setTimeout(loadHealth, 4000);
        }
      } catch {
        if (!cancelled) {
          setRuntimeHealth(null);
        }
      }
    };

    void loadHealth();

    return () => {
      cancelled = true;
      if (pollTimer) {
        clearTimeout(pollTimer);
      }
    };
  }, []);

  useEffect(() => {
    if (!token) {
      return;
    }

    let cancelled = false;
    api.dashboard(token)
      .then((analytics) => {
        if (!cancelled) {
          setDashboardAnalytics(analytics);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setDashboardAnalytics(null);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [token]);

  const emotionItems = useMemo(() => {
    if (!latestResponse) {
      return [
        { label: "Stress", value: 0 },
        { label: "Anxiety", value: 0 },
        { label: "Safety", value: 0 }
      ];
    }
    return [
      {
        label: latestResponse.emotion.primary_emotion,
        value: Math.round(latestResponse.emotion.emotional_intensity * 100)
      },
      {
        label: latestResponse.emotion.secondary_emotion ?? "confidence",
        value: Math.round(latestResponse.emotion.confidence * 100)
      },
      {
        label: "Safety",
        value: Math.round(latestResponse.safety.risk_score * 100)
      }
    ];
  }, [latestResponse]);

  const runtimePending = runtimeHealth?.runtime.filter(
    (component) => component.status === "pending" || component.status === "warming"
  );
  const trustedContactOptions = latestResponse?.trusted_contact_options ?? [];
  const emergencyResources = latestResponse?.safety.emergency_resources ?? [];

  const buildSmsHref = (phoneNumber: string, message: string) =>
    `sms:${phoneNumber}?body=${encodeURIComponent(message)}`;

  const buildMailHref = (email: string, subject: string, body: string) =>
    `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

  const priorityClasses: Record<"normal" | "important" | "urgent", string> = {
    normal: "border-sage-200 bg-white/70 text-sage-900",
    important: "border-amber-200 bg-amber-50 text-amber-900",
    urgent: "border-coral-200 bg-coral-50 text-coral-900"
  };
  const copilotCards = useMemo(() => {
    const baseCards = [
      {
        title: "Breathing reset",
        body: "Loosen your jaw, drop your shoulders, and do one slower exhale than inhale for the next minute.",
        icon: Flower2,
        tone: "from-sage-50 via-white to-mist dark:from-sage-950 dark:via-sage-900/80 dark:to-sage-950"
      },
      {
        title: "Journal prompt",
        body: "Write one sentence that starts with: “The hardest part of this right now is…”",
        icon: BookHeart,
        tone: "from-sand-50 via-white to-sand-100 dark:from-sand-950/30 dark:via-sage-950 dark:to-sand-950/20"
      },
      {
        title: "Next step",
        body: latestResponse?.support_actions[0]?.description ??
          "Choose the smallest useful action, not the most ambitious one.",
        icon: Compass,
        tone: "from-coral-50 via-white to-sand-50 dark:from-coral-950/20 dark:via-sage-950 dark:to-sand-950/20"
      }
    ];

    if (latestResponse?.safety.risk_level === "high" || latestResponse?.safety.risk_level === "critical") {
      baseCards[0] = {
        title: "Safety first",
        body: "Do not stay alone with this. Move toward a real person or use the trusted-support actions below.",
        icon: ShieldAlert,
        tone: "from-coral-50 via-white to-coral-100 dark:from-coral-950/30 dark:via-sage-950 dark:to-coral-950/20"
      };
    }

    return baseCards;
  }, [latestResponse]);
  const progressTrend = useMemo(() => {
    return dashboardAnalytics?.mood_trend.slice(-5) ?? [];
  }, [dashboardAnalytics]);
  const progressHighlights = useMemo(() => {
    if (!dashboardAnalytics) {
      return [
        { emoji: "🌱", label: "Support patterns", value: "Will appear after a few reflections" },
        { emoji: "📈", label: "Mood trend", value: "Live trend will show here" },
        { emoji: "🫶", label: "Weekly summary", value: "Your emotional pattern summary will build over time" }
      ];
    }

    return [
      {
        emoji: "🌱",
        label: "Dominant signal",
        value: dashboardAnalytics.hero.dominant_emotion
      },
      {
        emoji: "📈",
        label: "Weekly summary",
        value: dashboardAnalytics.hero.weekly_summary
      },
      {
        emoji: "🫶",
        label: "Safety status",
        value: dashboardAnalytics.hero.safety_status
      }
    ];
  }, [dashboardAnalytics]);
  const responseTags = useMemo(() => {
    if (!latestResponse) {
      return [
        { label: "Emotion", value: "Waiting", tone: "sage" },
        { label: "Mode", value: "Waiting", tone: "sand" },
        { label: "Risk", value: "Idle", tone: "coral" }
      ];
    }

    const formatValue = (value: string) =>
      value.charAt(0).toUpperCase() + value.slice(1).replaceAll("_", " ");

    return [
      {
        label: "Emotion",
        value: formatValue(latestResponse.emotion.primary_emotion),
        tone: "sage"
      },
      {
        label: "Mode",
        value: latestResponse.response_strategy.label,
        tone: "sand"
      },
      {
        label: "Risk",
        value: formatValue(latestResponse.safety.risk_level),
        tone: "coral"
      }
    ];
  }, [latestResponse]);
  const explainabilityStrip = useMemo(() => {
    if (!latestResponse) {
      return "Safebond will explain its reasoning here after the next live reflection.";
    }

    const memoryCount = latestResponse.rag_context.retrieved_memories.length;
    const memorySignal = memoryCount
      ? `${memoryCount} memory match${memoryCount > 1 ? "es" : ""}`
      : "no strong memory match yet";

    return `Why this response: detected ${latestResponse.emotion.primary_emotion}, selected ${latestResponse.response_strategy.label.toLowerCase()}, assessed risk as ${latestResponse.safety.risk_level}, and found ${memorySignal}.`;
  }, [latestResponse]);

  const sendMessage = async (text: string) => {
    if (!token || sendingRef.current) {
      return;
    }
    sendingRef.current = true;
    setError(null);
    setSending(true);
    const startedAt = new Date().toISOString();
    const pendingConversationId = activeConversationId ?? "pending-conversation";
    const pendingUserMessage: Message = {
      id: `pending-user-${Date.now()}`,
      conversation_id: pendingConversationId,
      user_id: "current-user",
      role: "user",
      content: text,
      created_at: startedAt
    };
    const pendingAssistantMessage: Message = {
      id: `pending-assistant-${Date.now()}`,
      conversation_id: pendingConversationId,
      user_id: "assistant",
      role: "assistant",
      content:
        runtimePending && runtimePending.length > 0
          ? "Safebond is warming up local AI models and preparing your response..."
          : "Safebond is reflecting on your message...",
      created_at: startedAt
    };

    setMessages((current) => [...current, pendingUserMessage, pendingAssistantMessage]);

    try {
      const response = await api.sendChatMessage(token, {
        message: text,
        conversation_id: activeConversationId ?? undefined,
        title: activeConversationId ? undefined : "New reflection"
      });
      setLatestResponse(response);
      setActiveConversationId(response.conversation.id);
      setMessages((current) =>
        current
          .filter(
            (message) =>
              message.id !== pendingUserMessage.id && message.id !== pendingAssistantMessage.id
          )
          .concat([response.user_message, response.assistant_message])
      );
      setConversations((current) => {
        const withoutCurrent = current.filter(
          (conversation) => conversation.id !== response.conversation.id
        );
        return [response.conversation, ...withoutCurrent];
      });
    } catch (err) {
      setMessages((current) =>
        current.filter(
          (message) =>
            message.id !== pendingUserMessage.id && message.id !== pendingAssistantMessage.id
        )
      );
      setError(err instanceof Error ? err.message : "Unable to send message.");
    } finally {
      sendingRef.current = false;
      setSending(false);
    }
  };

  return (
    <main className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
      <section className="space-y-4">
        <FadeIn>
          <Card className="p-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <SectionHeading
                eyebrow="Conversation Lab"
                title="Empathetic support grounded in memory and safety."
                description="The chat route now integrates authentication, emotion detection, conversational memory, safety gating, and moderated assistant output."
              />
              <div className="flex gap-3">
                <div className="rounded-full bg-sage-100 px-4 py-2 text-sm font-semibold text-sage-800 dark:bg-sage-900 dark:text-sand-50">
                  {activeConversationId ? "Conversation active" : "Start new conversation"}
                </div>
                <div className="rounded-full bg-coral-50 px-4 py-2 text-sm font-semibold text-coral-700 dark:bg-coral-950/30 dark:text-coral-100">
                  Safety route: {latestResponse?.safety.risk_level ?? "idle"}
                </div>
              </div>
            </div>
          </Card>
        </FadeIn>

        {runtimePending && runtimePending.length > 0 ? (
          <FadeIn delay={0.04}>
            <Card className="border-sand-200 bg-sand-50/80 p-5 dark:border-sand-800/60 dark:bg-sand-950/35">
              <p className="text-sm font-semibold text-sand-900 dark:text-sand-50">
                Local AI models are still warming up.
              </p>
              <p className="mt-2 text-sm leading-6 text-sage-800/80 dark:text-sand-50/86">
                Safebond is downloading or initializing the safety, emotion, and memory models in
                the background. The first live reply can take longer on a student laptop, but
                later replies should be much faster.
              </p>
            </Card>
          </FadeIn>
        ) : null}

        <FadeIn delay={0.08}>
          <Card className="sticky top-4 z-10 overflow-hidden p-6 dark:border-sage-800/70 dark:bg-sage-950/75">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.26em] text-sage-700/60 dark:text-sand-50/72">
                  Today’s support plan
                </p>
                <h3 className="mt-2 font-serif-display text-2xl text-ink dark:text-sand-50">
                  {latestResponse?.response_strategy.label ?? "Support mode will appear after your next reflection"}
                </h3>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-sage-800/76 dark:text-sand-50/86">
                  {latestResponse?.response_strategy.rationale ??
                    "Safebond will pin your current support mode here, then surface a few practical companion cards to help you act on it."}
                </p>
              </div>
              <div className="rounded-full bg-sage-100 px-4 py-2 text-sm font-semibold text-sage-800 dark:bg-sage-900 dark:text-sand-50">
                Risk: {latestResponse?.safety.risk_level ?? "idle"}
              </div>
            </div>
            <div className="mt-5 grid gap-3 lg:grid-cols-3">
              {copilotCards.map((card) => {
                const Icon = card.icon;
                return (
                  <div
                    key={card.title}
                    className={`rounded-[1.7rem] border border-white/70 bg-gradient-to-br ${card.tone} p-4 shadow-soft dark:border-sage-700/70`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="rounded-2xl bg-white/80 p-2 text-sage-800 shadow-soft dark:bg-sage-900 dark:text-sand-50">
                        <Icon className="h-4 w-4" />
                      </div>
                      <p className="text-sm font-semibold text-ink dark:text-sand-50">{card.title}</p>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-sage-900/78 dark:text-sand-50/88">
                      {card.body}
                    </p>
                  </div>
                );
              })}
            </div>
          </Card>
        </FadeIn>

        <FadeIn delay={0.1}>
          <Card className="overflow-hidden p-6 dark:border-sage-800/70 dark:bg-sage-950/75">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.26em] text-sage-700/60 dark:text-sand-50/72">
                  Seen over time
                </p>
                <h3 className="mt-2 font-serif-display text-2xl text-ink dark:text-sand-50">
                  Small shifts, not just single replies
                </h3>
              </div>
              <div className="flex items-center gap-2 rounded-full bg-sage-100 px-4 py-2 text-sm font-semibold text-sage-800 dark:bg-sage-900 dark:text-sand-50">
                <TrendingUp className="h-4 w-4" />
                Progress strip
              </div>
            </div>

            <div className="mt-5 grid gap-3 lg:grid-cols-3">
              {progressHighlights.map((item) => (
                <div
                  key={item.label}
                  className="rounded-[1.6rem] border border-white/70 bg-gradient-to-br from-white via-sage-50/70 to-sand-50/55 p-4 shadow-soft dark:border-sage-800/70 dark:from-sage-950 dark:via-sage-900/85 dark:to-sage-950"
                >
                  <p className="text-sm font-semibold text-ink dark:text-sand-50">
                    <span className="mr-2">{item.emoji}</span>
                    {item.label}
                  </p>
                  <p className="mt-3 text-sm leading-6 text-sage-900/76 dark:text-sand-50/86">
                    {item.value}
                  </p>
                </div>
              ))}
            </div>

            <div className="mt-5 rounded-[1.8rem] border border-sage-100 bg-sage-50/65 p-4 dark:border-sage-700/70 dark:bg-sage-900/78">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-semibold text-ink dark:text-sand-50">
                  Mood pulse over recent days
                </p>
                <p className="text-xs uppercase tracking-[0.22em] text-sage-700/60 dark:text-sand-50/72">
                  calm vs stress
                </p>
              </div>
              <div className="mt-4 grid grid-cols-5 gap-3">
                {progressTrend.length
                  ? progressTrend.map((point) => (
                      <div key={point.day} className="space-y-2 text-center">
                        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-sage-700/58 dark:text-sand-50/72">
                          {point.day}
                        </p>
                        <div className="flex h-24 items-end justify-center gap-1 rounded-2xl bg-white/75 px-3 py-2 dark:bg-sage-950/70">
                          <div
                            className="w-3 rounded-full bg-sage-400 dark:bg-sage-500"
                            style={{ height: `${Math.max(point.calm, 10)}%` }}
                          />
                          <div
                            className="w-3 rounded-full bg-coral-400 dark:bg-coral-500"
                            style={{ height: `${Math.max(point.stress, 10)}%` }}
                          />
                        </div>
                        <p className="text-[11px] text-sage-800/68 dark:text-sand-50/76">
                          {point.calm >= point.stress ? "🙂 calmer" : "🌀 stressed"}
                        </p>
                      </div>
                    ))
                  : Array.from({ length: 5 }).map((_, index) => (
                      <div key={index} className="space-y-2 text-center">
                        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-sage-700/58 dark:text-sand-50/72">
                          Day {index + 1}
                        </p>
                        <div className="flex h-24 items-end justify-center gap-1 rounded-2xl bg-white/75 px-3 py-2 dark:bg-sage-950/70">
                          <div className="h-8 w-3 rounded-full bg-sage-200 dark:bg-sage-800" />
                          <div className="h-10 w-3 rounded-full bg-coral-200 dark:bg-coral-900/70" />
                        </div>
                        <p className="text-[11px] text-sage-800/68 dark:text-sand-50/76">waiting</p>
                      </div>
                    ))}
              </div>
            </div>
          </Card>
        </FadeIn>

        <FadeIn delay={0.12}>
          <div className="grid gap-3 sm:grid-cols-3">
            {responseTags.map((tag) => (
              <Card
                key={tag.label}
                className={`p-4 ${
                  tag.tone === "sage"
                    ? "bg-gradient-to-br from-sage-50 via-white to-mist dark:from-sage-950 dark:via-sage-900/80 dark:to-sage-950"
                    : tag.tone === "sand"
                      ? "bg-gradient-to-br from-sand-50 via-white to-sand-100 dark:from-sand-950/30 dark:via-sage-950 dark:to-sand-950/20"
                      : "bg-gradient-to-br from-coral-50 via-white to-sand-50 dark:from-coral-950/20 dark:via-sage-950 dark:to-sand-950/20"
                }`}
              >
                <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-sage-700/58 dark:text-sand-50/72">
                  {tag.label}
                </p>
                <p className="mt-2 font-serif-display text-2xl text-ink dark:text-sand-50">
                  {tag.value}
                </p>
              </Card>
            ))}
          </div>
        </FadeIn>

        <FadeIn delay={0.13}>
          <Card className="p-4 dark:border-sage-800/70 dark:bg-sage-950/75">
            <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-sage-700/58 dark:text-sand-50/72">
              Why this response
            </p>
            <p className="mt-2 text-sm leading-6 text-sage-900/78 dark:text-sand-50/86">
              {explainabilityStrip}
            </p>
          </Card>
        </FadeIn>

        <FadeIn delay={0.14}>
          <Card className="p-6">
            {error ? <p className="mb-4 text-sm text-coral-700 dark:text-coral-200">{error}</p> : null}
            {loadingConversation ? (
              <p className="mb-4 text-sm text-sage-800/72 dark:text-sand-50/82">Loading your conversation history...</p>
            ) : null}
            <ChatThread messages={messages} />
          </Card>
        </FadeIn>

        <FadeIn delay={0.18}>
          <ChatComposer onSend={sendMessage} sending={sending} />
        </FadeIn>
      </section>

      <section className="space-y-4">
        <FadeIn delay={0.12}>
          <Card className="p-6">
            <div className="flex items-center gap-3">
              <div className="rounded-2xl bg-sage-100 p-3 text-sage-800 dark:bg-sage-900 dark:text-sand-50">
                <Sparkles className="h-4 w-4" />
              </div>
              <div>
                <h3 className="font-serif-display text-2xl text-ink dark:text-sand-50">Emotion panel</h3>
                <p className="text-sm text-sage-800/72 dark:text-sand-50/82">
                  Current live outputs from the emotion and safety stack
                </p>
              </div>
            </div>
            <div className="mt-6">
              <EmotionPulse items={emotionItems} />
            </div>
          </Card>
        </FadeIn>

        <FadeIn delay={0.18}>
          <Card className="p-6">
            <div className="flex items-center gap-3">
              <div className="rounded-2xl bg-sand-100 p-3 text-sand-900 dark:bg-sand-900 dark:text-sand-50">
                <MessageCircle className="h-4 w-4" />
              </div>
              <div>
                <h3 className="font-serif-display text-2xl text-ink dark:text-sand-50">Retrieved memory</h3>
                <p className="text-sm text-sage-800/72 dark:text-sand-50/82">
                  Context injected by the backend RAG layer
                </p>
              </div>
            </div>
            <div className="mt-6">
              <MemoryPanel memories={latestResponse ? latestResponse.rag_context.retrieved_memories : undefined} />
            </div>
          </Card>
        </FadeIn>

        <FadeIn delay={0.24}>
          <Card className="bg-sage-900 p-6 text-white dark:border-sage-800/70 dark:bg-sage-900/90">
            <div className="flex items-center gap-3">
              <div className="rounded-2xl bg-white/10 p-3 text-white">
                <ShieldCheck className="h-4 w-4" />
              </div>
              <div>
                <h3 className="font-serif-display text-2xl">Safety routing</h3>
                <p className="text-sm text-white/70">
                  Moderation action: {latestResponse?.moderation.action_taken ?? "pending"}
                </p>
              </div>
            </div>
            <div className="mt-6 space-y-4">
              <div className="rounded-[1.5rem] bg-white/8 p-4 text-sm leading-7 text-white/80">
                <p className="text-xs font-semibold uppercase tracking-[0.28em] text-white/55">
                  Response mode
                </p>
                <p className="mt-2 text-base font-semibold text-white">
                  {latestResponse?.response_strategy.label ?? "Awaiting live message"}
                </p>
                <p className="mt-2">
                  {latestResponse?.response_strategy.rationale ??
                    "The system will explain which support strategy it selected after the next live response."}
                </p>
              </div>
              <div className="rounded-[1.5rem] bg-white/8 p-4 text-sm leading-7 text-white/80">
                <p className="text-xs font-semibold uppercase tracking-[0.28em] text-white/55">
                  Retrieval summary
                </p>
                <p className="mt-2">
                  {latestResponse?.rag_context.retrieval_summary ??
                    "The system will surface memory retrieval and moderation summaries once a live message is sent."}
                </p>
              </div>
              {latestResponse?.support_actions.length ? (
                <div className="space-y-3 rounded-[1.5rem] bg-white/8 p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.28em] text-white/55">
                    Suggested next steps
                  </p>
                  <div className="space-y-2">
                    {latestResponse.support_actions.map((action) => (
                      <div
                        key={`${action.kind}-${action.label}`}
                        className={`rounded-2xl border px-4 py-3 text-sm leading-6 dark:border-sage-800 ${priorityClasses[action.priority]}`}
                      >
                        <p className="font-semibold">{action.label}</p>
                        <p className="mt-1 opacity-90">{action.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          </Card>
        </FadeIn>

        <FadeIn delay={0.3}>
          <Card className="border-coral-100 bg-gradient-to-br from-coral-50 via-white to-sand-50 p-6 dark:border-coral-900/40 dark:from-sage-950 dark:via-sage-900/88 dark:to-sand-950/32">
            <div className="flex items-center gap-3">
              <div className="rounded-2xl bg-coral-100 p-3 text-coral-700 dark:bg-coral-950/50 dark:text-coral-100">
                <ShieldAlert className="h-4 w-4" />
              </div>
              <div>
                <h3 className="font-serif-display text-2xl text-ink dark:text-sand-50">Trusted support plan</h3>
                <p className="text-sm text-sage-800/72 dark:text-sand-50/82">
                  Consent-based outreach appears here only when Safebond sees elevated risk.
                </p>
              </div>
            </div>

            {trustedContactOptions.length ? (
              <div className="mt-6 space-y-4">
                {trustedContactOptions.map((contact) => (
                  <div
                    key={contact.contact_id}
                    className="rounded-[1.5rem] border border-coral-100 bg-white/80 p-4 dark:border-coral-900/40 dark:bg-[#182323]/90"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div>
                        <p className="text-lg font-semibold text-ink dark:text-sand-50">{contact.name}</p>
                        <p className="text-sm text-sage-800/72 dark:text-sand-50/82">{contact.relationship_to_user}</p>
                      </div>
                      <span className="rounded-full bg-coral-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-coral-700 dark:bg-coral-950/50 dark:text-coral-100">
                        high-support prompt
                      </span>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-sage-800/82 dark:text-sand-50/86">{contact.why_now}</p>
                    <div className="mt-4 flex flex-wrap gap-3">
                      {contact.phone_number && contact.sms_message ? (
                        <a
                          href={buildSmsHref(contact.phone_number, contact.sms_message)}
                          className="inline-flex items-center gap-2 rounded-full border border-sage-200 bg-white px-4 py-2 text-sm font-semibold text-ink transition hover:bg-sage-50 dark:border-sage-700 dark:bg-sage-900 dark:text-sand-50 dark:hover:bg-sage-800"
                        >
                          <MessageSquareText className="h-4 w-4" />
                          Text contact
                        </a>
                      ) : null}
                      {contact.phone_number ? (
                        <a
                          href={`tel:${contact.phone_number}`}
                          className="inline-flex items-center gap-2 rounded-full border border-sage-200 bg-white px-4 py-2 text-sm font-semibold text-ink transition hover:bg-sage-50 dark:border-sage-700 dark:bg-sage-900 dark:text-sand-50 dark:hover:bg-sage-800"
                        >
                          <PhoneCall className="h-4 w-4" />
                          Call contact
                        </a>
                      ) : null}
                      {contact.email && contact.email_subject && contact.email_body ? (
                        <a
                          href={buildMailHref(contact.email, contact.email_subject, contact.email_body)}
                          className="inline-flex items-center gap-2 rounded-full border border-sage-200 bg-white px-4 py-2 text-sm font-semibold text-ink transition hover:bg-sage-50 dark:border-sage-700 dark:bg-sage-900 dark:text-sand-50 dark:hover:bg-sage-800"
                        >
                          <MessageCircle className="h-4 w-4" />
                          Email contact
                        </a>
                      ) : null}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="mt-6 rounded-[1.5rem] border border-dashed border-sage-200 bg-white/70 p-4 text-sm leading-6 text-sage-800/76 dark:border-sage-700/70 dark:bg-sage-900/72 dark:text-sand-50/84">
                Safebond will surface trusted-contact actions here when a conversation reaches a
                higher-risk threshold and the user has enabled contact reminders during onboarding.
              </div>
            )}

            {emergencyResources.length ? (
              <div className="mt-5 space-y-3 rounded-[1.5rem] border border-coral-100 bg-white/80 p-4 dark:border-coral-900/40 dark:bg-[#182323]/90">
                <p className="text-xs font-semibold uppercase tracking-[0.28em] text-coral-700 dark:text-coral-100">
                  Crisis resources
                </p>
                <div className="space-y-2">
                  {emergencyResources.map((resource) => (
                    <div
                      key={`${resource.name}-${resource.contact}`}
                      className="flex flex-wrap items-center justify-between gap-3 rounded-2xl bg-coral-50/60 px-4 py-3 dark:bg-coral-950/32"
                    >
                      <div>
                        <p className="font-semibold text-ink dark:text-sand-50">{resource.name}</p>
                        <p className="text-sm text-sage-800/72 dark:text-sand-50/82">{resource.availability}</p>
                      </div>
                      <a
                        href={`tel:${resource.contact}`}
                        className="inline-flex items-center gap-2 rounded-full bg-coral-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-coral-700"
                      >
                        <PhoneCall className="h-4 w-4" />
                        {resource.contact}
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}
          </Card>
        </FadeIn>
      </section>
    </main>
  );
}
