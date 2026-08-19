import { cn } from "@/lib/utils";
import { PRESETS } from "@/lib/presets";

export function PresetPicker({
  activeId,
  onSelect,
}: {
  activeId: string | null;
  onSelect: (presetId: string) => void;
}) {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
      {PRESETS.map((preset) => (
        <button
          key={preset.id}
          type="button"
          onClick={() => onSelect(preset.id)}
          className={cn(
            "rounded-lg border px-4 py-3 text-left transition-colors",
            activeId === preset.id
              ? "border-series-1 bg-[color-mix(in_oklab,var(--series-1)_8%,transparent)]"
              : "border-border bg-surface-1 hover:bg-surface-3",
          )}
        >
          <p className="text-sm font-semibold text-text-primary">{preset.label}</p>
          <p className="mt-1 text-xs leading-relaxed text-text-muted">{preset.blurb}</p>
        </button>
      ))}
    </div>
  );
}
