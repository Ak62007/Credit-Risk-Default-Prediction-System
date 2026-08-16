import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

export function StatTile({
  label,
  value,
  hint,
  accent,
}: {
  label: string;
  value: ReactNode;
  hint?: string;
  accent?: "good" | "warning" | "critical";
}) {
  const accentColor =
    accent === "good"
      ? "var(--status-good)"
      : accent === "warning"
        ? "var(--status-warning)"
        : accent === "critical"
          ? "var(--status-critical)"
          : undefined;

  return (
    <div className="rounded-xl border border-border bg-surface-1 px-5 py-4">
      <p className="text-xs font-medium uppercase tracking-wide text-text-muted">{label}</p>
      <p
        className={cn("mt-1.5 text-2xl font-semibold tabular-nums text-text-primary")}
        style={accentColor ? { color: accentColor } : undefined}
      >
        {value}
      </p>
      {hint && <p className="mt-1 text-xs text-text-secondary">{hint}</p>}
    </div>
  );
}
