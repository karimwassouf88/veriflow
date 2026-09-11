"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import type { Vendor, PurchaseOrder } from "@/lib/types";

export default function VendorPoManager({
  vendors,
  purchaseOrders,
}: {
  vendors: Vendor[];
  purchaseOrders: PurchaseOrder[];
}) {
  const router = useRouter();
  const [vendorName, setVendorName] = useState("");
  const [vendorTaxId, setVendorTaxId] = useState("");
  const [poNumber, setPoNumber] = useState("");
  const [poVendorId, setPoVendorId] = useState("");
  const [poAmount, setPoAmount] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function addVendor(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const res = await fetch("/api/vendors", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: vendorName, tax_id: vendorTaxId || null }),
    });
    setLoading(false);
    if (!res.ok) {
      setError("Could not create vendor.");
      return;
    }
    setVendorName("");
    setVendorTaxId("");
    router.refresh();
  }

  async function addPo(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const res = await fetch("/api/purchase-orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        po_number: poNumber,
        vendor_id: poVendorId,
        amount: parseFloat(poAmount),
      }),
    });
    setLoading(false);
    if (!res.ok) {
      setError(
        "Could not create purchase order — check the PO number isn't already used.",
      );
      return;
    }
    setPoNumber("");
    setPoVendorId("");
    setPoAmount("");
    router.refresh();
  }

  return (
    <div className="grid gap-8 md:grid-cols-2">
      <section className="space-y-4">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-blue-500">
          Vendors
        </h3>
        <form
          onSubmit={addVendor}
          className="space-y-2 rounded-lg border border-slate-200 bg-white p-4"
        >
          <input
            required
            placeholder="Vendor name"
            value={vendorName}
            onChange={(e) => setVendorName(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900"
          />
          <input
            placeholder="Tax ID (optional)"
            value={vendorTaxId}
            onChange={(e) => setVendorTaxId(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900"
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
          >
            Add vendor
          </button>
        </form>
        <div className="divide-y divide-slate-100 rounded-lg border border-slate-200 bg-white">
          {vendors.map((v) => (
            <div key={v.id} className="px-4 py-2 text-sm text-blue-700">
              {v.name}{" "}
              {v.tax_id && <span className="text-blue-400">· {v.tax_id}</span>}
            </div>
          ))}
          {vendors.length === 0 && (
            <p className="px-4 py-4 text-sm text-blue-400">No vendors yet.</p>
          )}
        </div>
      </section>

      <section className="space-y-4">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-blue-500">
          Purchase Orders
        </h3>
        <form
          onSubmit={addPo}
          className="space-y-2 rounded-lg border border-slate-200 bg-white p-4"
        >
          <input
            required
            placeholder="PO number"
            value={poNumber}
            onChange={(e) => setPoNumber(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900"
          />
          <select
            required
            value={poVendorId}
            onChange={(e) => setPoVendorId(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          >
            <option value="">Select vendor...</option>
            {vendors.map((v) => (
              <option key={v.id} value={v.id}>
                {v.name}
              </option>
            ))}
          </select>
          <input
            required
            type="number"
            step="0.01"
            placeholder="Amount"
            value={poAmount}
            onChange={(e) => setPoAmount(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900"
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
          >
            Add purchase order
          </button>
        </form>
        <div className="divide-y divide-slate-100 rounded-lg border border-slate-200 bg-white">
          {purchaseOrders.map((po) => (
            <div key={po.id} className="px-4 py-2 text-sm text-slate-700">
              {po.po_number} · ${po.amount.toFixed(2)} ·{" "}
              <span className="text-blue-400">{po.status}</span>
            </div>
          ))}
          {purchaseOrders.length === 0 && (
            <p className="px-4 py-4 text-sm text-blue-400">
              No purchase orders yet.
            </p>
          )}
        </div>
      </section>

      {error && <p className="text-sm text-red-600 md:col-span-2">{error}</p>}
    </div>
  );
}
