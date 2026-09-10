import PolicySearchBox from "@/components/PolicySearchBox";

export default function PolicySearchPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900">Policy Search</h2>
        <p className="mt-1 text-sm text-blue-500">
          Ask a question about ingested company policy documents.
        </p>
      </div>
      <PolicySearchBox />
    </div>
  );
}
