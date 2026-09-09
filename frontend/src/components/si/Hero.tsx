import { FilingArtifact } from "./FilingArtifact";
import { CompanySearch } from "./CompanySearch";

export function Hero() {
  return (
    <section id="top" className="relative flex min-h-[100svh] items-center pt-16">
      <div className="relative mx-auto w-full max-w-6xl px-6">
        <div className="grid items-center gap-12 md:grid-cols-12">
          <div className="md:col-span-7">
            <p className="text-[0.78rem] tracking-[0.1em] text-muted-foreground">Filing Intelligence</p>
            <h1 className="mt-8 max-w-3xl text-[2.6rem] leading-[1.04] tracking-[-0.03em] text-foreground sm:text-6xl lg:text-[4.2rem]">
              Turn filings into
              <br />
              <span className="text-muted-foreground">intelligence.</span>
            </h1>
            <p className="mt-8 max-w-md text-base leading-relaxed text-muted-foreground">
              Automated extraction, analysis, and AI-powered answers from SEC 10-K filings.
            </p>

            <div className="mt-12">
              <CompanySearch />
            </div>
          </div>

          <div className="pointer-events-none hidden md:col-span-5 md:block">
            <FilingArtifact className="mx-auto h-[62vh] w-full max-w-[340px] opacity-[0.55]" />
          </div>
        </div>
      </div>
    </section>
  );
}
