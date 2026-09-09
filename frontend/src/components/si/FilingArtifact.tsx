import { usePrefersReducedMotion } from "@/lib/theme";

/**
 * Subtle 10-K filing sheet used as the hero visual: a document being scanned.
 * Pure SVG + CSS, very low opacity, matches the graph-paper aesthetic.
 */
export function FilingArtifact({ className = "" }: { className?: string }) {
  const reduced = usePrefersReducedMotion();

  const line = (y: number, w: number, dim = 0.25) => (
    <rect key={`${y}-${w}`} x="34" y={y} width={w} height="1.6" fill="currentColor" opacity={dim} />
  );

  return (
    <div aria-hidden className={`relative ${className}`}>
      <svg viewBox="0 0 340 460" className="h-full w-full text-foreground" preserveAspectRatio="xMidYMid meet">
        <rect
          x="16"
          y="12"
          width="308"
          height="436"
          fill="var(--surface)"
          fillOpacity="0.35"
          stroke="var(--border-strong)"
          strokeWidth="1"
        />
        <text x="34" y="52" className="font-mono" fontSize="13" letterSpacing="3" fill="var(--signal)">
          10-K
        </text>
        <text x="34" y="72" fontSize="9" letterSpacing="2.4" fill="currentColor" opacity="0.5">
          ANNUAL REPORT
        </text>
        <line x1="34" y1="86" x2="306" y2="86" stroke="var(--border-strong)" strokeWidth="1" />

        <text x="34" y="118" className="font-mono" fontSize="8" letterSpacing="2.2" fill="var(--signal)" opacity="0.9">
          ITEM 1A
        </text>
        <text x="34" y="134" fontSize="10.5" letterSpacing="0.4" fill="currentColor" opacity="0.85">
          RISK FACTORS
        </text>
        {[148, 158, 168, 178, 188].map((y, i) => line(y, 250 - i * 14))}
        <rect x="34" y="200" width="196" height="6" fill="var(--signal)" opacity="0.28" />
        {[216, 226, 236].map((y, i) => line(y, 240 - i * 22))}

        <text x="34" y="278" className="font-mono" fontSize="8" letterSpacing="2.2" fill="var(--signal)" opacity="0.9">
          ITEM 3
        </text>
        <text x="34" y="294" fontSize="10.5" letterSpacing="0.4" fill="currentColor" opacity="0.85">
          LEGAL PROCEEDINGS
        </text>
        {[308, 318, 328, 338].map((y, i) => line(y, 244 - i * 18))}
        <rect x="34" y="350" width="150" height="6" fill="var(--signal)" opacity="0.2" />
        {[366, 376, 386, 396, 406].map((y, i) => line(y, 236 - i * 12, 0.18))}

        {/* document particles */}
        {[
          [270, 150],
          [292, 214],
          [256, 330],
          [286, 392],
        ].map(([x, y]) => (
          <circle key={`${x}-${y}`} cx={x} cy={y} r="1.6" fill="var(--signal)" opacity="0.45" />
        ))}
      </svg>

      {/* scanning line */}
      {!reduced && (
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="si-scan absolute inset-x-[5%] h-[2px] bg-signal/40" />
        </div>
      )}
    </div>
  );
}
