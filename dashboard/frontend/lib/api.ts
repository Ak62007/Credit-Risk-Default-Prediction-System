import type {
  DataHealthResponse,
  DriftHistoryResponse,
  DriftSummaryResponse,
  FeatureDriftResponse,
  HealthResponse,
  OverviewResponse,
  PredictionDetailResponse,
  PredictionListFilters,
  PredictionListResponse,
  ScoreDistributionResponse,
  TrafficResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8001";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} on ${path}: ${body}`);
  }
  return res.json() as Promise<T>;
}

function qs(params: Record<string, string | number | undefined>): string {
  const entries = Object.entries(params).filter(([, v]) => v !== undefined && v !== "");
  if (entries.length === 0) return "";
  return "?" + entries.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`).join("&");
}

export const api = {
  health: () => get<HealthResponse>("/api/health"),
  overview: () => get<OverviewResponse>("/api/overview"),
  trafficHourly: (hours = 48) => get<TrafficResponse>(`/api/traffic/hourly${qs({ hours })}`),
  scoreDistribution: (bins = 30) => get<ScoreDistributionResponse>(`/api/scores/distribution${qs({ bins })}`),
  driftSummary: () => get<DriftSummaryResponse>("/api/drift/summary"),
  featureDrift: (feature: string) => get<FeatureDriftResponse>(`/api/drift/feature/${encodeURIComponent(feature)}`),
  driftHistory: (feature: string, days = 30) =>
    get<DriftHistoryResponse>(`/api/drift/history${qs({ feature, days })}`),
  predictions: (filters: PredictionListFilters = {}) =>
    get<PredictionListResponse>(`/api/predictions${qs({ ...filters })}`),
  prediction: (requestId: string) => get<PredictionDetailResponse>(`/api/predictions/${requestId}`),
  dataHealth: () => get<DataHealthResponse>("/api/data-health"),
};
