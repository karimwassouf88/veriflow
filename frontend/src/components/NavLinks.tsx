"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  {
    href: "/documents",
    label: "Documents",
    roles: ["admin", "clerk", "approver", "auditor"],
  },
  { href: "/approvals", label: "Approvals", roles: ["admin", "approver"] },
  {
    href: "/policy-search",
    label: "Policy Search",
    roles: ["admin", "clerk", "approver", "auditor"],
  },
  { href: "/vendors", label: "Vendors", roles: ["admin"] },
];

export default function NavLinks({ role }: { role: string }) {
  const pathname = usePathname();
  return (
    <nav className="space-y-1">
      {LINKS.filter((l) => l.roles.includes(role)).map((link) => (
        <Link
          key={link.href}
          href={link.href}
          className={`block rounded-md px-3 py-2 text-sm font-medium ${
            pathname.startsWith(link.href)
              ? "bg-slate-900 text-white"
              : "text-blue-600 hover:bg-slate-100"
          }`}
        >
          {link.label}
        </Link>
      ))}
    </nav>
  );
}
