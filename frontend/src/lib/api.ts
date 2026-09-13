/**
 * Centralized API integration layer connecting the frontend to the FastAPI backend.
 * SEC, Groq, ChromaDB and embeddings are handled entirely server-side.
 */
import type { Company } from "./companies";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export type Source = {
  ticker: string;
  fiscal_year: string;
  section: string;
  text: string;
  source_url?: string | null;
  /** UI compatibility aliases */
  year?: string | number;
  item?: string;
};

export type AskRequest = {
  ticker: string;
  text: string;
};

export type AskResponse = {
  answer: string;
  ticker: string;
  sources: Source[];
};

export type DiffRequest = {
  ticker: string;
  year1: string;
  year2: string;
};

export type DiffChange = {
  type: string;
  topic: string;
  description: string;
};

export type DiffResponse = {
  ticker: string;
  year1: string;
  year2: string;
  summary: string;
  changes: DiffChange[];
  sources: Source[];
};

export type LitigationRequest = {
  query: string;
};

export type LitigationMatch = {
  ticker: string;
  fiscal_year: string;
  section: string;
  text: string;
};

export type LitigationResponse = {
  answer: string;
  matches: LitigationMatch[];
};

export type HealthResponse = {
  status: string;
  database: string;
  groq_configured: boolean;
};

/** GET /health */
export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) {
    throw new Error(`Health check failed with status ${res.status}`);
  }
  return (await res.json()) as HealthResponse;
}

/** GET /companies */
export async function getCompanies(): Promise<Company[]> {
  const res = await fetch(`${API_BASE_URL}/companies`);
  if (!res.ok) {
    throw new Error(`Failed to load companies (status ${res.status})`);
  }
  const data = (await res.json()) as Company[];
  return data;
}

/** POST /ask */
export async function ask({ ticker, text }: AskRequest): Promise<AskResponse> {
  const res = await fetch(`${API_BASE_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ticker: ticker.trim().toUpperCase(),
      text: text.trim(),
    }),
  });

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const err = await res.json();
      if (err?.detail) {
        detail = typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail);
      }
    } catch {
      // fallback to status text
    }
    throw new Error(detail);
  }

  const data = (await res.json()) as { answer: string; ticker: string; sources: Source[] };
  const normalizedSources: Source[] = (data.sources || []).map((s) => ({
    ticker: s.ticker,
    fiscal_year: s.fiscal_year,
    section: s.section,
    text: s.text,
    source_url: s.source_url ?? null,
    year: s.fiscal_year,
    item: s.section,
  }));

  return {
    answer: data.answer,
    ticker: data.ticker,
    sources: normalizedSources,
  };
}

/** POST /diff */
export async function diff(req: DiffRequest): Promise<DiffResponse> {
  const res = await fetch(`${API_BASE_URL}/diff`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ticker: req.ticker.trim().toUpperCase(),
      year1: String(req.year1).trim(),
      year2: String(req.year2).trim(),
    }),
  });

  if (!res.ok) {
    let detail = `Diff request failed (${res.status})`;
    try {
      const err = await res.json();
      if (err?.detail) {
        detail = typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail);
      }
    } catch {
      // fallback to status
    }
    throw new Error(detail);
  }

  return (await res.json()) as DiffResponse;
}

/** POST /litigation */
export async function scanLitigation(req: LitigationRequest): Promise<LitigationResponse> {
  const res = await fetch(`${API_BASE_URL}/litigation`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: req.query.trim(),
    }),
  });

  if (!res.ok) {
    let detail = `Litigation scan failed (${res.status})`;
    try {
      const err = await res.json();
      if (err?.detail) {
        detail = typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail);
      }
    } catch {
      // fallback to status
    }
    throw new Error(detail);
  }

  return (await res.json()) as LitigationResponse;
}
