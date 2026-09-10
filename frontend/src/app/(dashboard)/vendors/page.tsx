import { backendFetch } from "@/lib/backend";
import type { Vendor, PurchaseOrder } from "@/lib/types";
import VendorPoManager from "@/components/VendorPoManager";

export default async function VendorsPage() {
  const [vendorsRes, posRes] = await Promise.all([
    backendFetch("/api/v1/vendors"),
    backendFetch("/api/v1/purchase-orders"),
  ]);
  const vendors: Vendor[] = vendorsRes.ok ? await vendorsRes.json() : [];
  const purchaseOrders: PurchaseOrder[] = posRes.ok ? await posRes.json() : [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900">
          Vendors & Purchase Orders
        </h2>
        <p className="mt-1 text-sm text-blue-500">
          Master data used by the validation agent.
        </p>
      </div>
      <VendorPoManager vendors={vendors} purchaseOrders={purchaseOrders} />
    </div>
  );
}
