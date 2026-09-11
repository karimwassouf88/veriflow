"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import type { ApprovalWithDocument } from "@/lib/types";

export default function ApprovalQueue({
  approvals,
  canDecide,
}: {
  approvals: ApprovalWithDocument[];
  canDecide: boolean;
}) {
  const [comments, setComments] = useState<Record<string, string>>({});
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const router = useRouter();

  async function decide(id: string, decision: "approved" | "rejected") {
    setLoadingId(id);
    await fetch(`/api/approvals/${id}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision, comment: comments[id] || null }),
    });
    setLoadingId(null);
    router.refresh();
  }

  if (approvals.length === 0) {
    return (
      <p className="rounded-lg border border-slate-200 bg-white p-8 text-center text-sm text-blue-400">
        No pending approvals.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {approvals.map((a) => (
        <div
          key={a.id}
          className="rounded-lg border border-slate-200 bg-white p-5"
        >
          <div className="mb-2 flex items-center justify-between">
            <Link
              href={`/documents/${a.document_id}`}
              className="font-medium text-slate-900 hover:underline"
            >
              {a.document_filename ?? "Unknown document"}
            </Link>
            <span className="text-xs uppercase tracking-wide text-blue-400">
              {a.document_type?.replace("_", " ")}
            </span>
          </div>
          <p className="mb-3 text-sm text-blue-700">{a.routing_reason}</p>
          {canDecide ? (
            <div className="flex flex-wrap items-center gap-2">
              <input
                type="text"
                placeholder="Optional comment"
                value={comments[a.id] ?? ""}
                onChange={(e) =>
                  setComments((prev) => ({ ...prev, [a.id]: e.target.value }))
                }
                className="text-slate-900 flex-1 min-w-45 rounded-md border border-slate-300 px-3 py-1.5 text-sm"
              />
              <button
                onClick={() => decide(a.id, "approved")}
                disabled={loadingId === a.id}
                className="rounded-md bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
              >
                Approve
              </button>
              <button
                onClick={() => decide(a.id, "rejected")}
                disabled={loadingId === a.id}
                className="rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
              >
                Reject
              </button>
            </div>
          ) : (
            <p className="text-xs text-blue-400">
              Only Approvers and Admins can decide on this queue.
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
