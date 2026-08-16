"use client";

import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function ReasonCodeChart({ reasonCodes }: { reasonCodes: Record<string, number> }) {
  const data = Object.entries(reasonCodes)
    .map(([feature, value]) => ({ feature: feature.replace(/^(num__|cat__)/, ""), value }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value));

  return (
    <ResponsiveContainer width="100%" height={Math.max(160, data.length * 34)}>
      <BarChart data={data} layout="vertical" margin={{ top: 4, right: 24, left: 4, bottom: 4 }}>
        <XAxis type="number" hide />
        <YAxis
          type="category"
          dataKey="feature"
          tick={{ fill: "var(--text-secondary)", fontSize: 12 }}
          axisLine={false}
          tickLine={false}
          width={150}
        />
        <Tooltip
          cursor={{ fill: "var(--surface-3)" }}
          contentStyle={{
            background: "var(--surface-1)",
            border: "1px solid var(--border)",
            borderRadius: 8,
            fontSize: 12,
            color: "var(--text-primary)",
          }}
          formatter={(value) => {
            const v = Number(value);
            return [v.toFixed(3), v >= 0 ? "pushes toward default" : "pushes away from default"];
          }}
        />
        <Bar dataKey="value" radius={3} maxBarSize={18}>
          {data.map((d) => (
            <Cell key={d.feature} fill={d.value >= 0 ? "var(--status-critical)" : "var(--status-good)"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
