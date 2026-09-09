import { createFileRoute, Link } from "@tanstack/react-router";
import { ThemeProvider } from "@/lib/theme";
import { ParticleField } from "@/components/si/ParticleField";
import { Header, Footer } from "@/components/si/Chrome";
import { FilingChat } from "@/components/si/FilingChat";
import { ImagesBadge } from "@/components/ui/images-badge";
import { filingDocSets } from "@/components/si/FilingDocs";
import { filingRange } from "@/lib/companies";
import { useCompanies } from "@/hooks/use-companies";

export const Route = createFileRoute("/company/$ticker")({
  head: ({ params }) => {
    const t = params.ticker.toUpperCase();
    const title = `${t} filings — Filing Intelligence`;
    const description = `Ask questions about ${t} SEC 10-K filings: risk factors, legal proceedings and year-over-year risk changes.`;
    return {
      meta: [
        { title },
        { name: "description", content: description },
        { property: "og:title", content: title },
        { property: "og:description", content: description },
        { property: "og:type", content: "website" },
        { name: "twitter:card", content: "summary_large_image" },
      ],
    };
  },
  component: CompanyPage,
});

const focus = [
  { key: "risk", title: "Risk Factors", copy: "Item 1A risk disclosures and key risks." },
  { key: "legal", title: "Legal Proceedings", copy: "Lawsuits, litigation and legal matters." },
  { key: "changes", title: "Risk Changes", copy: "Year-over-year risk comparison." },
  { key: "ai", title: "AI Insights", copy: "Evidence-backed answers with sources." },
] as const;

function CompanyPage() {
  const { ticker } = Route.useParams();
  const upperTicker = ticker.toUpperCase();
  const { data: companies, isLoading } = useCompanies();
  const company = companies?.find((c) => c.ticker.toUpperCase() === upperTicker);

  return (
    <ThemeProvider>
      <div className="relative min-h-screen">
        <ParticleField />
        <Header />
        <main className="mx-auto max-w-6xl px-6 pt-32 pb-32">
          {isLoading ? (
            <div>
              <p className="label-mono">Loading</p>
              <h1 className="mt-6 text-3xl tracking-[-0.02em]">Retrieving filing records for “{upperTicker}”…</h1>
            </div>
          ) : !company ? (
            <div>
              <p className="label-mono">Not tracked</p>
              <h1 className="mt-6 text-3xl tracking-[-0.02em]">No filings for “{upperTicker}”</h1>
              <p className="mt-4 max-w-md text-muted-foreground">
                This company is not currently indexed in the SEC filing database.
              </p>
              <Link to="/" className="hover-arrow mt-8 inline-flex items-center gap-2 text-sm text-foreground">
                Back to search <span className="arrow font-mono text-signal">→</span>
              </Link>
            </div>
          ) : (
            <>
              <Link
                to="/"
                className="label-mono inline-flex items-center gap-2 transition-colors hover:text-foreground"
              >
                ← Search
              </Link>

              <div className="mt-8 grid gap-14 md:grid-cols-12">
                <div className="md:col-span-4">
                  <h1 className="text-3xl tracking-[-0.025em] sm:text-4xl">{company.name || company.ticker}</h1>
                  <p className="mt-3 font-mono text-[0.75rem] tracking-[0.14em] text-signal">{company.ticker}</p>
                  <p className="mt-4 text-sm text-muted-foreground">{filingRange(company)}</p>
                  <span className="mt-8 inline-flex items-center gap-2 border border-border px-3 py-1.5 font-mono text-[0.62rem] tracking-[0.14em] text-muted-foreground uppercase">
                    <span className="h-1.5 w-1.5 rounded-full bg-signal" /> Filing data available
                  </span>
                  <div className="rule-line mt-8" />
                  <ul className="mt-6 space-y-2 text-sm text-muted-foreground">
                    {company.years.map((y) => (
                      <li key={y} className="flex items-center gap-3">
                        <span className="h-px w-6 bg-border-strong" />
                        <span className="font-mono text-[0.72rem] tracking-[0.1em]">{y} · 10-K</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="md:col-span-7 md:col-start-6">
                  <h2 className="text-xl tracking-[-0.01em]">What would you like to know?</h2>
                  <div className="mt-8">
                    <FilingChat
                      key={company.ticker}
                      company={company}
                      shortName={company.name ? company.name.split(/[ ,.]/)[0]! : company.ticker}
                    />
                  </div>
                </div>
              </div>

              <div className="mt-32">
                <p className="label-mono">Focus areas</p>
                <div className="mt-16 grid gap-y-24 gap-x-10 sm:grid-cols-2 lg:grid-cols-4">
                  {focus.map((f) => (
                    <div key={f.key} className="group">
                      <div className="flex min-h-[130px] items-end justify-center">
                        <ImagesBadge images={filingDocSets[f.key]!.map((d) => d.node)} />
                      </div>
                      <div className="mt-8">
                        <div className="rule-line" />
                        <h3 className="mt-5 text-base text-muted-foreground transition-colors group-hover:text-foreground">
                          {f.title}
                        </h3>
                        <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{f.copy}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </main>
        <Footer />
      </div>
    </ThemeProvider>
  );
}
