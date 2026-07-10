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
  intent_tags?: string[];
  campaign_id?: string | null;
  kill_chain_stage?: string | null;
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
  intent_tags?: string[];
  campaign_id?: string | null;
  kill_chain_stage?: string | null;
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
  intent_tags?: string[];
  campaign_id?: string | null;
  kill_chain_stage?: string | null;
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

export class ApiError extends Error {
  status: number;
  detail?: string;
  constructor(status: number, detail?: string) {
    super(detail ?? `request_failed_${status}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

async function raiseForStatus(res: Response): Promise<void> {
  if (res.ok) return;
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("json")) {
    try {
      const body = (await res.json()) as { detail?: unknown };
      const detail = typeof body.detail === "string" ? body.detail : undefined;
      throw new ApiError(res.status, detail);
    } catch (err) {
      if (err instanceof ApiError) throw err;
    }
  }
  throw new ApiError(res.status);
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
  await raiseForStatus(res);
  return res.json() as Promise<T>;
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { headers: authHeaders() });
  await raiseForStatus(res);
  return res.json() as Promise<T>;
}

async function deleteJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  await raiseForStatus(res);
  return res.json() as Promise<T>;
}

async function deleteVoid(path: string): Promise<void> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  await raiseForStatus(res);
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

export async function fetchMeStats() {
  return getJson<{
    scans: number;
    threat_events: number;
    unread_notifications: number;
    domain_allowlist: number;
    risk_history: number;
    devices: number;
  }>("/v1/me/stats");
}

export async function analyzeBehavior(limit = 50) {
  return postJson<{
    score: number;
    verdict: string;
    confidence: number;
    recommended_action: string;
    reasons: { code: string; message_key: string }[];
    mitre_tags: string[];
    window: {
      scans: number;
      threat_events: number;
      malicious_scans: number;
      critical_events: number;
    };
  }>(`/v1/behavior/analyze?limit=${limit}`, {});
}

export async function fetchThreatEvents(severity?: string, mitre?: string) {
  const params = new URLSearchParams();
  if (severity) params.set("severity", severity);
  if (mitre) params.set("mitre", mitre);
  const q = params.toString() ? `?${params}` : "";
  return getJson<
    {
      event_id: string;
      category: string;
      severity: string;
      subject_hash: string;
      mitre_tags: string[];
      score: number | null;
      scam_family: string | null;
      detected_at: string;
    }[]
  >(`/v1/threat-events${q}`);
}

export async function eraseAccount(): Promise<{ status: string }> {
  return deleteJson("/v1/me");
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

export async function fetchScans(opts?: {
  verdict?: string;
  scan_type?: string;
  limit?: number;
}): Promise<ScanHistoryItem[]> {
  const params = new URLSearchParams();
  if (opts?.verdict) params.set("verdict", opts.verdict);
  if (opts?.scan_type) params.set("scan_type", opts.scan_type);
  if (opts?.limit) params.set("limit", String(opts.limit));
  const q = params.toString() ? `?${params}` : "";
  return getJson(`/v1/scans${q}`);
}

export async function pruneRiskHistory(retainDays = 180) {
  return postJson<{ deleted_risk_history: number; retain_days: number }>(
    `/v1/retention/prune?retain_days=${retainDays}`,
    {},
  );
}

export async function assessDeepfakeVoice(body: {
  duration_ms: number;
  sample_rate_hz?: number;
  filename_hint?: string;
}) {
  return postJson<{
    score: number;
    verdict: string;
    recommended_action: string;
    audio_stored: boolean;
  }>("/v1/deepfake/voice", body);
}

export async function fetchAudit(limit = 50) {
  return getJson<{ id: string; action: string; meta: Record<string, unknown>; at: string }[]>(
    `/v1/audit?limit=${limit}`,
  );
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

export async function setEmergencyConsent(granted: boolean): Promise<ConsentRecord> {
  return postJson<ConsentRecord>("/v1/emergency/consent", { granted, source: "ui" });
}

export type EmergencyConfirmResponse = {
  confirm_token: string;
  expires_at: string;
  modules: string[];
  requires_second_confirm: boolean;
};

export type EmergencyLogItem = {
  id: string;
  status: string;
  channel: string;
  evidence_code: string;
  modules: string[];
  confidence: number;
  dry_run: boolean;
  created_at: string;
};

export async function confirmEmergency(
  modules: string[],
  confidence: number,
  incidentRef?: string,
): Promise<EmergencyConfirmResponse> {
  return postJson("/v1/emergency/confirm", {
    modules,
    confidence,
    incident_ref: incidentRef ?? null,
  });
}

export async function dispatchEmergency(
  confirmToken: string,
  channel: "sms" | "api" | "email" = "api",
): Promise<EmergencyLogItem> {
  return postJson("/v1/emergency/dispatch", {
    confirm_token: confirmToken,
    channel,
  });
}

export async function fetchEmergencyLogs(): Promise<EmergencyLogItem[]> {
  return getJson("/v1/emergency/logs");
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

export async function reportSuspiciousMessage(
  text: string,
  source: "telegram_share" | "paste" | "sms_meta" = "paste",
  entities?: { urls?: string[]; bot_username?: string | null },
) {
  return postJson<{
    report_id: string;
    score: number;
    verdict: Verdict;
    scam_family: string | null;
    recommended_action: string;
    intent_tags: string[];
    campaign_id: string | null;
    preview: string;
    reasons: ScanReason[];
  }>("/v1/messages/suspicious", {
    text,
    source,
    entities: entities ?? { urls: [], bot_username: null },
  });
}

export async function breachCheck(email: string) {
  return postJson<{
    found: boolean;
    breach_count: number;
    breaches: { name: string; year: number; data_classes: string[] }[];
    recommendations: string[];
    email_hash_prefix: string;
  }>("/v1/breach-check", { email }, false);
}

export async function registerDevice(platform: "web" | "android" | "windows" | "extension" = "web") {
  const fingerprint =
    localStorage.getItem("cga_device_fp") ||
    (() => {
      const fp = `web-${crypto.randomUUID()}`;
      localStorage.setItem("cga_device_fp", fp);
      return fp;
    })();
  return postJson("/v1/devices/register", {
    platform,
    app_version: "0.3.0",
    device_label: "Browser",
    fingerprint,
  });
}

export async function fetchDevices() {
  return getJson<
    {
      id: string;
      platform: string;
      app_version: string;
      device_label: string | null;
      fingerprint: string;
      created_at: string;
      last_seen_at: string;
    }[]
  >("/v1/devices");
}

export async function revokeDevice(deviceId: string): Promise<void> {
  await deleteVoid(`/v1/devices/${deviceId}`);
}

export async function fetchNotifications(unreadOnly = false) {
  return getJson<
    {
      id: string;
      level: string;
      body_key: string;
      body_params: Record<string, unknown>;
      read_at: string | null;
      created_at: string;
    }[]
  >(`/v1/notifications?unread_only=${unreadOnly ? "true" : "false"}`);
}

export async function markNotificationRead(id: string) {
  return postJson(`/v1/notifications/${id}/read`, {});
}

export async function markAllNotificationsRead() {
  return postJson<{ updated: number }>("/v1/notifications/read-all", {});
}

export async function fetchSigmaRules() {
  return getJson<
    {
      id: string;
      title: string;
      version: string;
      status: string;
      mitre_tags: string[];
      platforms: string[];
    }[]
  >("/v1/sigma/rules");
}

export async function createReport(fromIso: string, toIso: string) {
  return postJson<{
    report_id: string;
    status: string;
    created_at: string;
    payload: unknown;
  }>("/v1/reports", {
    from: fromIso,
    to: toIso,
    types: ["scan", "threat_event"],
    format: "json",
    redact_pii: true,
  });
}

export async function passwordHealth(password: string) {
  return postJson<{
    score: number;
    verdict: string;
    pwned_local: boolean;
    reasons: { code: string; message_key: string }[];
    recommendations: string[];
  }>("/v1/password-health", { password }, false);
}

export async function fetchRiskHistory(limit = 50) {
  return getJson<
    {
      id: string;
      subject_type: string;
      subject_hash: string;
      score: number;
      confidence: number;
      model_version: string;
      created_at: string;
    }[]
  >(`/v1/risk-score/history?limit=${limit}`);
}

export async function dnsCheck(domain: string) {
  return postJson<{
    domain: string;
    verdict: string;
    score: number;
    allowlisted: boolean;
    recommended_action: string;
  }>("/v1/dns/check", { domain });
}

export async function fetchDnsAllowlist() {
  return getJson<{ id: string; domain: string; note: string | null; created_at: string }[]>(
    "/v1/dns/allowlist",
  );
}

export async function addDnsAllowlist(domain: string, note?: string) {
  return postJson<{ id: string; domain: string; note: string | null; created_at: string }>(
    "/v1/dns/allowlist",
    { domain, note },
  );
}

export async function removeDnsAllowlist(id: string) {
  return deleteVoid(`/v1/dns/allowlist/${id}`);
}

export async function sha256Hex(file: File): Promise<string> {
  const buffer = await file.arrayBuffer();
  const digest = await crypto.subtle.digest("SHA-256", buffer);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
