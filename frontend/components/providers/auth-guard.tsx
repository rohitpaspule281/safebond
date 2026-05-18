"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/providers/auth-provider";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { initialized, token } = useAuth();

  useEffect(() => {
    if (initialized && !token) {
      router.replace("/login");
    }
  }, [initialized, token, router]);

  if (!initialized || !token) {
    return (
      <div className="flex min-h-screen items-center justify-center px-6">
        <div className="rounded-[2rem] border border-white/70 bg-white/80 px-8 py-6 text-sm text-sage-800 shadow-soft">
          Loading your Safebond workspace...
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
