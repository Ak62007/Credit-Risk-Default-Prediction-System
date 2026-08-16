"use client";

import Link from "next/link";
import { api } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { DataView } from "@/components/ui/DataView";
import { EmptyState } from "@/components/ui/Spinner";
import { Badge } from "@/components/ui/Badge";

function NullRateBar({ feature, rate }: { feature: string; rate: number }) {
  return (
    <div className="flex items-center gap-3">
      <span className="w-56 truncate text-xs text-text-secondary">{feature}</span>
      <div className="h-2 flex-1 overflow-hidden rounded-full bg-surface-3">
        <div
          className="h-full rounded-full"
          style={{
            width: `${Math.max(2, rate * 100)}%`,
            background: rate > 0.6 ? "var(--status-critical)" : rate > 0.3 ? "var(--status-warning)" : "var(--series-1)",
          }}
        />
      </div>
      <span className="w-12 text-right text-xs tabular-nums text-text-muted">{(rate * 100).toFixed(0)}%</span>
    </div>
  );
}

export default function DataHealthPage() {
  const health = useApi(() => api.dataHealth(), []);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold text-text-primary">Data Health</h1>
        <p className="mt-1 text-sm text-text-secondary">Data-quality signals worth knowing about before trusting the numbers elsewhere.</p>
      </div>

      <DataView
        data={health.data}
        loading={health.loading}
        error={health.error}
        render={(d) => (
          <>
            {d.traffic_note && (
              <Card className="bg-[color-mix(in_oklab,var(--status-warning)_8%,var(--surface-1))]">
                <CardBody className="pb-4 pt-4">
                  <p className="text-xs text-text-secondary">{d.traffic_note}</p>
                </CardBody>
              </Card>
            )}

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <Card>
                <CardHeader title="Null rates" subtitle="'Months since last X' fields -- nulls here usually mean the event never happened" />
                <CardBody className="flex flex-col gap-2.5">
                  {Object.entries(d.null_rates).map(([feature, rate]) => (
                    <NullRateBar key={feature} feature={feature} rate={rate} />
                  ))}
                </CardBody>
              </Card>

              <Card>
                <CardHeader
                  title="Duplicate signals"
                  subtitle="Repeated payloads or timestamps that would bias distribution stats"
                />
                <CardBody className="flex flex-col gap-3">
                  <div className="flex justify-between border-b border-border pb-2 text-sm">
                    <span className="text-text-secondary">Duplicate payload groups</span>
                    <span className="tabular-nums text-text-primary">{d.duplicate_payload_groups}</span>
                  </div>
                  <div className="flex justify-between border-b border-border pb-2 text-sm">
                    <span className="text-text-secondary">Extra rows from duplicate payloads</span>
                    <span className="tabular-nums text-text-primary">{d.duplicate_payload_extra_rows}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-text-secondary">Duplicate logged_at timestamps</span>
                    <span className="tabular-nums text-text-primary">{d.duplicate_logged_at_count}</span>
                  </div>
                </CardBody>
              </Card>
            </div>

            <Card>
              <CardHeader title="Singleton / rare categories" subtitle={`≤5 rows -- unstable for any %-based chart`} />
              <CardBody>
                {d.singleton_categories.length === 0 ? (
                  <EmptyState message="No rare categories detected." />
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {d.singleton_categories.map((c) => (
                      <Badge key={`${c.feature}-${c.category}`}>
                        {c.feature}={c.category} ({c.count})
                      </Badge>
                    ))}
                  </div>
                )}
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Outlier values" subtitle="Rows outside normal domain ranges (dti, pub_rec, delinq_2yrs, revol_util)" />
              <CardBody>
                {d.outliers.length === 0 ? (
                  <EmptyState message="No outliers flagged." />
                ) : (
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-border text-xs uppercase tracking-wide text-text-muted">
                        <th className="py-2 font-medium">Request</th>
                        <th className="py-2 font-medium">Feature</th>
                        <th className="py-2 font-medium">Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {d.outliers.map((o, i) => (
                        <tr key={i} className="border-b border-border last:border-0">
                          <td className="py-2">
                            <Link href={`/predictions/${o.request_id}`} className="text-series-1 hover:underline">
                              {o.request_id.slice(0, 8)}&hellip;
                            </Link>
                          </td>
                          <td className="py-2 text-text-secondary">{o.feature}</td>
                          <td className="py-2 tabular-nums text-text-secondary">{o.value}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Known limitations" />
              <CardBody className="flex flex-col gap-1.5 text-xs text-text-muted">
                <p>&bull; No ground-truth default labels exist yet -- this dashboard cannot show accuracy, AUC, or calibration.</p>
                <p>&bull; prediction_logs has no model-version column, so a served-model change can&apos;t be attributed programmatically.</p>
                <p>&bull; Traffic reflects scripted load-test bursts, not steady production volume.</p>
              </CardBody>
            </Card>
          </>
        )}
      />
    </div>
  );
}
