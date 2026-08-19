import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

type Tone = "neutral" | "good" | "critical";

const TONE_STYLES: Record<Tone, string> = {
  neutral: "bg-surface-3 text-text-secondary",
  good: "bg-[color-mix(in_oklab,var(--status-good)_14%,transparent)] text-[var(--status-good)]",
  critical: "bg-[color-mix(in_oklab,var(--status-critical)_14%,transparent)] text-[var(--status-critical)]",
};

export function Badge({
  tone = "neutral",
  className,
  children,
}: {
  tone?: Tone;
  className?: string;
  children: ReactNode;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-medium",
        TONE_STYLES[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
