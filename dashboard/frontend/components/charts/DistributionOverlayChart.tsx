"use client";

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { NumericBucket } from "@/lib/types";

function formatEdge(v: number | null): string {
  if (v === null) return "";
  if (Math.abs(v) >= 1000) return `${(v / 1000).toFixed(1)}k`;
  return Number.isInteger(v) ? `${v}` : v.toFixed(1);
}

const legendStyle = { fontSize: 12, color: "var(--text-secondary)" };
const tooltipContentStyle = {
  background: "var(--surface-1)",
  border: "1px solid var(--border)",
  borderRadius: 8,
  fontSize: 12,
  color: "var(--text-primary)",
};

export function NumericDistributionChart({ buckets }: { buckets: NumericBucket[] }) {
  const data = buckets.map((b, i) => ({
    label: i === 0 ? `< ${formatEdge(b.range_end)}` : i === buckets.length - 1 ? `> ${formatEdge(b.range_start)}` : `${formatEdge(b.range_start)}-${formatEdge(b.range_end)}`,
    Reference: b.reference_pct,
    Live: b.live_pct,
  }));

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }} barGap={2}>
        <CartesianGrid stroke="var(--gridline)" vertical={false} />
        <XAxis
          dataKey="label"
          tick={{ fill: "var(--text-muted)", fontSize: 10 }}
          axisLine={{ stroke: "var(--baseline)" }}
          tickLine={false}
          angle={-30}
          textAnchor="end"
          height={50}
        />
        <YAxis
          tick={{ fill: "var(--text-muted)", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          width={44}
          tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
        />
        <Tooltip
          contentStyle={tooltipContentStyle}
          formatter={(value) => `${(Number(value) * 100).toFixed(1)}%`}
        />
        <Legend wrapperStyle={legendStyle} iconType="circle" iconSize={8} />
        <Bar dataKey="Reference" fill="var(--series-1)" radius={[3, 3, 0, 0]} maxBarSize={20} />
        <Bar dataKey="Live" fill="var(--series-2)" radius={[3, 3, 0, 0]} maxBarSize={20} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function CategoricalDistributionChart({
  referenceProportions,
  liveProportions,
}: {
  referenceProportions: Record<string, number>;
  liveProportions: Record<string, number>;
}) {
  const categories = Object.keys(referenceProportions).sort(
    (a, b) => (referenceProportions[b] ?? 0) - (referenceProportions[a] ?? 0)
  );
  const data = categories.map((c) => ({
    label: c,
    Reference: referenceProportions[c] ?? 0,
    Live: liveProportions[c] ?? 0,
  }));

  return (
    <ResponsiveContainer width="100%" height={Math.max(240, categories.length * 28)}>
      <BarChart data={data} layout="vertical" margin={{ top: 8, right: 16, left: 4, bottom: 0 }} barGap={2}>
        <CartesianGrid stroke="var(--gridline)" horizontal={false} />
        <XAxis
          type="number"
          tick={{ fill: "var(--text-muted)", fontSize: 11 }}
          axisLine={{ stroke: "var(--baseline)" }}
          tickLine={false}
          tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
        />
        <YAxis
          type="category"
          dataKey="label"
          tick={{ fill: "var(--text-secondary)", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          width={110}
        />
        <Tooltip
          contentStyle={tooltipContentStyle}
          formatter={(value) => `${(Number(value) * 100).toFixed(1)}%`}
        />
        <Legend wrapperStyle={legendStyle} iconType="circle" iconSize={8} />
        <Bar dataKey="Reference" fill="var(--series-1)" radius={[0, 3, 3, 0]} maxBarSize={12} />
        <Bar dataKey="Live" fill="var(--series-2)" radius={[0, 3, 3, 0]} maxBarSize={12} />
      </BarChart>
    </ResponsiveContainer>
  );
}
