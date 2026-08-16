"use client";

import { Bar, BarChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ScoreBucket } from "@/lib/types";

export function ScoreHistogramChart({ buckets, threshold }: { buckets: ScoreBucket[]; threshold: number }) {
  const data = buckets.map((b) => ({
    ...b,
    label: b.range_start.toFixed(2),
    crossesThreshold: threshold >= b.range_start && threshold < b.range_end,
  }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 22, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="var(--gridline)" vertical={false} />
        <XAxis
          dataKey="label"
          tick={{ fill: "var(--text-muted)", fontSize: 11 }}
          axisLine={{ stroke: "var(--baseline)" }}
          tickLine={false}
          interval={4}
        />
        <YAxis
          tick={{ fill: "var(--text-muted)", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          width={36}
          allowDecimals={false}
        />
        <Tooltip
          contentStyle={{
            background: "var(--surface-1)",
            border: "1px solid var(--border)",
            borderRadius: 8,
            fontSize: 12,
            color: "var(--text-primary)",
          }}
          labelFormatter={(label) => `prob ~ ${label}`}
          formatter={(value) => [`${value} predictions`, ""]}
        />
        <ReferenceLine
          x={data.find((d) => d.crossesThreshold)?.label}
          stroke="var(--status-critical)"
          strokeDasharray="4 3"
          strokeWidth={1.5}
          label={{ value: `threshold ${threshold}`, position: "top", fill: "var(--status-critical)", fontSize: 11 }}
        />
        <Bar dataKey="count" fill="var(--series-1)" radius={[3, 3, 0, 0]} maxBarSize={22} />
      </BarChart>
    </ResponsiveContainer>
  );
}
