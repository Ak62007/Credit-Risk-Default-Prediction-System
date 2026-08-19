export function ProbabilityGauge({ probability }: { probability: number }) {
  const pct = Math.round(probability * 100);
  const clamped = Math.min(1, Math.max(0, probability));

  // Semicircle arc from -90deg to +90deg.
  const radius = 70;
  const cx = 90;
  const cy = 82;
  const endAngle = Math.PI - clamped * Math.PI; // sweeps from 180deg (left) toward 0deg (right)
  const x2 = cx + radius * Math.cos(endAngle);
  const y2 = cy + radius * Math.sin(endAngle) * -1;
  // The colored arc always sweeps clockwise from the left point by at most 180deg
  // (probability tops out at 100%), so it's never the circle's "large" arc — this
  // must stay 0, or SVG picks the wrong arc center once probability exceeds 50%.
  const largeArc = 0;

  const color =
    clamped < 0.2
      ? "var(--status-good)"
      : clamped < 0.4
        ? "var(--status-warning)"
        : clamped < 0.65
          ? "var(--status-serious)"
          : "var(--status-critical)";

  return (
    <div className="flex flex-col items-center pb-3">
      <svg viewBox="0 0 180 128" className="w-full max-w-[220px]">
        <path
          d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 1 1 ${cx + radius} ${cy}`}
          fill="none"
          stroke="var(--gridline)"
          strokeWidth={14}
          strokeLinecap="round"
        />
        {clamped > 0.001 && (
          <path
            d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}`}
            fill="none"
            stroke={color}
            strokeWidth={14}
            strokeLinecap="round"
          />
        )}
        <text x={cx} y={cy - 6} textAnchor="middle" className="fill-text-primary text-[28px] font-semibold tabular-nums">
          {pct}%
        </text>
        {/* Fixed distance below the dome's bottom edge (cy + half the stroke width),
            not tied to cy, so there's always real breathing room under the arc. */}
        <text x={cx} y={cy + 34} textAnchor="middle" className="fill-text-muted text-[11px]">
          estimated default probability
        </text>
      </svg>
    </div>
  );
}
