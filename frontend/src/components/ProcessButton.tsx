"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function ProcessButton({ documentId }: { documentId: string }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function handleClick() {
    setLoading(true);
    setError(null);
    const res = await fetch(`/api/documents/${documentId}/process`, {
      method: "POST",
    });
    setLoading(false);
    if (!res.ok) {
      setError("Pipeline failed to run.");
      return;
    }
    router.refresh();
  }

  return (
    <div className="text-right">
      <button
        onClick={handleClick}
        disabled={loading}
        className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
      >
        {loading ? "Running pipeline..." : "Run Full Pipeline"}
      </button>
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}
