"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/providers/auth-provider";
import { api } from "@/lib/api";

export function ProfileGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { token, signOut } = useAuth();
  const [checking, setChecking] = useState(true);
  const loadedTokenRef = useRef<string | null>(null);

  useEffect(() => {
    if (!token) {
      return;
    }
    if (loadedTokenRef.current === token) {
      setChecking(false);
      return;
    }

    let cancelled = false;
    loadedTokenRef.current = token;
    setChecking(true);

    api.profileStatus(token)
      .then((status) => {
        if (cancelled) {
          return;
        }
        if (!status.completed) {
          router.replace("/onboarding");
          return;
        }
        setChecking(false);
      })
      .catch(() => {
        if (!cancelled) {
          signOut();
          router.replace("/login");
          setChecking(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [router, signOut, token]);

  if (checking) {
    return (
      <div className="flex min-h-screen items-center justify-center px-6">
        <div className="rounded-[2rem] border border-white/70 bg-white/80 px-8 py-6 text-sm text-sage-800 shadow-soft">
          Checking your wellness setup...
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
