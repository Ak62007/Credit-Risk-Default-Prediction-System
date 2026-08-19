import { TrendingDown, TrendingUp } from "lucide-react";
import type { ExplainedReason } from "@/lib/explainReasonCodes";
import { cn } from "@/lib/utils";

const MAGNITUDE_LABEL: Record<ExplainedReason["magnitude"], string> = {
  strongly: "Strong effect",
  moderately: "Moderate effect",
  slightly: "Minor effect",
};

export function ReasonCodeList({ reasons }: { reasons: ExplainedReason[] }) {
  return (
    <ul className="flex flex-col divide-y divide-border">
      {reasons.map((reason) => {
        const Icon = reason.direction === "up" ? TrendingUp : TrendingDown;
        return (
          <li key={reason.feature} className="flex items-start gap-3 py-3 first:pt-0 last:pb-0">
            <span
              className={cn(
                "mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full",
                reason.direction === "up"
                  ? "bg-[color-mix(in_oklab,var(--status-critical)_14%,transparent)] text-[var(--status-critical)]"
                  : "bg-[color-mix(in_oklab,var(--status-good)_14%,transparent)] text-[var(--status-good)]",
              )}
            >
              <Icon className="h-4 w-4" strokeWidth={2} />
            </span>
            <div className="flex flex-col gap-0.5">
              <p className="text-sm text-text-primary">{reason.sentence}</p>
              <p className="text-xs text-text-muted">{MAGNITUDE_LABEL[reason.magnitude]}</p>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
