/** Local, lightweight CSS/SVG mini previews of SEC filing artifacts. No external images. */

type DocProps = {
  kicker?: string;
  heading?: string;
  lines?: number;
  highlight?: number;
  chart?: "diff" | "answer" | "none";
  label?: string;
};

function Lines({ count, highlight }: { count: number; highlight?: number | undefined }) {
  return (
    <div className="mt-1 space-y-[3px]">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={i === highlight ? "h-[3px] bg-signal/60" : "h-[2px] bg-muted-foreground/25"}
          style={{ width: `${62 + ((i * 37) % 36)}%` }}
        />
      ))}
    </div>
  );
}

export function FilingDoc({ kicker, heading, lines = 8, highlight, chart = "none", label }: DocProps) {
  return (
    <div aria-hidden className="flex h-full w-full flex-col p-[6px] text-left">
      {kicker ? (
        <span className="font-mono text-[4.5px] tracking-[0.18em] text-signal uppercase">{kicker}</span>
      ) : null}
      {heading ? (
        <span className="mt-[2px] text-[5px] leading-[1.15] font-medium tracking-[-0.01em] text-foreground">
          {heading}
        </span>
      ) : null}
      <div className="mt-[3px] h-px w-full bg-border" />
      {chart === "none" ? <Lines count={lines} highlight={highlight} /> : null}
      {chart === "diff" ? (
        <div className="mt-[4px] grid flex-1 grid-cols-2 gap-[3px]">
          <div className="space-y-[3px] border-r border-border pr-[3px]">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-[2px] bg-muted-foreground/25" />
            ))}
          </div>
          <div className="space-y-[3px]">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className={i === 1 || i === 3 ? "h-[2px] bg-signal/60" : "h-[2px] bg-muted-foreground/25"} />
            ))}
          </div>
        </div>
      ) : null}
      {chart === "answer" ? (
        <div className="mt-[4px] flex-1 space-y-[3px]">
          <div className="h-[2px] w-3/4 bg-muted-foreground/25" />
          <div className="h-[2px] w-2/3 bg-muted-foreground/25" />
          <div className="mt-[4px] border border-border bg-surface/70 p-[3px]">
            <div className="h-[2px] w-4/5 bg-signal/55" />
            <div className="mt-[2px] h-[2px] w-3/5 bg-signal/35" />
          </div>
        </div>
      ) : null}
      {label ? (
        <span className="mt-auto font-mono text-[4px] tracking-[0.14em] text-muted-foreground">{label}</span>
      ) : null}
    </div>
  );
}

export const filingDocSets: Record<string, { alt: string; node: React.ReactNode }[]> = {
  risk: [
    { alt: "10-K cover page showing Item 1A Risk Factors", node: <FilingDoc kicker="Item 1A" heading="Risk Factors" lines={7} label="10-K" /> },
    { alt: "Highlighted risk paragraph excerpt", node: <FilingDoc heading="Key risk excerpt" lines={9} highlight={3} /> },
    { alt: "Additional filing excerpt", node: <FilingDoc kicker="Annual report" heading="Business risks" lines={8} highlight={6} /> },
  ],
  legal: [
    { alt: "Filing page showing Item 3 Legal Proceedings", node: <FilingDoc kicker="Item 3" heading="Legal Proceedings" lines={7} label="10-K" /> },
    { alt: "Legal disclosure excerpt", node: <FilingDoc heading="Disclosure" lines={9} highlight={2} /> },
    { alt: "Litigation case text excerpt", node: <FilingDoc kicker="Matters" heading="Pending cases" lines={8} highlight={5} /> },
  ],
  supply: [
    { alt: "Supplier disclosure page", node: <FilingDoc kicker="Item 1A" heading="Supplier concentration" lines={7} /> },
    { alt: "Manufacturing and distribution excerpt", node: <FilingDoc heading="Manufacturing" lines={9} highlight={4} /> },
    { alt: "Supply-chain risk excerpt", node: <FilingDoc kicker="Operations" heading="Supply chain" lines={8} highlight={1} /> },
  ],
  cyber: [
    { alt: "Cybersecurity risk heading in filing", node: <FilingDoc kicker="Item 1A" heading="Cybersecurity" lines={7} /> },
    { alt: "Security disclosure excerpt", node: <FilingDoc heading="Systems & data" lines={9} highlight={3} /> },
    { alt: "Cyber risk paragraph excerpt", node: <FilingDoc kicker="Item 1C" heading="Risk management" lines={8} highlight={6} /> },
  ],
  changes: [
    { alt: "2024 annual filing", node: <FilingDoc kicker="FY2024" heading="Risk Factors" lines={8} label="10-K" /> },
    { alt: "2025 annual filing", node: <FilingDoc kicker="FY2025" heading="Risk Factors" lines={8} highlight={2} label="10-K" /> },
    { alt: "Side-by-side risk comparison", node: <FilingDoc kicker="Diff" heading="Year over year" chart="diff" /> },
  ],
  ai: [
    { alt: "User question card", node: <FilingDoc kicker="Question" heading="What are the top risks?" lines={4} /> },
    { alt: "Retrieved filing excerpt", node: <FilingDoc kicker="Retrieved" heading="Filing context" lines={9} highlight={4} /> },
    { alt: "AI answer with sources", node: <FilingDoc kicker="Answer" heading="Evidence-backed" chart="answer" label="Sources" /> },
  ],
};
