import { useRef, useState } from "react";
import { ArrowRight, MessageSquare, AlertCircle } from "lucide-react";
import { HoverBorderGradient } from "@/components/ui/hover-border-gradient";
import { ask, type Source } from "@/lib/api";
import type { Company } from "@/lib/companies";

type Turn = {
  role: "user" | "assistant";
  text: string;
  sources?: Source[];
  isError?: boolean;
};

const EXAMPLES = (name: string) => [
  `What are ${name}'s biggest risks?`,
  `What cybersecurity risks does ${name} disclose?`,
  "What supply-chain risks are mentioned?",
  "What changed compared with last year?",
  `What legal proceedings does ${name} disclose?`,
];

export function FilingChat({ company, shortName }: { company: Company; shortName: string }) {
  const [value, setValue] = useState("");
  const [focused, setFocused] = useState(false);
  const [busy, setBusy] = useState(false);
  const [turns, setTurns] = useState<Turn[]>([]);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const send = async (text: string) => {
    const q = text.trim();
    if (!q || busy) return;
    setBusy(true);
    setValue("");
    setTurns((t) => [...t, { role: "user", text: q }]);
    try {
      const res = await ask({ ticker: company.ticker, text: q });
      setTurns((t) => [...t, { role: "assistant", text: res.answer, sources: res.sources }]);
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : "An unexpected error occurred while processing the request.";
      setTurns((t) => [
        ...t,
        {
          role: "assistant",
          text: errorMessage,
          isError: true,
        },
      ]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <p className="label-mono">What can I ask?</p>
      <div className="mt-5 flex flex-wrap gap-2">
        {EXAMPLES(shortName).map((q) => (
          <button
            key={q}
            type="button"
            onClick={() => {
              setValue(q);
              inputRef.current?.focus();
            }}
            className="rounded-full border border-border bg-surface/40 px-4 py-1.5 text-left text-[0.78rem] text-muted-foreground transition-colors duration-300 hover:border-border-strong hover:bg-surface/70 hover:text-foreground"
          >
            {q}
          </button>
        ))}
      </div>

      {turns.length > 0 && (
        <div className="mt-10 space-y-6" aria-live="polite">
          {turns.map((t, i) =>
            t.role === "user" ? (
              <div key={i} className="flex justify-end">
                <p className="max-w-[85%] rounded-2xl bg-primary px-4 py-2.5 text-[0.9rem] text-primary-foreground">
                  {t.text}
                </p>
              </div>
            ) : (
              <div key={i} className="max-w-[92%]">
                {t.isError ? (
                  <div className="flex items-start gap-2 text-destructive">
                    <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                    <p className="text-[0.95rem] leading-relaxed">{t.text}</p>
                  </div>
                ) : (
                  <p className="text-[0.95rem] leading-relaxed whitespace-pre-wrap text-foreground">
                    {t.text}
                  </p>
                )}
                {t.sources && t.sources.length > 0 && (
                  <div className="mt-4">
                    <p className="label-mono">Sources</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {t.sources.map((s, idx) => {
                        const yearDisplay = s.fiscal_year || s.year || "";
                        const itemDisplay = s.section || s.item || "Filing";
                        const label = `${s.ticker} · ${yearDisplay} · ${itemDisplay}`;
                        return s.source_url ? (
                          <a
                            key={`${s.ticker}-${yearDisplay}-${itemDisplay}-${idx}`}
                            href={s.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="border border-border px-2.5 py-1 font-mono text-[0.68rem] tracking-[0.1em] text-signal transition-colors hover:border-signal"
                          >
                            {label} ↗
                          </a>
                        ) : (
                          <span
                            key={`${s.ticker}-${yearDisplay}-${itemDisplay}-${idx}`}
                            className="border border-border px-2.5 py-1 font-mono text-[0.68rem] tracking-[0.1em] text-muted-foreground"
                          >
                            {label}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            ),
          )}
          {busy && (
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 animate-ping rounded-full bg-signal" />
              <p className="text-sm text-muted-foreground">Reading filings…</p>
            </div>
          )}
        </div>
      )}

      <form
        className="mt-8"
        onSubmit={(e) => {
          e.preventDefault();
          void send(value);
        }}
      >
        <label htmlFor="filing-chat" className="sr-only">
          Ask a question about {company.name} filings
        </label>
        <HoverBorderGradient active={focused}>
          <div className="flex items-center gap-3 px-5 py-3">
            <MessageSquare aria-hidden className="h-4 w-4 shrink-0 text-muted-foreground" />
            <input
              id="filing-chat"
              ref={inputRef}
              value={value}
              disabled={busy}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              onChange={(e) => setValue(e.target.value)}
              placeholder={`Ask anything about ${shortName}'s filings...`}
              className="w-full bg-transparent text-[0.95rem] text-foreground placeholder:text-muted-foreground/70 focus:outline-none disabled:opacity-60"
            />
            <button
              type="submit"
              disabled={busy || !value.trim()}
              aria-label="Send question"
              className="hover-arrow inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-signal transition-colors hover:bg-secondary/70 disabled:opacity-40"
            >
              <ArrowRight className="arrow h-4 w-4" />
            </button>
          </div>
        </HoverBorderGradient>
      </form>
    </div>
  );
}
