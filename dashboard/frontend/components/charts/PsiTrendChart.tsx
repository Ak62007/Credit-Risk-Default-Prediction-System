"use client";

import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { DriftHistoryPoint } from "@/lib/types";
import { format, parseISO } from "date-fns";

export function PsiTrendChart({ points }: { points: DriftHistoryPoint[] }) {
  const data = points.map((p) => ({ ...p, label: format(parseISO(p.computed_at), "MMM d, HH:mm") }));

  return (
    <ResponsiveContainer width="100%" height={180}>
      <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="var(--gridline)" vertical={false} />
        <XAxis
          dataKey="label"
          tick={{ fill: "var(--text-muted)", fontSize: 10 }}
          axisLine={{ stroke: "var(--baseline)" }}
          tickLine={false}
          minTickGap={40}
        />
        <YAxis tick={{ fill: "var(--text-muted)", fontSize: 11 }} axisLine={false} tickLine={false} width={36} />
        <ReferenceLine y={0.1} stroke="var(--status-warning)" strokeDasharray="3 3" strokeWidth={1} />
        <ReferenceLine y={0.25} stroke="var(--status-critical)" strokeDasharray="3 3" strokeWidth={1} />
        <Tooltip
          contentStyle={{
            background: "var(--surface-1)",
            border: "1px solid var(--border)",
            borderRadius: 8,
            fontSize: 12,
            color: "var(--text-primary)",
          }}
          formatter={(value) => [Number(value).toFixed(3), "PSI"]}
        />
        <Line type="monotone" dataKey="psi" stroke="var(--series-1)" strokeWidth={2} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}
