"use client";

import { use } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { api } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { DataView } from "@/components/ui/DataView";
import { Badge } from "@/components/ui/Badge";
import { ReasonCodeChart } from "@/components/charts/ReasonCodeChart";
import { format, parseISO } from "date-fns";

export default function PredictionDetailPage({ params }: { params: Promise<{ requestId: string }> }) {
  const { requestId } = use(params);
  const detail = useApi(() => api.prediction(requestId), [requestId]);

  return (
    <div className="flex flex-col gap-6">
      <Link href="/predictions" className="flex w-fit items-center gap-1.5 text-sm text-text-secondary hover:text-text-primary">
        <ArrowLeft className="h-3.5 w-3.5" /> Back to Predictions
      </Link>

      <DataView
        data={detail.data}
        loading={detail.loading}
        error={detail.error}
        render={(d) => (
          <>
            <div className="flex items-center justify-between">
              <div>
                <h1 className="font-mono text-lg font-semibold text-text-primary">{d.request_id}</h1>
                <p className="mt-1 text-sm text-text-secondary">
                  Logged {format(parseISO(d.logged_at), "MMM d, yyyy HH:mm:ss")}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-2xl font-semibold tabular-nums text-text-primary">{d.prob.toFixed(3)}</span>
                <Badge
                  className={
                    d.pred === 1
                      ? "bg-[color-mix(in_oklab,var(--status-critical)_14%,transparent)] text-[var(--status-critical)]"
                      : "bg-[color-mix(in_oklab,var(--status-good)_14%,transparent)] text-[var(--status-good)]"
                  }
                >
                  {d.pred === 1 ? "predicted default" : "predicted repay"}
                </Badge>
              </div>
            </div>

            <Card>
              <CardHeader title="Why" subtitle="Top SHAP contributions to this prediction" />
              <CardBody>
                <ReasonCodeChart reasonCodes={d.reason_codes} />
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Raw input" subtitle="Fields submitted with this request" />
              <CardBody>
                <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm md:grid-cols-3">
                  {Object.entries(d.raw_input)
                    .filter(([, v]) => v !== null)
                    .map(([key, value]) => (
                      <div key={key} className="flex justify-between gap-3 border-b border-border py-1">
                        <span className="truncate text-text-muted">{key}</span>
                        <span className="tabular-nums text-text-secondary">{String(value)}</span>
                      </div>
                    ))}
                </div>
              </CardBody>
            </Card>
          </>
        )}
      />
    </div>
  );
}
