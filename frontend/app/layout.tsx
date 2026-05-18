import type { Metadata } from "next";

import { AuthProvider } from "@/components/providers/auth-provider";
import { ThemeProvider } from "@/components/providers/theme-provider";

import "./globals.css";

export const metadata: Metadata = {
  title: "Safebond",
  description:
    "Emotion-aware AI support for mental wellness with memory, safety, and analytics."
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="font-sans-body antialiased">
        <ThemeProvider>
          <AuthProvider>{children}</AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
