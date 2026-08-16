"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { StatTile } from "@/components/ui/StatTile";
import { DataView } from "@/components/ui/DataView";
import { DriftBadge } from "@/components/ui/Badge";
import { Spinner, ErrorState, EmptyState } from "@/components/ui/Spinner";
import { PsiBarChart } from "@/components/charts/PsiBarChart";
import { NumericDistributionChart, CategoricalDistributionChart } from "@/components/charts/DistributionOverlayChart";
import { PsiTrendChart } from "@/components/charts/PsiTrendChart";

function FeatureDrillDown({ feature }: { feature: string }) {
  const detail = useApi(() => api.featureDrift(feature), [feature]);
  const history = useApi(() => api.driftHistory(feature, 30), [feature]);

  return (
    <div className="flex flex-col gap-5">
      <DataView
        data={detail.data}
        loading={detail.loading}
        error={detail.error}
        render={(d) => (
          <div>
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-medium text-text-primary">{d.feature}</h4>
                <p className="text-xs text-text-muted">reference (training data) vs. live traffic</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold tabular-nums text-text-primary">PSI {d.psi.toFixed(3)}</span>
                <DriftBadge level={d.drift_level} />
              </div>
            </div>
            <div className="mt-3">
              {d.type === "numeric" && d.buckets ? (
                <NumericDistributionChart buckets={d.buckets} />
              ) : d.reference_proportions && d.live_proportions ? (
                <CategoricalDistributionChart
                  referenceProportions={d.reference_proportions}
                  liveProportions={d.live_proportions}
                />
              ) : null}
            </div>
            {d.unseen_categories && d.unseen_categories.length > 0 && (
              <p className="mt-2 text-xs text-text-muted">
                Categories seen live but never in training: {d.unseen_categories.join(", ")}
              </p>
            )}
          </div>
        )}
      />

      <div>
        <h4 className="mb-2 text-sm font-medium text-text-primary">PSI over time</h4>
        {history.loading && <Spinner />}
        {history.error && <ErrorState message={history.error.message} />}
        {history.data && !history.data.available && (
          <EmptyState message="Drift history isn't set up yet -- needs the drift_snapshots table and background snapshot job." />
        )}
        {history.data?.available && history.data.points.length === 0 && (
          <EmptyState message="No snapshots recorded yet. Check back after the next scheduled run." />
        )}
        {history.data?.available && history.data.points.length > 0 && <PsiTrendChart points={history.data.points} />}
      </div>
    </div>
  );
}

export default function DriftPage() {
  const summary = useApi(() => api.driftSummary(), []);
  const [selected, setSelected] = useState<string | null>(null);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold text-text-primary">Drift Monitoring</h1>
        <p className="mt-1 text-sm text-text-secondary">
          Covariate shift (PSI) between the training reference set and live prediction traffic.
        </p>
      </div>

      <DataView
        data={summary.data}
        loading={summary.loading}
        error={summary.error}
        render={(d) => (
          <>
            {d.sample_size_warning && (
              <Card className="border-status-warning/40 bg-[color-mix(in_oklab,var(--status-warning)_8%,var(--surface-1))]">
                <CardBody className="pt-4 pb-4">
                  <p className="text-xs text-text-secondary">
                    Only {d.live_size} live rows logged so far (below the {d.min_sample_threshold}-row minimum) --
                    PSI values below this sample size can be unreliable. Treat the numbers below as directional.
                  </p>
                </CardBody>
              </Card>
            )}

            <div className="grid grid-cols-3 gap-4">
              <StatTile label="Stable" value={d.counts.stable} accent="good" />
              <StatTile label="Moderate" value={d.counts.moderate} accent="warning" />
              <StatTile label="Significant" value={d.counts.significant} accent="critical" />
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <Card>
                <CardHeader
                  title="PSI by feature"
                  subtitle={`reference n=${d.reference_size.toLocaleString()} vs live n=${d.live_size.toLocaleString()} -- click a bar to drill in`}
                />
                <CardBody>
                  <PsiBarChart data={d.all_features} onSelect={setSelected} selected={selected ?? undefined} />
                </CardBody>
              </Card>

              <Card>
                <CardHeader title="Feature detail" subtitle={selected ?? "select a feature from the chart"} />
                <CardBody>
                  {selected ? (
                    <FeatureDrillDown feature={selected} />
                  ) : (
                    <EmptyState message="Click any bar on the left to see its distribution and trend." />
                  )}
                </CardBody>
              </Card>
            </div>
          </>
        )}
      />
    </div>
  );
}
