import Link from "next/link";

import { LoginForm } from "@/components/auth/login-form";
import { Card } from "@/components/ui/card";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-5 py-10">
      <Card className="grid w-full max-w-5xl overflow-hidden lg:grid-cols-[0.95fr_1.05fr]">
        <div className="bg-gradient-to-br from-sage-900 via-sage-800 to-sage-700 p-8 text-white sm:p-10">
          <p className="text-xs uppercase tracking-[0.28em] text-white/60">Safebond</p>
          <h1 className="mt-6 font-serif-display text-4xl">
            Welcome back to your calm operations layer.
          </h1>
          <p className="mt-5 max-w-md text-sm leading-7 text-white/78">
            Continue from your last session, review emotional trends, and access memory-grounded support conversations.
          </p>
        </div>
        <div className="p-8 sm:p-10">
          <div className="mx-auto max-w-md">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sage-700/72">
              Sign in
            </p>
            <h2 className="mt-3 font-serif-display text-3xl text-ink">
              Enter your workspace
            </h2>
            <LoginForm />
            <p className="mt-6 text-sm text-sage-800/74">
              New to Safebond?{" "}
              <Link className="font-semibold text-sage-900" href="/signup">
                Create an account
              </Link>
            </p>
          </div>
        </div>
      </Card>
    </main>
  );
}
