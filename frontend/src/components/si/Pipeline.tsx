import { useEffect, useRef, useState } from "react";
import { PipelineVisual } from "./PipelineVisual";

const stages = [
  { n: "01", label: "Ingest", copy: "Retrieve 10-K filings from SEC EDGAR." },
  { n: "02", label: "Extract", copy: "Pull Item 1A Risk Factors and Item 3 Legal Proceedings." },
  { n: "03", label: "Chunk", copy: "Split filing text into semantic chunks." },
  { n: "04", label: "Embed", copy: "Generate local embeddings for semantic retrieval." },
  { n: "05", label: "Index", copy: "Store filing vectors and metadata in ChromaDB." },
  { n: "06", label: "Retrieve", copy: "Find the most relevant filing context for a question." },
  { n: "07", label: "Analyze", copy: "Generate an evidence-grounded answer using Groq." },
  { n: "08", label: "Insight", copy: "Return the answer with supporting filing sources." },
];

export function Pipeline() {
  const sectionRef = useRef<HTMLElement | null>(null);
  const [p, setP] = useState(0);

  useEffect(() => {
    const el = sectionRef.current;
    if (!el) return;
    let raf = 0;
    let target = 0;
    let current = 0;

    const compute = () => {
      const rect = el.getBoundingClientRect();
      const total = rect.height - window.innerHeight;
      target = total <= 0 ? 0 : Math.min(1, Math.max(0, -rect.top / total));
    };

    const tick = () => {
      current += (target - current) * 0.12;
      setP(current);
      raf = requestAnimationFrame(tick);
    };

    compute();
    window.addEventListener("scroll", compute, { passive: true });
    window.addEventListener("resize", compute);
    raf = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("scroll", compute);
      window.removeEventListener("resize", compute);
    };
  }, []);

  const active = Math.min(stages.length - 1, Math.floor(p * stages.length + 0.0001));

  return (
    <section id="how-it-works" ref={sectionRef} className="relative h-[420svh]">
      <div className="sticky top-0 flex h-[100svh] items-center overflow-hidden">
        <div className="mx-auto w-full max-w-6xl px-6">
          {/* filing transformation visual */}
          <div className="pointer-events-none absolute top-1/2 -right-[6vw] hidden h-[68vh] w-[38vh] -translate-y-1/2 opacity-60 lg:block">
            <PipelineVisual active={active} p={p} />
          </div>

          <div className="relative">
            <p className="label-mono">Process</p>
            <h2 className="mt-6 text-3xl tracking-[-0.02em] sm:text-4xl">How it works</h2>
            <p className="mt-3 text-muted-foreground">From filing to evidence-backed insight.</p>

            {/* continuous timeline */}
            <div className="relative mt-14 hidden md:block">
              <div className="pointer-events-none absolute top-1/2 right-0 left-0 h-px -translate-y-1/2 bg-border" />
              <div
                className="pointer-events-none absolute top-1/2 left-0 h-px -translate-y-1/2 bg-signal/70 transition-[width] duration-500 ease-out"
                style={{ width: `${p * 100}%` }}
              />
              <div
                className="pointer-events-none absolute top-1/2 h-[6px] w-[6px] -translate-y-1/2 rounded-full bg-signal"
                style={{ left: `calc(${p * 100}% - 3px)` }}
              />
              <div className="relative flex items-stretch justify-between">
                {stages.map((s, i) => (
                  <div key={s.n} className="flex flex-1 flex-col items-center">
                    <div
                      className="flex flex-col items-center pb-3 transition-opacity duration-500 ease-out"
                      style={{ opacity: i === active ? 1 : i < active ? 0.6 : 0.32 }}
                    >
                      <span
                        className="font-mono text-[0.68rem] tracking-[0.14em] transition-colors duration-500 ease-out"
                        style={{ color: i === active ? "var(--signal)" : "var(--muted-foreground)" }}
                      >
                        {s.n}
                      </span>
                    </div>
                    <div className="h-3 w-full" />
                    <div
                      className="flex flex-col items-center pt-3 transition-all duration-500 ease-out"
                      style={{
                        opacity: i === active ? 1 : i < active ? 0.55 : 0.3,
                        color: i === active ? "var(--foreground)" : "var(--muted-foreground)",
                      }}
                    >
                      <span className="text-[0.8rem] whitespace-nowrap">{s.label}</span>
                      <span
                        className="mt-2 h-px bg-signal transition-all duration-500 ease-out"
                        style={{ width: i === active ? "22px" : "0px" }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* mobile rail */}
            <div className="relative mt-10 h-px w-full bg-border md:hidden">
              <div
                className="absolute top-0 left-0 h-px bg-signal transition-[width] duration-500 ease-out"
                style={{ width: `${p * 100}%` }}
              />
              <div
                className="absolute -top-[3px] h-[7px] w-[7px] rounded-full bg-signal"
                style={{ left: `calc(${p * 100}% - 3px)` }}
              />
            </div>

            {/* active stage explanation */}
            <div className="mt-12 grid gap-8 md:grid-cols-12">
              <div className="md:col-span-5">
                <div key={active} className="animate-fade-in">
                  <p className="font-mono text-[0.7rem] tracking-[0.16em] text-signal">{stages[active]!.n}</p>
                  <h3 className="mt-4 text-2xl tracking-[-0.02em] sm:text-3xl">{stages[active]!.label}</h3>
                  <p className="mt-4 max-w-sm leading-relaxed text-muted-foreground">{stages[active]!.copy}</p>
                </div>
              </div>

              <div className="md:col-span-5 md:col-start-8">
                <ol className="space-y-2 md:hidden">
                  {stages.map((s, i) => (
                    <li
                      key={s.n}
                      className="flex items-baseline gap-3 text-sm transition-opacity duration-500"
                      style={{ opacity: i === active ? 1 : 0.4 }}
                    >
                      <span className="font-mono text-[0.7rem] text-signal">{s.n}</span>
                      <span>{s.label}</span>
                    </li>
                  ))}
                </ol>
                <div className="hidden space-y-3 md:block">
                  {stages.map((s, i) => (
                    <div key={s.n} className="flex items-center gap-4">
                      <div
                        className="h-px transition-all duration-500"
                        style={{
                          width: i === active ? "72px" : "28px",
                          background: i === active ? "var(--signal)" : "var(--border)",
                        }}
                      />
                      <span
                        className="text-[0.8rem] transition-opacity duration-500"
                        style={{ opacity: i === active ? 1 : 0.4 }}
                      >
                        {s.label}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
