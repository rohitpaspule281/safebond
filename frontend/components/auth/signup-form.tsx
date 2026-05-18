"use client";

import { FormEvent, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/providers/auth-provider";
import { Button } from "@/components/ui/button";

export function SignupForm() {
  const router = useRouter();
  const { signUp } = useAuth();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [timezone, setTimezone] = useState("Asia/Kolkata");
  const [acknowledged, setAcknowledged] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const canSubmit = useMemo(
    () => acknowledged && fullName.trim() && email.trim() && password.trim(),
    [acknowledged, email, fullName, password]
  );

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await signUp({
        email,
        password,
        display_name: fullName,
        timezone
      });
      router.push("/onboarding");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create account.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="contents" onSubmit={onSubmit}>
      <div className="mt-10 grid gap-4 sm:grid-cols-2">
        <input
          className="rounded-[1.5rem] border border-sage-200 bg-sage-50/60 px-4 py-4 text-sm outline-none"
          placeholder="Full name"
          value={fullName}
          onChange={(event) => setFullName(event.target.value)}
        />
        <input
          className="rounded-[1.5rem] border border-sage-200 bg-sage-50/60 px-4 py-4 text-sm outline-none"
          placeholder="Email address"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />
        <input
          className="rounded-[1.5rem] border border-sage-200 bg-sage-50/60 px-4 py-4 text-sm outline-none"
          placeholder="Password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
        <input
          className="rounded-[1.5rem] border border-sage-200 bg-sage-50/60 px-4 py-4 text-sm outline-none"
          placeholder="Timezone"
          value={timezone}
          onChange={(event) => setTimezone(event.target.value)}
        />
      </div>
      <label className="mt-6 flex items-start gap-3 rounded-[1.5rem] border border-sand-200 bg-sand-50/80 p-4 text-sm leading-6 text-sage-900/78">
        <input
          className="mt-1"
          type="checkbox"
          checked={acknowledged}
          onChange={(event) => setAcknowledged(event.target.checked)}
        />
        <span>
          I understand Safebond is an AI support system for emotional wellness, not a therapist or crisis substitute.
        </span>
      </label>
      {error ? <p className="mt-4 text-sm text-coral-700">{error}</p> : null}
      <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
        <Button disabled={!canSubmit || loading} type="submit">
          {loading ? "Creating account..." : "Create account"}
        </Button>
      </div>
    </form>
  );
}
