"use client";

import { useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { Card, CardBody } from "@/components/ui/Card";
import { DataView } from "@/components/ui/DataView";
import { Badge } from "@/components/ui/Badge";
import { format, parseISO } from "date-fns";
import type { PredictionListFilters } from "@/lib/types";

const PAGE_SIZE = 25;

export default function PredictionsPage() {
  const [filters, setFilters] = useState<PredictionListFilters>({});
  const [offset, setOffset] = useState(0);

  const list = useApi(
    () => api.predictions({ ...filters, limit: PAGE_SIZE, offset }),
    [JSON.stringify(filters), offset]
  );

  function updateFilter<K extends keyof PredictionListFilters>(key: K, value: PredictionListFilters[K]) {
    setOffset(0);
    setFilters((f) => ({ ...f, [key]: value || undefined }));
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-semibold text-text-primary">Predictions Explorer</h1>
        <p className="mt-1 text-sm text-text-secondary">Browse and filter logged predictions.</p>
      </div>

      <Card>
        <CardBody className="flex flex-wrap items-center gap-3 pt-5">
          <select
            className="rounded-lg border border-border bg-surface-1 px-3 py-1.5 text-sm text-text-primary"
            value={filters.pred ?? ""}
            onChange={(e) => updateFilter("pred", e.target.value === "" ? undefined : Number(e.target.value))}
          >
            <option value="">Any outcome</option>
            <option value="0">Repayable (0)</option>
            <option value="1">Default (1)</option>
          </select>
          <input
            className="w-32 rounded-lg border border-border bg-surface-1 px-3 py-1.5 text-sm text-text-primary placeholder:text-text-muted"
            placeholder="purpose"
            value={filters.purpose ?? ""}
            onChange={(e) => updateFilter("purpose", e.target.value)}
          />
          <input
            className="w-24 rounded-lg border border-border bg-surface-1 px-3 py-1.5 text-sm text-text-primary placeholder:text-text-muted"
            placeholder="state (CA)"
            maxLength={2}
            value={filters.addr_state ?? ""}
            onChange={(e) => updateFilter("addr_state", e.target.value.toUpperCase())}
          />
          <input
            type="number"
            step="0.01"
            min={0}
            max={1}
            className="w-28 rounded-lg border border-border bg-surface-1 px-3 py-1.5 text-sm text-text-primary placeholder:text-text-muted"
            placeholder="min prob"
            value={filters.min_prob ?? ""}
            onChange={(e) => updateFilter("min_prob", e.target.value ? Number(e.target.value) : undefined)}
          />
          <input
            type="number"
            step="0.01"
            min={0}
            max={1}
            className="w-28 rounded-lg border border-border bg-surface-1 px-3 py-1.5 text-sm text-text-primary placeholder:text-text-muted"
            placeholder="max prob"
            value={filters.max_prob ?? ""}
            onChange={(e) => updateFilter("max_prob", e.target.value ? Number(e.target.value) : undefined)}
          />
          {Object.keys(filters).length > 0 && (
            <button
              className="text-xs font-medium text-series-1 hover:underline"
              onClick={() => {
                setFilters({});
                setOffset(0);
              }}
            >
              Clear filters
            </button>
          )}
        </CardBody>
      </Card>

      <Card>
        <DataView
          data={list.data}
          loading={list.loading}
          error={list.error}
          render={(d) => (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-border text-xs uppercase tracking-wide text-text-muted">
                      <th className="px-5 py-3 font-medium">Logged at</th>
                      <th className="px-5 py-3 font-medium">Outcome</th>
                      <th className="px-5 py-3 font-medium">Prob</th>
                      <th className="px-5 py-3 font-medium">Purpose</th>
                      <th className="px-5 py-3 font-medium">State</th>
                      <th className="px-5 py-3 font-medium">Loan amt</th>
                      <th className="px-5 py-3 font-medium">Income</th>
                      <th className="px-5 py-3 font-medium">DTI</th>
                    </tr>
                  </thead>
                  <tbody>
                    {d.rows.map((row) => (
                      <tr key={row.request_id} className="border-b border-border last:border-0 hover:bg-surface-3">
                        <td className="px-5 py-2.5">
                          <Link href={`/predictions/${row.request_id}`} className="text-series-1 hover:underline">
                            {format(parseISO(row.logged_at), "MMM d, HH:mm:ss")}
                          </Link>
                        </td>
                        <td className="px-5 py-2.5">
                          <Badge className={row.pred === 1 ? "bg-[color-mix(in_oklab,var(--status-critical)_14%,transparent)] text-[var(--status-critical)]" : undefined}>
                            {row.pred === 1 ? "default" : "repay"}
                          </Badge>
                        </td>
                        <td className="px-5 py-2.5 tabular-nums text-text-secondary">{row.prob.toFixed(3)}</td>
                        <td className="px-5 py-2.5 text-text-secondary">{row.purpose}</td>
                        <td className="px-5 py-2.5 text-text-secondary">{row.addr_state}</td>
                        <td className="px-5 py-2.5 tabular-nums text-text-secondary">${row.loan_amnt.toLocaleString()}</td>
                        <td className="px-5 py-2.5 tabular-nums text-text-secondary">${row.annual_inc.toLocaleString()}</td>
                        <td className="px-5 py-2.5 tabular-nums text-text-secondary">{row.dti.toFixed(1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="flex items-center justify-between px-5 py-4">
                <p className="text-xs text-text-muted">
                  {d.total === 0 ? "No results" : `Showing ${offset + 1}-${Math.min(offset + PAGE_SIZE, d.total)} of ${d.total}`}
                </p>
                <div className="flex gap-2">
                  <button
                    className="rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-text-secondary disabled:opacity-40"
                    disabled={offset === 0}
                    onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                  >
                    Previous
                  </button>
                  <button
                    className="rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-text-secondary disabled:opacity-40"
                    disabled={offset + PAGE_SIZE >= d.total}
                    onClick={() => setOffset(offset + PAGE_SIZE)}
                  >
                    Next
                  </button>
                </div>
              </div>
            </>
          )}
        />
      </Card>
    </div>
  );
}
