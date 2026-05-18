import { AuthGuard } from "@/components/providers/auth-guard";
import { ProfileGate } from "@/components/providers/profile-gate";
import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";

export default function WorkspaceLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <AuthGuard>
      <ProfileGate>
        <div className="min-h-screen px-4 py-4 sm:px-6 lg:px-8">
          <div className="mx-auto grid max-w-7xl gap-4 lg:grid-cols-[280px_1fr]">
            <Sidebar />
            <div className="space-y-4">
              <Topbar />
              {children}
            </div>
          </div>
        </div>
      </ProfileGate>
    </AuthGuard>
  );
}
