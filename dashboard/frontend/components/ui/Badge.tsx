import { cn } from "@/lib/utils";
import type { DriftLevel } from "@/lib/types";

const DRIFT_STYLES: Record<DriftLevel, string> = {
  stable: "bg-[color-mix(in_oklab,var(--status-good)_14%,transparent)] text-[var(--status-good)]",
  moderate: "bg-[color-mix(in_oklab,var(--status-warning)_20%,transparent)] text-[#8a5a00]",
  significant: "bg-[color-mix(in_oklab,var(--status-critical)_14%,transparent)] text-[var(--status-critical)]",
};

export function DriftBadge({ level }: { level: DriftLevel }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium capitalize",
        DRIFT_STYLES[level]
      )}
    >
      <span
        className="h-1.5 w-1.5 rounded-full"
        style={{
          backgroundColor:
            level === "stable"
              ? "var(--status-good)"
              : level === "moderate"
                ? "var(--status-warning)"
                : "var(--status-critical)",
        }}
      />
      {level}
    </span>
  );
}

export function Badge({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full bg-surface-3 px-2 py-0.5 text-xs font-medium text-text-secondary",
        className
      )}
    >
      {children}
    </span>
  );
}
