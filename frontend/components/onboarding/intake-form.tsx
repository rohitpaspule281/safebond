"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/providers/auth-provider";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import type { EmergencyResource } from "@/lib/types";

type TrustedContactDraft = {
  name: string;
  relationship_to_user: string;
  phone_number: string;
  email: string;
  notes: string;
};

type QuestionnairePrompt = {
  id: string;
  prompt: string;
  helper: string;
};

const SCALE_LABELS = ["Not at all", "Rarely", "Sometimes", "Often", "Almost always"];

const QUESTIONS: QuestionnairePrompt[] = [
  {
    id: "overwhelm",
    prompt: "How often have you felt emotionally overwhelmed by daily life recently?",
    helper: "Measures current emotional load."
  },
  {
    id: "sleep",
    prompt: "How difficult has it been to calm your mind enough to rest or sleep well?",
    helper: "Tracks cognitive activation and recovery difficulty."
  },
  {
    id: "withdrawal",
    prompt: "How often have you pulled away from people who usually feel safe or supportive?",
    helper: "Captures isolation and withdrawal patterns."
  },
  {
    id: "hope",
    prompt: "How hard has it been to imagine things improving in the near future?",
    helper: "Captures hopelessness without asking directly about self-harm."
  },
  {
    id: "motivation",
    prompt: "How difficult has it been to do basic tasks like getting up, eating, or attending to responsibilities?",
    helper: "Estimates functional strain."
  },
  {
    id: "pressure",
    prompt: "How trapped have you felt by responsibilities, deadlines, or expectations?",
    helper: "Surfaces burnout and pressure signatures."
  },
  {
    id: "self_worth",
    prompt: "How often have you felt like a burden, not good enough, or hard on yourself?",
    helper: "Captures self-worth stress indirectly."
  },
  {
    id: "grounded_safety",
    prompt: "When distress spikes, how hard is it to stay grounded, regulated, and safe?",
    helper: "A safety-oriented question without directly asking about suicidality."
  },
  {
    id: "panic",
    prompt: "How often have you experienced racing thoughts, panic, or intense inner agitation?",
    helper: "Captures anxious activation."
  },
  {
    id: "support",
    prompt: "How unsupported or alone have you felt even when people are around you?",
    helper: "Measures perceived disconnection."
  }
];

const emptyContact: TrustedContactDraft = {
  name: "",
  relationship_to_user: "",
  phone_number: "",
  email: "",
  notes: ""
};

function initialAnswers() {
  return Object.fromEntries(QUESTIONS.map((question) => [question.id, 0])) as Record<string, number>;
}

