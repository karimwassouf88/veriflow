"use client";
import { useState } from "react";
import type { PolicySearchResponse } from "@/lib/types";

export default function PolicySearchBox() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<PolicySearchResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setResult(null);
    const res = await fetch("/api/policy-search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    setLoading(false);
    if (res.ok) setResult(await res.json());
  }

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. What's the approval threshold for a $15,000 purchase?"
          className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
        >
          {loading ? "Searching..." : "Ask"}
        </button>
      </form>

      {result && (
        <div className="space-y-4">
          <div
            className={`rounded-lg border p-5 ${result.answerable ? "border-slate-200 bg-white" : "border-amber-200 bg-amber-50"}`}
          >
            <p className="text-sm text-slate-800">{result.answer}</p>
            {!result.answerable && (
              <p className="mt-2 text-xs text-amber-700">
                Not confidently answerable from ingested policy documents.
              </p>
            )}
          </div>
          {result.sources.length > 0 && (
            <div>
              <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-blue-500">
                Sources
              </h4>
              <div className="space-y-2">
                {result.sources.map((s, i) => (
                  <div
                    key={i}
                    className="rounded-md border border-slate-200 bg-slate-50 p-3 text-xs text-blue-600"
                  >
                    <span className="font-medium text-slate-800">
                      {s.filename}
                    </span>{" "}
                    · chunk {s.chunk_index} · relevance{" "}
                    {s.rerank_score.toFixed(2)}
                    <p className="mt-1 text-blue-500">{s.text}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
