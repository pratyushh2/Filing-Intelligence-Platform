export type Company = {
  ticker: string;
  name: string;
  years: (string | number)[];
};

export const POPULAR_TICKERS = ["AAPL", "MSFT", "TSLA", "NVDA", "AMZN"];

export function searchCompanies(query: string, list: Company[] = []): Company[] {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  return list.filter(
    (c) => c.ticker.toLowerCase().includes(q) || c.name.toLowerCase().includes(q)
  );
}

export function findCompany(ticker: string, list: Company[] = []): Company | undefined {
  if (!ticker) return undefined;
  return list.find((c) => c.ticker.toLowerCase() === ticker.toLowerCase());
}

export function filingRange(c: Company): string {
  if (!c.years || c.years.length === 0) return "Annual filings";
  const first = c.years[0];
  const last = c.years[c.years.length - 1];
  if (first === last) return `Annual filing · ${first}`;
  return `Annual filings · ${first} — ${last}`;
}
