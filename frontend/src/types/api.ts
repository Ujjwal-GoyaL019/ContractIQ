export interface Supplier {
  id: string;
  code: string;
  name: string;
  contact_email?: string;
  contact_phone?: string;
  country: string;
  base_lead_time_days: number;
  reliability_score: number;
  quality_score: number;
  disruption_risk_score: number;
  payment_terms: string;
  status: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  product_count?: number;
  document_count?: number;
}

export interface Product {
  id: string;
  sku: string;
  name: string;
  description?: string;
  category: string;
  unit_of_measure: string;
  unit_cost: number;
  unit_price: number;
  min_safety_stock: number;
  target_service_level: number;
  lead_time_days: number;
  supplier_id?: string;
  supplier?: Supplier;
  current_stock: number;
  days_of_supply: number;
  stockout_risk_score: number;
  created_at: string;
  updated_at: string;
}

export interface InventoryItem {
  id: string;
  product_id: string;
  warehouse_code: string;
  current_stock: number;
  allocated_stock: number;
  incoming_stock: number;
  available_stock: number;
  reorder_point: number;
  reorder_quantity: number;
  stockout_risk_score: number;
  days_of_supply: number;
  urgency_status: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'HEALTHY' | 'OVERSTOCKED';
  product?: Product;
  created_at: string;
  updated_at: string;
}

export interface ForecastPoint {
  date: string;
  predicted_demand: number;
  lower_bound: number;
  upper_bound: number;
  actual_demand?: number;
}

export interface ForecastResponse {
  sku: string;
  product_name: string;
  model_type: string;
  horizon_days: number;
  generated_at: string;
  mape?: number;
  rmse?: number;
  mae?: number;
  historical_points: ForecastPoint[];
  forecast_points: ForecastPoint[];
  total_forecasted_demand: number;
  average_daily_demand: number;
}

export interface BacktestMetric {
  model_type: string;
  mape: number;
  rmse: number;
  mae: number;
  wape: number;
  sample_count: number;
}

export interface RiskBreakdown {
  stockout_risk_score: number;
  supplier_disruption_risk: number;
  composite_risk_score: number;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface SKURiskItem {
  sku: string;
  product_name: string;
  category: string;
  supplier_name: string;
  supplier_country: string;
  current_stock: number;
  incoming_stock: number;
  lead_time_days: number;
  forecasted_demand_lead_time: number;
  safety_stock: number;
  projected_net_stock: number;
  days_until_stockout: number;
  reorder_recommended_units: number;
  financial_impact_risk: number;
  risk_breakdown: RiskBreakdown;
  risk_reasons: string[];
  suggested_action: string;
}

export interface RiskSummaryResponse {
  total_skus: number;
  critical_risk_count: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  total_capital_at_risk: number;
  average_supplier_reliability: number;
  items: SKURiskItem[];
}

export interface DocumentMetadata {
  id: string;
  title: string;
  filename: string;
  doc_type: string;
  supplier_id?: string;
  supplier_name?: string;
  chunk_count: number;
  file_size_bytes: number;
  created_at: string;
  summary?: string;
}

export interface Citation {
  doc_id: string;
  document_title: string;
  supplier_name?: string;
  page_number?: number;
  snippet: string;
  score: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations?: Citation[];
  risk_flags_detected?: string[];
  suggested_followups?: string[];
}
