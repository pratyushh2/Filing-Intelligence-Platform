import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { ArrowRight, Search } from "lucide-react";
import { HoverBorderGradient } from "@/components/ui/hover-border-gradient";
import { POPULAR_TICKERS, filingRange, searchCompanies, type Company } from "@/lib/companies";
import { useCompanies } from "@/hooks/use-companies";

export function CompanySearch() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [focused, setFocused] = useState(false);
  const [index, setIndex] = useState(0);
  const wrapRef = useRef<HTMLDivElement | null>(null);

  const { data: companies = [] } = useCompanies();

  const results = useMemo(() => searchCompanies(query, companies), [query, companies]);

  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  const go = (ticker: string) => {
    setOpen(false);
    setQuery("");
    navigate({ to: "/company/$ticker", params: { ticker: ticker.toUpperCase() } });
  };

  const submit = () => {
    const pick = results[index] ?? results[0];
    if (pick) go(pick.ticker);
  };

  return (
    <div ref={wrapRef} className="relative w-full max-w-xl">
      <label htmlFor="company-search" className="label-mono block">
        Find a company
      </label>

      <HoverBorderGradient active={focused} containerClassName="mt-3" className="rounded-full">
        <div className="flex items-center gap-3 px-5 py-3">
          <Search aria-hidden className="h-4 w-4 shrink-0 text-muted-foreground" />
          <input
            id="company-search"
            type="text"
            role="combobox"
            aria-expanded={open && results.length > 0}
            aria-controls="company-search-results"
            autoComplete="off"
            placeholder="Search company or ticker (e.g., AAPL, Microsoft...)"
            value={query}
            onFocus={() => {
              setFocused(true);
              setOpen(true);
            }}
            onBlur={() => setFocused(false)}
            onChange={(e) => {
              setQuery(e.target.value);
              setIndex(0);
              setOpen(true);
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter") submit();
              if (e.key === "Escape") setOpen(false);
              if (e.key === "ArrowDown") {
                e.preventDefault();
                setIndex((i) => Math.min(results.length - 1, i + 1));
              }
              if (e.key === "ArrowUp") {
                e.preventDefault();
                setIndex((i) => Math.max(0, i - 1));
              }
            }}
            className="w-full bg-transparent text-[0.95rem] text-foreground placeholder:text-muted-foreground/70 focus:outline-none"
          />
          <button
            type="button"
            onClick={submit}
            aria-label="Open company analysis"
            className="hover-arrow inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-signal transition-colors hover:bg-secondary/70"
          >
            <ArrowRight className="arrow h-4 w-4" />
          </button>
        </div>
      </HoverBorderGradient>

      {open && results.length > 0 && (
        <ul
          id="company-search-results"
          role="listbox"
          className="animate-fade-in absolute z-30 mt-2 w-full overflow-hidden rounded-md border border-border bg-popover/95 backdrop-blur-md"
        >
          {results.map((c, i) => (
            <li key={c.ticker} role="option" aria-selected={i === index}>
              <button
                type="button"
                onMouseEnter={() => setIndex(i)}
                onClick={() => go(c.ticker)}
                className={`flex w-full items-baseline justify-between gap-4 px-5 py-3 text-left transition-colors ${
                  i === index ? "bg-secondary/70" : "hover:bg-secondary/50"
                }`}
              >
                <span className="text-[0.9rem] text-foreground">{c.name}</span>
                <span className="font-mono text-[0.7rem] tracking-[0.12em] text-signal">{c.ticker}</span>
              </button>
            </li>
          ))}
        </ul>
      )}

      <div className="mt-5 flex flex-wrap items-center gap-2.5">
        <span className="label-mono">Popular</span>
        {POPULAR_TICKERS.map((t) => {
          const c = companies.find((x) => x.ticker === t);
          return (
            <button
              key={t}
              type="button"
              onClick={() => go(t)}
              title={c ? `${c.name} · ${filingRange(c)}` : t}
              className="inline-flex cursor-pointer items-center rounded-full border border-border bg-surface/40 px-4 py-1.5 font-mono text-[0.72rem] tracking-[0.1em] text-muted-foreground transition-colors duration-300 hover:border-border-strong hover:bg-surface/70 hover:text-foreground"
            >
              {t}
            </button>
          );
        })}
      </div>
    </div>
  );
}
