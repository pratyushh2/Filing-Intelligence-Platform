import type { Company } from "./companies";

export const API_BASE_URL = import.meta.env["VITE_API_BASE_URL"] ?? "http://localhost:8000";

export type Source = {
  ticker: string;
  fiscal_year: string;
  section: string;
  text: string;
  source_url?: string | null;
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

export type DiffChange = {
  type: string; // "added" | "removed" | "changed"
  topic: string;
  description: string;
};

export type DiffRequest = {
  ticker: string;
  year1: string;
  year2: string;
};

export type DiffResponse = {
  ticker: string;
  year1: string;
  year2: string;
  summary: string;
  changes: DiffChange[];
  sources: Source[];
};

export type LitigationMatch = {
  ticker: string;
  fiscal_year: string;
  section: string;
  text: string;
};

export type LitigationRequest = {
  query: string;
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

export async function health(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) {
    throw new Error(`Health check failed: HTTP ${res.status}`);
  }
  return res.json();
}

export async function getCompanies(): Promise<Company[]> {
  const res = await fetch(`${API_BASE_URL}/companies`);
  if (!res.ok) {
    throw new Error(`Failed to load companies: HTTP ${res.status}`);
  }
  return res.json();
}

export async function ask(req: AskRequest): Promise<AskResponse> {
  const normalized = req.text.trim().toLowerCase().replace(/^[\s.,!?;:'"“”]+|[\s.,!?;:'"“”]+$/g, "");
  const tickerUpper = req.ticker.trim().toUpperCase();

  const greetings = new Set([
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "greetings",
    "howdy",
  ]);

  const helpQueries = new Set([
    "what type of questions can i ask",
    "what can i ask",
    "what questions can i ask",
    "help",
    "what can you do",
    "how does this work",
    "how do i use this",
    "what do you do",
  ]);

  if (greetings.has(normalized)) {
    return {
      answer: "Hi! I'm Filing Intelligence. Ask me about a company's SEC filings, risks, legal proceedings, or changes between filings.",
      ticker: tickerUpper,
      sources: [],
    };
  }

  if (helpQueries.has(normalized)) {
    return {
      answer: `I can help you analyze SEC filings and uncover insights. Here are some examples of what you can ask:\n\n- What are ${tickerUpper}'s biggest business risks?\n- What cybersecurity risks does ${tickerUpper} disclose?\n- What does ${tickerUpper} say about its supply chain?\n- How have the legal proceedings changed since last year?`,
      ticker: tickerUpper,
      sources: [],
    };
  }

  const res = await fetch(`${API_BASE_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ticker: tickerUpper,
      text: req.text.trim(),
    }),
  });
  if (!res.ok) {
    let detail = "";
    try {
      const err = await res.json();
      detail = err.detail || "";
    } catch {
      // ignore
    }
    throw new Error(detail || `Request failed with HTTP ${res.status}`);
  }
  return res.json();
}

export async function diff(req: DiffRequest): Promise<DiffResponse> {
  const res = await fetch(`${API_BASE_URL}/diff`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    let detail = "";
    try {
      const err = await res.json();
      detail = err.detail || "";
    } catch {
      // ignore
    }
    throw new Error(detail || `Risk diff request failed with HTTP ${res.status}`);
  }
  return res.json();
}

export async function litigation(req: LitigationRequest): Promise<LitigationResponse> {
  const res = await fetch(`${API_BASE_URL}/litigation`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    let detail = "";
    try {
      const err = await res.json();
      detail = err.detail || "";
    } catch {
      // ignore
    }
    throw new Error(detail || `Litigation search failed with HTTP ${res.status}`);
  }
  return res.json();
}
