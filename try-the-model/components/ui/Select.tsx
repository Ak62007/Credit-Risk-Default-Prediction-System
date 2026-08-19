import { cn } from "@/lib/utils";
import type { SelectHTMLAttributes } from "react";

export function Select({ className, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className={cn(
        "w-full rounded-lg border border-border bg-surface-1 px-3 py-2 text-sm text-text-primary",
        "focus:border-series-1 focus:outline-none focus:ring-2 focus:ring-[color-mix(in_oklab,var(--series-1)_25%,transparent)]",
        className,
      )}
      {...props}
    />
  );
}