export function IntakeForm() {
  const router = useRouter();
  const { initialized, token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resources, setResources] = useState<EmergencyResource[]>([]);
  const [answers, setAnswers] = useState<Record<string, number>>(initialAnswers);
  const [supportGoals, setSupportGoals] = useState("");
  const [personalNotes, setPersonalNotes] = useState("");
  const [allowHighRiskContactReminders, setAllowHighRiskContactReminders] = useState(true);
  const [contact, setContact] = useState<TrustedContactDraft>(emptyContact);

  useEffect(() => {
    if (!initialized) {
      return;
    }
    if (!token) {
      router.replace("/login");
      return;
    }

    let cancelled = false;
    api.getProfile(token)
      .then((response) => {
        if (cancelled) {
          return;
        }
        if (response.completed && response.profile?.onboarding_completed_at) {
          router.replace("/dashboard");
          return;
        }
        if (response.profile) {
          setSupportGoals(response.profile.support_goals ?? "");
          setAllowHighRiskContactReminders(response.profile.allow_contact_reminders_in_high_risk);
          setResources(response.recommended_resources);
          const firstContact = response.profile.emergency_contacts[0];
          if (firstContact) {
            setContact({
              name: firstContact.name,
              relationship_to_user: firstContact.relationship_to_user,
              phone_number: firstContact.phone_number ?? "",
              email: firstContact.email ?? "",
              notes: firstContact.notes ?? ""
            });
          }
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unable to load your intake profile.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [initialized, router, token]);

  const totalScore = useMemo(
    () => Object.values(answers).reduce((sum, value) => sum + value, 0),
    [answers]
  );

  const canSubmit =
    contact.name.trim() &&
    contact.relationship_to_user.trim() &&
    (contact.phone_number.trim() || contact.email.trim());

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!token) {
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const response = await api.saveProfile(token, {
        questionnaire_answers: QUESTIONS.map((question) => ({
          question_id: question.id,
          prompt: question.prompt,
          score: answers[question.id] ?? 0
        })),
        support_goals: supportGoals || null,
        personal_notes: personalNotes || null,
        allow_contact_reminders_in_high_risk: allowHighRiskContactReminders,
        emergency_contacts: [
          {
            name: contact.name,
            relationship_to_user: contact.relationship_to_user,
            phone_number: contact.phone_number || null,
            email: contact.email || null,
            notes: contact.notes || null
          }
        ]
      });
      setResources(response.recommended_resources);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save your intake profile.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <p className="text-sm text-sage-800/76">Loading your intake questionnaire...</p>;
  }

  return (
    <form className="space-y-8" onSubmit={onSubmit}>
      <div className="rounded-[1.75rem] border border-sage-200 bg-sage-50/55 p-5">
        <p className="text-sm font-semibold text-ink">10-question psychological check-in</p>
        <p className="mt-2 text-sm leading-6 text-sage-800/78">
          Safebond uses these responses to infer emotional pressure, disconnection, hopelessness,
          regulation difficulty, and support needs without asking a direct self-harm question.
        </p>
        <div className="mt-4 inline-flex rounded-full bg-white/80 px-4 py-2 text-sm font-semibold text-sage-900">
          Current distress load estimate: {totalScore}/40
        </div>
      </div>

      <div className="space-y-4">
        {QUESTIONS.map((question, index) => (
          <div
            key={question.id}
            className="rounded-[1.75rem] border border-white/70 bg-white/82 p-5 shadow-soft"
          >
            <p className="text-xs uppercase tracking-[0.22em] text-sage-700/60">
              Question {index + 1}
            </p>
            <h3 className="mt-2 font-semibold text-ink">{question.prompt}</h3>
            <p className="mt-1 text-sm text-sage-800/72">{question.helper}</p>
            <div className="mt-4 grid gap-2 sm:grid-cols-5">
              {SCALE_LABELS.map((label, value) => {
                const selected = answers[question.id] === value;
                return (
                  <button
                    key={label}
                    type="button"
                    className={`rounded-[1.25rem] border px-3 py-3 text-sm transition ${
                      selected
                        ? "border-sage-700 bg-sage-800 text-white"
                        : "border-sage-200 bg-sage-50/60 text-sage-900 hover:bg-sage-100"
                    }`}
                    onClick={() =>
                      setAnswers((current) => ({
                        ...current,
                        [question.id]: value
                      }))
                    }
                  >
                    {label}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <textarea
          className="min-h-[130px] rounded-[1.5rem] border border-sage-200 bg-sage-50/60 px-4 py-4 text-sm outline-none"
          placeholder="What kind of support would help most from Safebond?"
          value={supportGoals}
          onChange={(event) => setSupportGoals(event.target.value)}
        />
        <textarea
          className="min-h-[130px] rounded-[1.5rem] border border-sage-200 bg-sage-50/60 px-4 py-4 text-sm outline-none"
          placeholder="Anything else you want Safebond to keep in mind?"
          value={personalNotes}
          onChange={(event) => setPersonalNotes(event.target.value)}
        />
      </div>

      <div className="rounded-[1.75rem] border border-sky-200 bg-sky-50/65 p-5">
        <p className="text-sm font-semibold text-ink">Trusted contact</p>
        <p className="mt-2 text-sm leading-6 text-sage-800/78">
          Please add at least one trusted person. Safebond can surface this contact back to the
          user during higher-risk conversations as part of a safer support flow.
        </p>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <input
            className="rounded-[1.5rem] border border-sky-200 bg-white/85 px-4 py-4 text-sm outline-none"
            placeholder="Trusted contact name"
            value={contact.name}
            onChange={(event) => setContact((current) => ({ ...current, name: event.target.value }))}
          />
          <input
            className="rounded-[1.5rem] border border-sky-200 bg-white/85 px-4 py-4 text-sm outline-none"
            placeholder="Relationship"
            value={contact.relationship_to_user}
            onChange={(event) =>
              setContact((current) => ({ ...current, relationship_to_user: event.target.value }))
            }
          />
          <input
            className="rounded-[1.5rem] border border-sky-200 bg-white/85 px-4 py-4 text-sm outline-none"
            placeholder="Phone number"
            value={contact.phone_number}
            onChange={(event) =>
              setContact((current) => ({ ...current, phone_number: event.target.value }))
            }
          />
          <input
            className="rounded-[1.5rem] border border-sky-200 bg-white/85 px-4 py-4 text-sm outline-none"
            placeholder="Email"
            value={contact.email}
            onChange={(event) => setContact((current) => ({ ...current, email: event.target.value }))}
          />
        </div>
        <textarea
          className="mt-4 min-h-[96px] w-full rounded-[1.5rem] border border-sky-200 bg-white/85 px-4 py-4 text-sm outline-none"
          placeholder="Notes about why this person is a safe contact or when to reach out."
          value={contact.notes}
          onChange={(event) => setContact((current) => ({ ...current, notes: event.target.value }))}
        />
        <label className="mt-4 flex items-start gap-3 text-sm leading-6 text-sage-900/82">
          <input
            className="mt-1"
            type="checkbox"
            checked={allowHighRiskContactReminders}
            onChange={(event) => setAllowHighRiskContactReminders(event.target.checked)}
          />
          <span>Allow Safebond to remind me of this trusted contact during higher-risk moments.</span>
        </label>
      </div>

      {resources.length > 0 ? (
        <div className="rounded-[1.75rem] border border-coral-200 bg-coral-50/75 p-5">
          <p className="text-sm font-semibold text-coral-900">Support resources prepared for you</p>
          <div className="mt-4 grid gap-3">
            {resources.map((resource) => (
              <div key={`${resource.name}-${resource.contact}`} className="rounded-[1.25rem] bg-white/85 p-4">
                <p className="font-semibold text-ink">{resource.name}</p>
                <p className="mt-1 text-sm text-sage-800/78">
                  {resource.contact} · {resource.availability} · {resource.region}
                </p>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {error ? <p className="text-sm text-coral-700">{error}</p> : null}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <Button disabled={saving || !canSubmit} type="submit">
          {saving ? "Analyzing responses..." : "Analyze and continue"}
        </Button>
      </div>
    </form>
  );
}
