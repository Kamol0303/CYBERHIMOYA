export type Verdict = "malicious" | "suspicious" | "clean" | "unknown";

export type ScanReason = {
  code: string;
  message_key: string;
};

export type UrlScanResponse = {
  scan_id: string;
  url_normalized: string;
  score: number;
  confidence: number;
  verdict: Verdict;
  reasons: ScanReason[];
  mitre_tags: string[];
  scam_family: string | null;
  actor_hint: string | null;
  recommended_action: string;
  scanned_at: string;
};

export type QrScanResponse = {
  scan_id: string;
  qr_type: string;
  payload_preview: string;
  url_normalized: string | null;
  score: number;
  confidence: number;
  verdict: Verdict;
  reasons: ScanReason[];
  mitre_tags: string[];
  scam_family: string | null;
  actor_hint: string | null;
  recommended_action: string;
  scanned_at: string;
};

export type FileScanResponse = {
  scan_id: string;
  sha256: string;
  file_name: string | null;
  score: number;
  confidence: number;
  verdict: Verdict;
  ti_hits: { source: string; tag: string }[];
  yara_matches: { rule: string; namespace: string }[];
  reasons: ScanReason[];
  mitre_tags: string[];
  scam_family: string | null;
  recommended_action: string;
  scanned_at: string;
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
};

export type UserProfile = {
  id: string;
  email: string;
  role: string;
  locale: string;
  created_at: string;
};

export type ConsentRecord = {
  id: string;
  user_id: string;
  consent_type: string;
  granted: boolean;
  changed_at: string;
  source: string;
};

export type ScanHistoryItem = {
  scan_id: string;
  scan_type: string;
  score: number;
  verdict: string;
  subject_hash: string;
  mitre_tags: string[];
  scam_family: string | null;
  recommended_action: string | null;
  created_at: string;
};

const API_BASE = import.meta.env.VITE_API_BASE ?? "";
const TOKEN_KEY = "cga_access_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

function authHeaders(): HeadersInit {
  const token = getToken();
  return token
    ? { Authorization: `Bearer ${token}`, Accept: "application/json" }
    : { Accept: "application/json" };
}

async function postJson<T>(path: string, body: unknown, withAuth = true): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };
  if (withAuth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`request_failed_${res.status}`);
  }
  return res.json() as Promise<T>;
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { headers: authHeaders() });
  if (!res.ok) throw new Error(`request_failed_${res.status}`);
  return res.json() as Promise<T>;
}

export async function register(
  email: string,
  password: string,
  locale: string,
): Promise<TokenResponse> {
  return postJson("/v1/auth/register", { email, password, locale }, false);
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  return postJson("/v1/auth/token", { email, password }, false);
}

export async function fetchMe(): Promise<UserProfile> {
  return getJson("/v1/me");
}

export async function fetchConsents(): Promise<ConsentRecord[]> {
  return getJson("/v1/consents");
}

export async function upsertConsent(
  consent_type: string,
  granted: boolean,
): Promise<ConsentRecord> {
  return postJson("/v1/consents", { consent_type, granted, source: "ui" });
}

export async function fetchScans(): Promise<ScanHistoryItem[]> {
  return getJson("/v1/scans");
}

export type ThreatFeedSync = {
  version: string;
  delta_url: string | null;
  signature: string;
  algorithm: string;
  item_counts: Record<string, number>;
};

export async function fetchThreatFeedSync(): Promise<ThreatFeedSync> {
  return getJson("/v1/threat-feed/sync");
}

export type EmergencyAllowlist = {
  aq039_resolved: boolean;
  dry_run_forced: boolean;
  sms_destinations_configured: number;
  api_endpoints_configured: number;
  email_destinations_configured: number;
  note: string;
  defensive_only: boolean;
};

export async function fetchEmergencyAllowlist(): Promise<EmergencyAllowlist> {
  return getJson("/v1/emergency/allowlist");
}

export async function setEmergencyConsent(granted: boolean) {
  return postJson("/v1/emergency/consent", { granted, source: "ui" });
}

export async function scanUrl(url: string): Promise<UrlScanResponse> {
  return postJson("/v1/scan/url", {
    url,
    context: { source: "manual", client_cache_hit: false },
  });
}

export async function scanQr(payloadText: string): Promise<QrScanResponse> {
  return postJson("/v1/scan/qr", { payload_text: payloadText });
}

export async function scanFileHash(
  sha256: string,
  fileName?: string,
): Promise<FileScanResponse> {
  return postJson("/v1/scan/file", { sha256, file_name: fileName ?? null, run_yara: false });
}

export async function sha256Hex(file: File): Promise<string> {
  const buffer = await file.arrayBuffer();
  const digest = await crypto.subtle.digest("SHA-256", buffer);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
