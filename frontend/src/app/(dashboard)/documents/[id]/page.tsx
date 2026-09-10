import { backendFetch } from "@/lib/backend";
import { notFound } from "next/navigation";
import type {
  Document,
  ExtractionResult,
  ValidationResult,
  ComplianceResult,
  Approval,
} from "@/lib/types";
import ProcessButton from "@/components/ProcessButton";
import ConfidenceBar from "@/components/ConfidenceBar";

async function fetchOrNull<T>(path: string): Promise<T | null> {
  const res = await backendFetch(path);
  if (!res.ok) return null;
  return res.json();
}

export default async function DocumentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const doc = await fetchOrNull<Document>(`/api/v1/documents/${id}`);
  if (!doc) notFound();

  const [extraction, validation, compliance, approval] = await Promise.all([
    fetchOrNull<ExtractionResult>(`/api/v1/documents/${id}/extraction`),
    fetchOrNull<ValidationResult>(`/api/v1/documents/${id}/validation`),
    fetchOrNull<ComplianceResult>(`/api/v1/documents/${id}/compliance`),
    fetchOrNull<Approval>(`/api/v1/documents/${id}/approval`),
  ]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900">
            {doc.original_filename}
          </h2>
          <p className="text-sm capitalize text-blue-500">
            {doc.type.replace("_", " ")} ·{" "}
            {doc.ingestion_status.replace(/_/g, " ")}
          </p>
        </div>
        {doc.type === "invoice" && <ProcessButton documentId={doc.id} />}
      </div>

      {extraction && extraction.fields.length > 0 && (
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-blue-500">
            Extraction
          </h3>
          <div className="space-y-3">
            {extraction.fields.map((f) => (
              <div key={f.field_name} className="flex items-center gap-4">
                <span className="w-32 shrink-0 text-sm capitalize text-blue-600">
                  {f.field_name.replace(/_/g, " ")}
                </span>
                <span className="flex-1 text-sm font-medium text-slate-900">
                  {f.extracted_value ?? <em className="text-blue-400">null</em>}
                </span>
                <ConfidenceBar score={f.confidence_score} />
              </div>
            ))}
          </div>
        </section>
      )}

      {validation && (
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <div className="mb-2 flex items-center gap-2">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-blue-500">
              Validation
            </h3>
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${validation.passed ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}`}
            >
              {validation.passed ? "Passed" : "Flagged"}
            </span>
          </div>
          <p className="text-sm text-blue-700">{validation.summary}</p>
        </section>
      )}

      {compliance && (
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <div className="mb-2 flex items-center gap-2">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-blue-500">
              Compliance
            </h3>
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${compliance.compliant ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}`}
            >
              {compliance.compliant ? "Compliant" : "Flagged"} ·{" "}
              {compliance.required_approval_level} approval
            </span>
          </div>
          <p className="text-sm text-blue-700">{compliance.reasoning}</p>
        </section>
      )}

      {approval && (
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <div className="mb-2 flex items-center gap-2">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-blue-500">
              Approval
            </h3>
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                approval.decision === "approved" ||
                approval.decision === "auto_approved"
                  ? "bg-emerald-100 text-emerald-700"
                  : approval.decision === "rejected"
                    ? "bg-red-100 text-red-700"
                    : "bg-amber-100 text-amber-700"
              }`}
            >
              {approval.decision.replace(/_/g, " ")}
            </span>
          </div>
          <p className="text-sm text-blue-700">{approval.routing_reason}</p>
        </section>
      )}

      {!extraction && (
        <p className="text-sm text-blue-400">
          Not processed yet — run the pipeline above.
        </p>
      )}
    </div>
  );
}
