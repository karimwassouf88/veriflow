import { backendFetch } from "@/lib/backend";
import type { Document } from "@/lib/types";
import Link from "next/link";
import UploadForm from "@/components/UploadForm";

const STATUS_COLORS: Record<string, string> = {
  uploaded: "bg-slate-100 text-slate-700",
  processing: "bg-blue-100 text-blue-700",
  extracted: "bg-blue-100 text-blue-700",
  extraction_failed: "bg-red-100 text-red-700",
  validated: "bg-blue-100 text-blue-700",
  validation_error: "bg-red-100 text-red-700",
  compliance_checked: "bg-emerald-100 text-emerald-700",
  compliance_error: "bg-red-100 text-red-700",
  rag_ingested: "bg-emerald-100 text-emerald-700",
  rag_ingestion_failed: "bg-red-100 text-red-700",
};

export default async function DocumentsPage() {
  const res = await backendFetch("/api/v1/documents");
  const documents: Document[] = res.ok ? await res.json() : [];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900">Documents</h2>
        <p className="mt-1 text-sm text-blue-500">
          Upload an invoice or policy document to run through the pipeline.
        </p>
      </div>

      <UploadForm />

      <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-blue-500">
            <tr>
              <th className="px-4 py-3">Filename</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Uploaded</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr
                key={doc.id}
                className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
              >
                <td className="px-4 py-3">
                  <Link
                    href={`/documents/${doc.id}`}
                    className="font-medium text-slate-900 hover:underline"
                  >
                    {doc.original_filename}
                  </Link>
                </td>
                <td className="px-4 py-3 capitalize text-blue-600">
                  {doc.type.replace("_", " ")}
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`rounded-full px-2 py-1 text-xs font-medium ${STATUS_COLORS[doc.ingestion_status] ?? "bg-slate-100 text-slate-700"}`}
                  >
                    {doc.ingestion_status.replace(/_/g, " ")}
                  </span>
                </td>
                <td className="px-4 py-3 text-blue-500">
                  {new Date(doc.created_at).toLocaleString()}
                </td>
              </tr>
            ))}
            {documents.length === 0 && (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-blue-400">
                  No documents uploaded yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
