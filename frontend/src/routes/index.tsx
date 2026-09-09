import { createFileRoute } from "@tanstack/react-router";
import { ThemeProvider } from "@/lib/theme";
import { ParticleField } from "@/components/si/ParticleField";
import { Header, Footer } from "@/components/si/Chrome";
import { Hero } from "@/components/si/Hero";
import { Pipeline } from "@/components/si/Pipeline";
import { Capabilities } from "@/components/si/Capabilities";
import { FilingChat } from "@/components/si/FilingChat";
import { filingRange } from "@/lib/companies";
import { useCompanies } from "@/hooks/use-companies";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Filing Intelligence — Turn filings into intelligence" },
      {
        name: "description",
        content:
          "Automated extraction, analysis, and AI-powered answers from SEC 10-K filings: risk factors, legal proceedings and year-over-year risk changes.",
      },
      { property: "og:title", content: "Filing Intelligence — Turn filings into intelligence" },
      {
        property: "og:description",
        content: "AI-powered analysis of SEC 10-K filings with evidence-backed answers and source citations.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

function Index() {
  const { data: companies } = useCompanies();
  const apple = companies?.find((c) => c.ticker === "AAPL") ?? {
    ticker: "AAPL",
    name: "Apple Inc.",
    years: ["2022", "2023", "2024", "2025"],
  };

  return (
    <ThemeProvider>
      <div className="relative min-h-screen">
        <ParticleField />
        <Header />
        <main>
          <Hero />
          <Capabilities />
          <Pipeline />

          <section id="analyze" className="mx-auto max-w-6xl px-6 pb-40">
            <p className="label-mono">Company analysis</p>
            <div className="mt-10 grid gap-14 border border-border bg-background/60 p-8 backdrop-blur-sm md:grid-cols-12 md:p-12">
              <div className="md:col-span-4">
                <h2 className="text-2xl tracking-[-0.02em] sm:text-3xl">
                  {apple.name} <span className="text-muted-foreground">({apple.ticker})</span>
                </h2>
                <p className="mt-3 text-sm text-muted-foreground">{filingRange(apple)}</p>
                <span className="mt-8 inline-flex items-center gap-2 border border-border px-3 py-1.5 font-mono text-[0.62rem] tracking-[0.14em] text-muted-foreground uppercase">
                  <span className="h-1.5 w-1.5 rounded-full bg-signal" /> Filing data available
                </span>
                <div className="rule-line mt-8" />
                <p className="mt-6 max-w-[30ch] text-sm leading-relaxed text-muted-foreground">
                  A focused research workspace: ask a question, read the answer, follow the filing sources.
                </p>
              </div>
              <div className="md:col-span-7 md:col-start-6">
                <h3 className="text-xl tracking-[-0.01em]">What would you like to know?</h3>
                <div className="mt-8">
                  <FilingChat key={apple.ticker} company={apple} shortName="Apple" />
                </div>
              </div>
            </div>
          </section>
        </main>
        <Footer />
      </div>
    </ThemeProvider>
  );
}
