import type { ReactNode } from "react";

export function Field({
  label,
  hint,
  value,
  children,
}: {
  label: string;
  hint?: string;
  value?: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-baseline justify-between gap-2">
        <label className="text-sm font-medium text-text-primary">{label}</label>
        {value !== undefined && (
          <span className="text-sm font-medium tabular-nums text-text-secondary">{value}</span>
        )}
      </div>
      {children}
      {hint && <p className="text-xs text-text-muted">{hint}</p>}
    </div>
  );
}
