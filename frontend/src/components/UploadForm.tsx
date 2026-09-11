"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

const DOC_TYPES = ["invoice", "purchase_order", "contract", "policy"];

export default function UploadForm() {
  const [docType, setDocType] = useState("invoice");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("doc_type", docType);
    formData.append("file", file);

    const res = await fetch("/api/documents/upload", {
      method: "POST",
      body: formData,
    });
    setUploading(false);

    if (!res.ok) {
      setError("Upload failed — check the file is a valid PDF.");
      return;
    }
    setFile(null);
    router.refresh();
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-wrap items-end gap-3 rounded-lg border border-slate-200 bg-white p-4"
    >
      <div className="space-y-1">
        <label className="block text-xs font-medium text-blue-600">
          Document type
        </label>
        <select
          value={docType}
          onChange={(e) => setDocType(e.target.value)}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm"
        >
          {DOC_TYPES.map((t) => (
            <option key={t} value={t}>
              {t.replace("_", " ")}
            </option>
          ))}
        </select>
      </div>
      <div className="space-y-1">
        <label className="block text-xs font-medium text-blue-600">
          PDF file
        </label>
        <input
          type="file"
          accept="application/pdf"
          required
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="text-sm text-slate-900"
        />
      </div>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <button
        type="submit"
        disabled={uploading || !file}
        className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
      >
        {uploading ? "Uploading..." : "Upload"}
      </button>
    </form>
  );
}
