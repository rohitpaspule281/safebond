import { IntakeForm } from "@/components/onboarding/intake-form";
import { Card } from "@/components/ui/card";

export default function OnboardingPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-5 py-10">
      <Card className="w-full max-w-4xl p-8 sm:p-10">
        <div className="max-w-3xl">
          <p className="text-xs uppercase tracking-[0.28em] text-sage-700/72">
            Wellness Intake
          </p>
          <h1 className="mt-4 font-serif-display text-4xl text-ink">
            Let Safebond understand your emotional landscape before the first session.
          </h1>
          <p className="mt-4 text-sm leading-7 text-sage-800/78">
            This intake uses a structured psychological check-in, support-planning prompts, and a trusted-contact step so the system can respond more responsibly and with better context.
          </p>
        </div>
        <div className="mt-10">
          <IntakeForm />
        </div>
      </Card>
    </main>
  );
}
