import {
  AuthTokenResponse,
  ChatResponse,
  Conversation,
  DashboardAnalytics,
  HealthResponse,
  InsightsAnalytics,
  Message,
  User,
  WellnessProfileEnvelope,
  WellnessProfileStatus
} from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

type RequestOptions = {
  method?: string;
  token?: string | null;
  body?: unknown;
};

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: options.method ?? "GET",
      headers: {
        "Content-Type": "application/json",
        ...(options.token ? { Authorization: `Bearer ${options.token}` } : {})
      },
      body: options.body ? JSON.stringify(options.body) : undefined,
      cache: "no-store"
    });
  } catch (error) {
    throw new ApiError(
      error instanceof Error
        ? `Unable to reach the Safebond backend. ${error.message}`
        : "Unable to reach the Safebond backend.",
      0
    );
  }

  if (!response.ok) {
    let detail = "Request failed.";
    try {
      const data = await response.json();
      detail = data.detail ?? data.message ?? detail;
    } catch {
      detail = response.statusText || detail;
    }
    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as T;
}

export const api = {
  register(payload: {
    email: string;
    password: string;
    display_name: string;
    timezone: string;
  }) {
    return request<AuthTokenResponse>("/auth/register", {
      method: "POST",
      body: payload
    });
  },
  login(payload: { email: string; password: string }) {
    return request<AuthTokenResponse>("/auth/login", {
      method: "POST",
      body: payload
    });
  },
  me(token: string) {
    return request<User>("/auth/me", { token });
  },
  profileStatus(token: string) {
    return request<WellnessProfileStatus>("/profile/status", { token });
  },
  getProfile(token: string) {
    return request<WellnessProfileEnvelope>("/profile/me", { token });
  },
  saveProfile(
    token: string,
    payload: {
      questionnaire_answers: {
        question_id: string;
        prompt: string;
        score: number;
      }[];
      support_goals?: string | null;
      personal_notes?: string | null;
      allow_contact_reminders_in_high_risk: boolean;
      emergency_contacts: {
        name: string;
        relationship_to_user: string;
        phone_number?: string | null;
        email?: string | null;
        notes?: string | null;
      }[];
    }
  ) {
    return request<WellnessProfileEnvelope>("/profile/me", {
      method: "PUT",
      token,
      body: payload
    });
  },
  health() {
    return request<HealthResponse>("/health");
  },
  dashboard(token: string) {
    return request<DashboardAnalytics>("/analytics/dashboard", { token });
  },
  insights(token: string) {
    return request<InsightsAnalytics>("/analytics/insights", { token });
  },
  listConversations(token: string) {
    return request<{ conversations: Conversation[] }>("/conversations", { token });
  },
  getConversation(token: string, conversationId: string) {
    return request<{ conversation: Conversation; messages: Message[] }>(
      `/conversations/${conversationId}`,
      { token }
    );
  },
  sendChatMessage(
    token: string,
    payload: { message: string; conversation_id?: string; title?: string }
  ) {
    return request<ChatResponse>("/chat/message", {
      method: "POST",
      token,
      body: payload
    });
  }
};
