"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { Activity, LayoutDashboard, ListTree, Menu, Stethoscope, X } from "lucide-react";

const NAV_ITEMS = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/drift", label: "Drift Monitoring", icon: Activity },
  { href: "/predictions", label: "Predictions", icon: ListTree },
  { href: "/data-health", label: "Data Health", icon: Stethoscope },
];

export function Sidebar() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);

  // Below `lg`, the sidebar is a drawer -- close it whenever the route changes
  // (e.g. after tapping a nav link) so it doesn't stay open over the new page.
  const [lastPathname, setLastPathname] = useState(pathname);
  if (pathname !== lastPathname) {
    setLastPathname(pathname);
    setIsOpen(false);
  }

  useEffect(() => {
    if (!isOpen) return;
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") setIsOpen(false);
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [isOpen]);

  return (
    <>
      <header className="fixed inset-x-0 top-0 z-30 flex h-14 items-center gap-3 border-b border-border bg-surface-1 px-4 lg:hidden">
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          aria-label="Open navigation menu"
          className="flex h-9 w-9 items-center justify-center rounded-lg text-text-secondary hover:bg-surface-3 hover:text-text-primary"
        >
          <Menu className="h-5 w-5" strokeWidth={2} />
        </button>
        <p className="text-sm font-semibold text-text-primary">Credit Risk Ops</p>
      </header>

      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setIsOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex h-full w-64 shrink-0 flex-col border-r border-border bg-surface-1 transition-transform duration-200 ease-out",
          "lg:static lg:z-auto lg:w-60 lg:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex items-start justify-between px-5 py-5">
          <div>
            <p className="text-sm font-semibold text-text-primary">Credit Risk Ops</p>
            <p className="text-xs text-text-muted">Model monitoring dashboard</p>
          </div>
          <button
            type="button"
            onClick={() => setIsOpen(false)}
            aria-label="Close navigation menu"
            className="flex h-8 w-8 items-center justify-center rounded-lg text-text-secondary hover:bg-surface-3 hover:text-text-primary lg:hidden"
          >
            <X className="h-4 w-4" strokeWidth={2} />
          </button>
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
    </>
  );
}
