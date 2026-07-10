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

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export async function scanUrl(url: string): Promise<UrlScanResponse> {
  const res = await fetch(`${API_BASE}/v1/scan/url`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ url, context: { source: "manual", client_cache_hit: false } }),
  });
  if (!res.ok) {
    throw new Error(`scan_failed_${res.status}`);
  }
  return res.json() as Promise<UrlScanResponse>;
}
