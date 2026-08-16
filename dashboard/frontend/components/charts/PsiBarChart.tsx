"use client";

import { Bar, BarChart, CartesianGrid, Cell, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { DriftLevel } from "@/lib/types";

const LEVEL_COLOR: Record<DriftLevel, string> = {
  stable: "var(--status-good)",
  moderate: "var(--status-warning)",
  significant: "var(--status-critical)",
};

export interface PsiBarDatum {
  feature: string;
  PSI: number;
  drift_level: DriftLevel;
}

export function PsiBarChart({
  data,
  onSelect,
  selected,
}: {
  data: PsiBarDatum[];
  onSelect?: (feature: string) => void;
  selected?: string;
}) {
  const sorted = [...data].sort((a, b) => b.PSI - a.PSI);
  const height = Math.max(320, sorted.length * 20);

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={sorted} layout="vertical" margin={{ top: 4, right: 24, left: 4, bottom: 4 }}>
        <CartesianGrid stroke="var(--gridline)" horizontal={false} />
        <XAxis
          type="number"
          tick={{ fill: "var(--text-muted)", fontSize: 11 }}
          axisLine={{ stroke: "var(--baseline)" }}
          tickLine={false}
        />
        <YAxis
          type="category"
          dataKey="feature"
          tick={{ fill: "var(--text-secondary)", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          width={170}
        />
        <ReferenceLine x={0.1} stroke="var(--status-warning)" strokeDasharray="3 3" strokeWidth={1} />
        <ReferenceLine x={0.25} stroke="var(--status-critical)" strokeDasharray="3 3" strokeWidth={1} />
        <Tooltip
          cursor={{ fill: "var(--surface-3)" }}
          contentStyle={{
            background: "var(--surface-1)",
            border: "1px solid var(--border)",
            borderRadius: 8,
            fontSize: 12,
            color: "var(--text-primary)",
          }}
          formatter={(value, _name, entry) => [
            `PSI ${Number(value).toFixed(3)} (${(entry.payload as PsiBarDatum).drift_level})`,
            "",
          ]}
        />
        <Bar
          dataKey="PSI"
          radius={[0, 3, 3, 0]}
          maxBarSize={14}
          onClick={(entry) => onSelect?.((entry as unknown as PsiBarDatum).feature)}
          cursor={onSelect ? "pointer" : undefined}
        >
          {sorted.map((d) => (
            <Cell
              key={d.feature}
              fill={LEVEL_COLOR[d.drift_level]}
              opacity={selected && selected !== d.feature ? 0.35 : 1}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
