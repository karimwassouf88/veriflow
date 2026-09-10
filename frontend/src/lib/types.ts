export interface Document {
  id: string;
  type: "invoice" | "purchase_order" | "contract" | "policy";
  original_filename: string;
  file_size: number;
  content_hash: string;
  ingestion_status: string;
  uploaded_by: string;
  created_at: string;
}
export interface ExtractionField {
  field_name: string;
  extracted_value: string | null;
  confidence_score: number;
  model_version: string;
}
export interface ExtractionResult {
  document_id: string;
  ingestion_status: string;
  fields: ExtractionField[];
}
export interface ValidationResult {
  document_id: string;
  vendor_status: string;
  po_status: string;
  amount_difference_pct: number | null;
  summary: string;
  passed: boolean;
}
export interface ComplianceResult {
  document_id: string;
  compliant: boolean;
  required_approval_level: string;
  reasoning: string;
  policy_sources: string | null;
  model_version: string;
  created_at: string;
}
export interface Approval {
  id: string;
  document_id: string;
  decision: string;
  routing_reason: string;
  approver_id: string | null;
  comment: string | null;
  decided_at: string | null;
  created_at: string;
}

export interface ApprovalWithDocument extends Approval {
  document_filename: string | null;
  document_type: string | null;
}

export interface Vendor {
  id: string;
  name: string;
  tax_id: string | null;
  is_active: boolean;
}
export interface PurchaseOrder {
  id: string;
  po_number: string;
  vendor_id: string;
  amount: number;
  status: string;
}
export interface PolicySearchSource {
  document_id: string;
  filename: string;
  chunk_index: number;
  text: string;
  rerank_score: number;
}
export interface PolicySearchResponse {
  query: string;
  answer: string;
  answerable: boolean;
  sources: PolicySearchSource[];
}
