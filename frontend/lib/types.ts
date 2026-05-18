export type User = {
  id: string;
  email: string;
  display_name: string;
  timezone: string;
  is_active: boolean;
  created_at: string;
};

export type AuthTokenResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
};

export type Conversation = {
  id: string;
  title: string;
  summary: string | null;
  created_at: string;
  updated_at: string;
  last_message_at: string | null;
};

export type Message = {
  id: string;
  conversation_id: string;
  user_id: string;
  role: string;
  content: string;
  created_at: string;
};

export type MemoryResult = {
  memory_id: string;
  message_id: string;
  conversation_id: string;
  role: string;
  content: string;
  semantic_score: number;
  recency_score: number;
  importance_score: number;
  same_conversation_boost: number;
  final_score: number;
  created_at: string | null;
};

export type EmotionLabelScore = {
  label: string;
  score: number;
};

export type EmotionAnalysis = {
  text: string;
  primary_emotion: string;
  secondary_emotion: string | null;
  emotional_intensity: number;
  confidence: number;
  top_emotions: EmotionLabelScore[];
};

export type SafetyAssessment = {
  risk_level: "low" | "moderate" | "high" | "critical";
  risk_score: number;
  safe_fallback_response: string;
  policy_action: string;
  should_block_standard_response: boolean;
  needs_immediate_escalation: boolean;
  emergency_resources: EmergencyResource[];
};

export type RuntimeComponentStatus = {
  name: string;
  status: "pending" | "warming" | "ready" | "error";
  detail: string;
  warmed_at: string | null;
};

export type HealthResponse = {
  status: "ok" | "degraded";
  app_name: string;
  environment: string;
  version: string;
  services: {
    name: string;
    status: "up" | "down";
    detail: string;
  }[];
  runtime: RuntimeComponentStatus[];
};

export type EmergencyResource = {
  name: string;
  contact: string;
  kind: string;
  availability: string;
  region: string;
  source_name: string;
  source_url: string;
};

export type TrustedContact = {
  id: string;
  name: string;
  relationship_to_user: string;
  phone_number: string | null;
  email: string | null;
  notes: string | null;
  created_at: string;
};

export type WellnessProfile = {
  id: string;
  user_id: string;
  current_state_of_mind: string;
  primary_stressors: string | null;
  support_goals: string | null;
  inferred_risk_level: string;
  has_recent_suicidal_thoughts: boolean;
  would_like_crisis_resources: boolean;
  allow_contact_reminders_in_high_risk: boolean;
  emergency_contacts: TrustedContact[];
  created_at: string;
  updated_at: string;
  onboarding_completed_at: string | null;
};

export type WellnessProfileStatus = {
  completed: boolean;
  trusted_contacts_count: number;
  inferred_risk_level: string;
  has_recent_suicidal_thoughts: boolean;
  recommended_resources: EmergencyResource[];
};

export type WellnessProfileEnvelope = {
  completed: boolean;
  profile: WellnessProfile | null;
  recommended_resources: EmergencyResource[];
};

export type ChatResponse = {
  conversation: Conversation;
  user_message: Message;
  assistant_message: Message;
  emotion: EmotionAnalysis;
  safety: SafetyAssessment;
  rag_context: {
    query: string;
    conversation_id: string | null;
    retrieved_memories: MemoryResult[];
    injected_context: string;
    retrieval_summary: string;
  };
  moderation: {
    action_taken: "allow" | "sanitize" | "replace_with_fallback";
    moderated_response: string;
  };
  response_strategy: {
    key:
      | "validation"
      | "grounding"
      | "reflection"
      | "reframing"
      | "action_step"
      | "memory_continuity"
      | "containment";
    label: string;
    rationale: string;
  };
  support_actions: {
    kind:
      | "reflect"
      | "ground"
      | "journal"
      | "reach_out"
      | "call_trusted_contact"
      | "text_trusted_contact"
      | "view_crisis_resources";
    label: string;
    description: string;
    priority: "normal" | "important" | "urgent";
  }[];
  trusted_contact_options: {
    contact_id: string;
    name: string;
    relationship_to_user: string;
    phone_number: string | null;
    email: string | null;
    why_now: string;
    sms_message: string | null;
    email_subject: string | null;
    email_body: string | null;
    call_recommended: boolean;
  }[];
};

export type DashboardAnalytics = {
  hero: {
    dominant_emotion: string;
    safety_status: string;
    weekly_summary: string;
  };
  stats: {
    title: string;
    value: string;
    trend: string;
    detail: string;
    accent: string;
  }[];
  mood_trend: {
    day: string;
    calm: number;
    stress: number;
    loneliness: number;
  }[];
  emotion_distribution: {
    emotion: string;
    share: number;
    avg_intensity: number;
    color: string;
  }[];
  risk_trend: {
    day: string;
    avg_risk: number;
    elevated: number;
    high_alerts: number;
  }[];
  session_activity: {
    day: string;
    messages: number;
    avg_words: number;
    reflection_depth: number;
  }[];
  heatmap: { value: string }[][];
  insights: {
    title: string;
    body: string;
    tone: string;
  }[];
};

export type InsightsAnalytics = {
  trend: {
    day: string;
    calm: number;
    stress: number;
    loneliness: number;
  }[];
  emotion_distribution: {
    emotion: string;
    share: number;
    avg_intensity: number;
    color: string;
  }[];
  risk_trend: {
    day: string;
    avg_risk: number;
    elevated: number;
    high_alerts: number;
  }[];
  session_activity: {
    day: string;
    messages: number;
    avg_words: number;
    reflection_depth: number;
  }[];
  heatmap: { value: string }[][];
  summaries: {
    title: string;
    body: string;
  }[];
};
