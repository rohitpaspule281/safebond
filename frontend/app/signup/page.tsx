import Link from "next/link";

import { SignupForm } from "@/components/auth/signup-form";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function SignupPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-5 py-10">
      <Card className="w-full max-w-3xl p-8 sm:p-10">
        <div className="max-w-2xl">
          <p className="text-xs uppercase tracking-[0.28em] text-sage-700/72">
            Create your account
          </p>
          <h1 className="mt-4 font-serif-display text-4xl text-ink">
            Build a protected space for reflective, safety-aware support.
          </h1>
          <p className="mt-4 text-sm leading-7 text-sage-800/76">
            Safebond uses emotion analysis, contextual memory, and explicit safety boundaries. It does not replace licensed mental health professionals or emergency care.
          </p>
        </div>
        <SignupForm />
        <div className="mt-4">
          <Link href="/login">
            <Button variant="secondary">I already have an account</Button>
          </Link>
        </div>
      </Card>
    </main>
  );
}
