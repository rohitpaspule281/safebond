export const dashboardStats = [
  {
    title: "Calm Recovery Index",
    value: "74%",
    trend: "+8.2%",
    detail: "Steadier recovery after stressful evenings",
    accent: "from-sage-500/25 to-sage-200/50"
  },
  {
    title: "Risk Escalations Prevented",
    value: "12",
    trend: "Safety-first",
    detail: "High-risk sessions routed into escalation policy",
    accent: "from-coral-500/20 to-sand-200/50"
  },
  {
    title: "Memory Recall Accuracy",
    value: "91%",
    trend: "Top-k context",
    detail: "Personalized recall from longitudinal conversation memory",
    accent: "from-sand-400/20 to-white/60"
  }
] as const;

export const moodTrend = [
  { day: "Mon", calm: 58, stress: 44, loneliness: 28 },
  { day: "Tue", calm: 62, stress: 48, loneliness: 24 },
  { day: "Wed", calm: 55, stress: 61, loneliness: 31 },
  { day: "Thu", calm: 68, stress: 40, loneliness: 19 },
  { day: "Fri", calm: 64, stress: 46, loneliness: 25 },
  { day: "Sat", calm: 72, stress: 30, loneliness: 16 },
  { day: "Sun", calm: 76, stress: 26, loneliness: 14 }
];

export const stressHeatmap = [
  ["Low", "Low", "Moderate", "Moderate", "Low", "Low", "Low"],
  ["Moderate", "Moderate", "High", "High", "Moderate", "Low", "Low"],
  ["Low", "Moderate", "High", "Moderate", "Low", "Low", "Low"],
  ["Low", "Low", "Moderate", "Moderate", "Low", "Low", "Low"]
] as const;

export const chatMessages = [
  {
    id: "1",
    role: "assistant",
    text: "You handled a lot this week. Before we jump into solutions, what feels heaviest right now: pressure, loneliness, or the sense of running on empty?"
  },
  {
    id: "2",
    role: "user",
    text: "Mostly pressure. I feel like I’m doing everything at once, and even when I stop working my brain keeps going."
  },
  {
    id: "3",
    role: "assistant",
    text: "That sounds closer to sustained stress than a single bad moment. I’m noticing a pattern of overextension in your recent check-ins too. We can work on slowing the mental spillover first."
  }
] as const;

export const recentMemories = [
  {
    title: "Deadline Spiral",
    detail: "Retrieved from Wednesday 11:42 PM",
    score: "0.92",
    tag: "Stress"
  },
  {
    title: "Sleep Disruption Pattern",
    detail: "Retrieved from Monday 1:08 AM",
    score: "0.88",
    tag: "Anxiety"
  },
  {
    title: "Supportive Friend Mention",
    detail: "Retrieved from last Sunday",
    score: "0.81",
    tag: "Protective factor"
  }
] as const;

export const emotionPulse = [
  { label: "Sadness", value: 31 },
  { label: "Anxiety", value: 67 },
  { label: "Stress", value: 74 },
  { label: "Loneliness", value: 22 },
  { label: "Burnout", value: 59 },
  { label: "Anger", value: 18 }
];

export const sidebarItems = [
  { href: "/dashboard", label: "Overview" },
  { href: "/chat", label: "Conversation Lab" },
  { href: "/insights", label: "Mood Analytics" }
] as const;
