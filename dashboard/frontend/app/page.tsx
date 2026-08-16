"use client";

import { api } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { StatTile } from "@/components/ui/StatTile";
import { DataView } from "@/components/ui/DataView";
import { Badge } from "@/components/ui/Badge";
import { TrafficChart } from "@/components/charts/TrafficChart";
import { ScoreHistogramChart } from "@/components/charts/ScoreHistogramChart";
import { format, parseISO } from "date-fns";

export default function OverviewPage() {
  const overview = useApi(() => api.overview(), []);
  const traffic = useApi(() => api.trafficHourly(48), []);
  const scores = useApi(() => api.scoreDistribution(30), []);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold text-text-primary">Overview</h1>
        <p className="mt-1 text-sm text-text-secondary">
          Live status of the credit risk prediction service, read from <code className="text-xs">prediction_logs</code>.
        </p>
      </div>

      <DataView
        data={overview.data}
        loading={overview.loading}
        error={overview.error}
        render={(d) => (
          <>
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              <StatTile label="Total predictions logged" value={d.total_logged.toLocaleString()} />
              <StatTile
                label="Requests, last 24h"
                value={d.requests_last_24h.toLocaleString()}
                hint={`${d.requests_last_1h} in the last hour`}
              />
              <StatTile
                label="Predicted default rate"
                value={`${(
                  (100 * (d.pred_split["1"] ?? 0)) /
                  Math.max(1, (d.pred_split["0"] ?? 0) + (d.pred_split["1"] ?? 0))
                ).toFixed(1)}%`}
                hint={`${d.pred_split["1"] ?? 0} of ${d.total_logged} flagged`}
              />
              <StatTile label="Decision threshold" value={d.current_threshold.toFixed(2)} hint={d.model_artifact} />
            </div>

            <Card className="mt-2">
              <CardBody className="pt-5">
                <p className="text-xs text-text-muted">
                  Logged {d.logged_at_range.min ? format(parseISO(d.logged_at_range.min), "MMM d, HH:mm") : "-"} through{" "}
                  {d.logged_at_range.max ? format(parseISO(d.logged_at_range.max), "MMM d, HH:mm") : "-"}. {d.model_version_note}
                </p>
              </CardBody>
            </Card>
          </>
        )}
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader
            title="Traffic, last 48h"
            subtitle="Hourly request volume"
            action={
              traffic.data?.is_bursty ? <Badge>bursty / load-test traffic</Badge> : undefined
            }
          />
          <CardBody>
            <DataView
              data={traffic.data}
              loading={traffic.loading}
              error={traffic.error}
              render={(d) => (
                <>
                  <TrafficChart buckets={d.buckets} />
                  {d.note && <p className="mt-2 text-xs text-text-muted">{d.note}</p>}
                </>
              )}
            />
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Score distribution" subtitle="Predicted default probability across logged requests" />
          <CardBody>
            <DataView
              data={scores.data}
              loading={scores.loading}
              error={scores.error}
              render={(d) => (
                <>
                  <ScoreHistogramChart buckets={d.buckets} threshold={d.threshold} />
                  <p className="mt-2 text-xs text-text-muted">
                    mean {d.mean?.toFixed(3)} &middot; median {d.median?.toFixed(3)}
                  </p>
                </>
              )}
            />
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
