/**
 * Scroll-stage visual for the pipeline: document → sections → chunks →
 * vectors → retrieval → answer. Layers cross-fade with the active stage.
 */
export function PipelineVisual({ active, p }: { active: number; p: number }) {
  const show = (from: number, to: number) => (active >= from && active <= to ? 1 : 0);

  const chunks = Array.from({ length: 18 });
  const points = Array.from({ length: 36 });

  return (
    <svg
      aria-hidden
      viewBox="0 0 360 360"
      className="h-full w-full text-foreground"
      preserveAspectRatio="xMidYMid meet"
    >
      {/* document sheet: stages 01–03 */}
      <g style={{ opacity: show(0, 2), transition: "opacity 600ms ease" }}>
        <rect
          x="108"
          y="46"
          width="144"
          height="200"
          fill="var(--surface)"
          fillOpacity="0.4"
          stroke="var(--border-strong)"
        />
        <text x="122" y="72" className="font-mono" fontSize="9" letterSpacing="2.4" fill="var(--signal)">
          10-K
        </text>
        {[86, 94, 102, 110].map((y) => (
          <rect key={y} x="122" y={y} width="96" height="1.6" fill="currentColor" opacity="0.22" />
        ))}
        {/* extracted sections highlight: stage 02+ */}
        <g style={{ opacity: active >= 1 ? 1 : 0, transition: "opacity 500ms ease" }}>
          <rect x="118" y="124" width="124" height="16" fill="var(--signal)" opacity="0.16" />
          <text x="122" y="136" className="font-mono" fontSize="7" letterSpacing="1.6" fill="var(--signal)">
            ITEM 1A
          </text>
          <rect x="118" y="164" width="124" height="16" fill="var(--signal)" opacity="0.12" />
          <text x="122" y="176" className="font-mono" fontSize="7" letterSpacing="1.6" fill="var(--signal)">
            ITEM 3
          </text>
        </g>
        {[196, 204, 212, 220].map((y) => (
          <rect key={y} x="122" y={y} width="88" height="1.6" fill="currentColor" opacity="0.18" />
        ))}
      </g>

      {/* chunks: stage 03 */}
      <g style={{ opacity: show(2, 2), transition: "opacity 600ms ease" }}>
        {chunks.map((_, i) => (
          <rect
            key={i}
            x={104 + (i % 6) * 26}
            y={272 + Math.floor(i / 6) * 18}
            width="20"
            height="11"
            fill="var(--signal)"
            opacity={0.18 + (i % 5) * 0.06}
          />
        ))}
      </g>

      {/* vectors / index / retrieval / answer: stages 04–08 */}
      <g style={{ opacity: active >= 3 ? 1 : 0, transition: "opacity 600ms ease" }}>
        {points.map((_, i) => {
          const col = i % 6;
          const row = Math.floor(i / 6);
          const scattered = active === 3;
          const cx = scattered ? 84 + ((i * 47) % 200) : 96 + col * 34;
          const cy = scattered ? 70 + ((i * 83) % 210) : 84 + row * 34;
          const relevant = i % 7 === 0;
          const lit = active >= 5 && relevant;
          return (
            <circle
              key={i}
              cx={cx}
              cy={cy}
              r={lit ? 3.4 : 2}
              fill={lit ? "var(--signal)" : "currentColor"}
              opacity={lit ? 0.9 : active >= 5 ? 0.18 : 0.4}
              style={{ transition: "all 700ms cubic-bezier(0.2,0.7,0.2,1)" }}
            />
          );
        })}

        {/* query sweep: stage 06 */}
        <line
          x1="72"
          x2="288"
          y1={80 + (p % 0.125) * 8 * 190}
          y2={80 + (p % 0.125) * 8 * 190}
          stroke="var(--signal)"
          strokeWidth="1"
          opacity={active === 5 ? 0.55 : 0}
          style={{ transition: "opacity 400ms ease" }}
        />

        {/* convergence: stage 07 */}
        <g style={{ opacity: active === 6 ? 1 : 0, transition: "opacity 500ms ease" }}>
          {[0, 1, 2, 3].map((i) => (
            <line
              key={i}
              x1={96 + i * 46}
              y1={100 + i * 24}
              x2="180"
              y2="290"
              stroke="var(--signal)"
              strokeWidth="0.8"
              opacity="0.35"
            />
          ))}
        </g>

        {/* answer card: stage 08 */}
        <g style={{ opacity: active === 7 ? 1 : 0, transition: "opacity 500ms ease" }}>
          <rect
            x="96"
            y="252"
            width="168"
            height="76"
            fill="var(--surface)"
            fillOpacity="0.55"
            stroke="var(--signal)"
            strokeOpacity="0.5"
          />
          <text x="110" y="272" className="font-mono" fontSize="7" letterSpacing="1.8" fill="var(--signal)">
            ANSWER
          </text>
          {[282, 290, 298].map((y, i) => (
            <rect key={y} x="110" y={y} width={132 - i * 22} height="1.8" fill="currentColor" opacity="0.3" />
          ))}
          <text x="110" y="318" className="font-mono" fontSize="6.5" letterSpacing="1.4" fill="currentColor" opacity="0.5">
            SOURCES · ITEM 1A
          </text>
        </g>
      </g>
    </svg>
  );
}
