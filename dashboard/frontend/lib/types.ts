export interface HealthResponse {
  status: "ok" | "degraded";
  db_reachable: boolean;
  reference_loaded: boolean;
  last_live_load_at: number | null;
}

export interface OverviewResponse {
  total_logged: number;
  requests_last_24h: number;
  requests_last_1h: number;
  pred_split: Record<string, number>;
  prob_percentiles: { p50: number; p90: number; p95: number; p99: number; max: number };
  current_threshold: number;
  model_artifact: string;
  logged_at_range: { min: string | null; max: string | null };
  model_version_note: string;
}

export interface TrafficBucket {
  hour_start: string;
  count: number;
}

export interface TrafficResponse {
  buckets: TrafficBucket[];
  is_bursty: boolean;
  note: string | null;
}

export interface ScoreBucket {
  range_start: number;
  range_end: number;
  count: number;
}

export interface ScoreDistributionResponse {
  buckets: ScoreBucket[];
  threshold: number;
  mean: number | null;
  median: number | null;
}

export type DriftLevel = "stable" | "moderate" | "significant";

export interface DriftFeatureSummary {
  feature: string;
  PSI: number;
  drift_level: DriftLevel;
}

export interface DriftSummaryResponse {
  counts: Record<DriftLevel, number>;
  top_features: DriftFeatureSummary[];
  all_features: DriftFeatureSummary[];
  reference_size: number;
  live_size: number;
  sample_size_warning: boolean;
  min_sample_threshold: number;
}

export interface NumericBucket {
  range_start: number | null;
  range_end: number | null;
  reference_pct: number;
  live_pct: number;
}

export interface FeatureDriftResponse {
  feature: string;
  psi: number;
  drift_level: DriftLevel;
  type: "numeric" | "categorical";
  buckets?: NumericBucket[];
  reference_missing_pct?: number;
  live_missing_pct?: number;
  reference_proportions?: Record<string, number>;
  live_proportions?: Record<string, number>;
  unseen_categories?: string[];
}

export interface DriftHistoryPoint {
  computed_at: string;
  psi: number;
  drift_level: DriftLevel;
}

export interface DriftHistoryResponse {
  feature: string;
  points: DriftHistoryPoint[];
  available: boolean;
}

export interface PredictionListRow {
  request_id: string;
  logged_at: string;
  pred: number;
  prob: number;
  purpose: string;
  addr_state: string;
  loan_amnt: number;
  annual_inc: number;
  dti: number;
}

export interface PredictionListResponse {
  total: number;
  rows: PredictionListRow[];
}

export interface PredictionDetailResponse {
  request_id: string;
  logged_at: string;
  issue_d: string | null;
  pred: number;
  prob: number;
  reason_codes: Record<string, number>;
  raw_input: Record<string, unknown>;
}

export interface PredictionListFilters {
  limit?: number;
  offset?: number;
  pred?: number;
  min_prob?: number;
  max_prob?: number;
  purpose?: string;
  addr_state?: string;
  date_from?: string;
  date_to?: string;
}

export interface SingletonCategory {
  feature: string;
  category: string;
  count: number;
}

export interface DataHealthOutlier {
  request_id: string;
  feature: string;
  value: number;
}

export interface DataHealthResponse {
  null_rates: Record<string, number>;
  singleton_categories: SingletonCategory[];
  duplicate_payload_groups: number;
  duplicate_payload_extra_rows: number;
  duplicate_logged_at_count: number;
  outliers: DataHealthOutlier[];
  traffic_note: string | null;
}
