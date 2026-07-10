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

export type ScanResultView = {
  title: string;
  score: number;
  verdict: Verdict;
  recommended_action: string;
  scam_family: string | null;
  mitre_tags: string[];
  reasons: ScanReason[];
};

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`scan_failed_${res.status}`);
  }
  return res.json() as Promise<T>;
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
