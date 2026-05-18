"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/providers/auth-provider";
import { Button } from "@/components/ui/button";

export function LoginForm() {
  const router = useRouter();
  const { signIn } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await signIn({ email, password });
      router.push("/onboarding");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="mt-8 space-y-4" onSubmit={onSubmit}>
      <input
        className="w-full rounded-[1.5rem] border border-sage-200 bg-sage-50/75 px-4 py-4 text-sm text-sage-950 outline-none transition placeholder:text-sage-500 focus:border-sage-400 focus:bg-white dark:border-sage-700 dark:bg-sage-900/92 dark:text-sand-50 dark:placeholder:text-sand-50/58 dark:focus:border-sage-500 dark:focus:bg-sage-900"
        placeholder="Email address"
        type="email"
        autoComplete="email"
        value={email}
        onChange={(event) => setEmail(event.target.value)}
      />
      <input
        className="w-full rounded-[1.5rem] border border-sage-200 bg-sage-50/75 px-4 py-4 text-sm text-sage-950 outline-none transition placeholder:text-sage-500 focus:border-sage-400 focus:bg-white dark:border-sage-700 dark:bg-sage-900/92 dark:text-sand-50 dark:placeholder:text-sand-50/58 dark:focus:border-sage-500 dark:focus:bg-sage-900"
        placeholder="Password"
        type="password"
        autoComplete="current-password"
        value={password}
        onChange={(event) => setPassword(event.target.value)}
      />
      {error ? <p className="text-sm text-coral-700 dark:text-coral-200">{error}</p> : null}
      <Button className="w-full" disabled={loading} type="submit">
        {loading ? "Signing in..." : "Sign in to dashboard"}
      </Button>
    </form>
  );
}
