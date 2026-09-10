import { backendFetch } from "@/lib/backend";
import { redirect } from "next/navigation";
import LogoutButton from "@/components/LogoutButton";
import NavLinks from "@/components/NavLinks";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const res = await backendFetch("/api/v1/auth/me");
  if (!res.ok) redirect("/login");
  const user = await res.json();

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="w-60 border-r border-slate-200 bg-white p-4">
        <h1 className="mb-6 text-lg font-semibold text-slate-900">Veriflow</h1>
        <NavLinks role={user.role} />
        <div className="mt-8 border-t border-slate-200 pt-4">
          <p className="text-xs text-blue-500">{user.email}</p>
          <p className="text-xs font-medium uppercase tracking-wide text-blue-500">
            {user.role}
          </p>
          <LogoutButton />
        </div>
      </aside>
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}
