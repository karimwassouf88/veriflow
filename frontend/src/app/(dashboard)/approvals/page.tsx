import { backendFetch } from "@/lib/backend";
import type { ApprovalWithDocument } from "@/lib/types";
import ApprovalQueue from "@/components/ApprovalQueue";

export default async function ApprovalsPage() {
  const [approvalsRes, meRes] = await Promise.all([
    backendFetch("/api/v1/approvals?pending_only=true"),
    backendFetch("/api/v1/auth/me"),
  ]);
  const approvals: ApprovalWithDocument[] = approvalsRes.ok
    ? await approvalsRes.json()
    : [];
  const me = meRes.ok ? await meRes.json() : null;
  const canDecide = me ? ["admin", "approver"].includes(me.role) : false;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900">
          Approval Queue
        </h2>
        <p className="mt-1 text-sm text-blue-500">
          Invoices routed here need a human decision before payment.
        </p>
      </div>
      <ApprovalQueue approvals={approvals} canDecide={canDecide} />
    </div>
  );
}
