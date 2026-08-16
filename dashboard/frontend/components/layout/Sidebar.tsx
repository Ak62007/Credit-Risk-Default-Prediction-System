"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Activity, LayoutDashboard, ListTree, Stethoscope } from "lucide-react";

const NAV_ITEMS = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/drift", label: "Drift Monitoring", icon: Activity },
  { href: "/predictions", label: "Predictions", icon: ListTree },
  { href: "/data-health", label: "Data Health", icon: Stethoscope },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-60 shrink-0 flex-col border-r border-border bg-surface-1">
      <div className="px-5 py-5">
        <p className="text-sm font-semibold text-text-primary">Credit Risk Ops</p>
        <p className="text-xs text-text-muted">Model monitoring dashboard</p>
      </div>
      <nav className="flex flex-col gap-0.5 px-3">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-[color-mix(in_oklab,var(--series-1)_12%,transparent)] text-series-1"
                  : "text-text-secondary hover:bg-surface-3 hover:text-text-primary"
              )}
            >
              <Icon className="h-4 w-4" strokeWidth={2} />
              {label}
            </Link>
          );
        })}
      </nav>
      <div className="mt-auto px-5 py-4">
        <p className="text-[11px] leading-relaxed text-text-muted">
          Read-only view over prediction_logs. No ground-truth labels exist yet, so this
          covers input drift, traffic, and score distribution -- not accuracy.
        </p>
      </div>
    </aside>
  );
}
