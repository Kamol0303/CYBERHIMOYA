import { useEffect, useState, type FormEvent } from "react";
import {
  ApiError,
  confirmEmergency,
  dispatchEmergency,
  eraseAccount,
  fetchConsents,
  fetchDevices,
  fetchEmergencyAllowlist,
  fetchEmergencyLogs,
  fetchMe,
  fetchNotifications,
  fetchScans,
  fetchThreatEvents,
  fetchThreatFeedSync,
  createReport,
  markNotificationRead,
  passwordHealth,
  fetchRiskHistory,
  dnsCheck,
  fetchDnsAllowlist,
  addDnsAllowlist,
  removeDnsAllowlist,
  getToken,
  login,
  register,
  registerDevice,
  reportSuspiciousMessage,
  revokeDevice,
  breachCheck,
  scanFileHash,
  scanQr,
  scanUrl,
  setEmergencyConsent,
  setToken,
  sha256Hex,
  upsertConsent,
  type ConsentRecord,
  type EmergencyAllowlist,
  type EmergencyLogItem,
  type ScanHistoryItem,
  type ScanReason,
  type ThreatFeedSync,
  type UserProfile,
  type Verdict,
} from "./lib/api";
import { locales, t, tCode, type Locale } from "./i18n/messages";
import {
  clearGuestHistory,
  loadGuestHistory,
  pushGuestScan,
  type GuestScanItem,
} from "./lib/guestHistory";
import "./App.css";

type ScanMode = "url" | "qr" | "file";
type View = "scan" | "dashboard" | "auth";

type ResultView = {
  title: string;
  score: number;
  verdict: Verdict;
  recommended_action: string;
  scam_family: string | null;
  mitre_tags: string[];
  reasons: ScanReason[];
  intent_tags?: string[];
  campaign_id?: string | null;
  actor_hint?: string | null;
};

function verdictLabel(locale: Locale, verdict: Verdict): string {
  return t(locale, verdict);
}

function scanErrorMessage(locale: Locale, err: unknown): string {
  if (err instanceof ApiError && err.status === 429) {
    return err.detail?.trim() || t(locale, "rateLimited");
  }
  if (err instanceof ApiError && err.detail?.trim()) {
    return err.detail;
  }
  return t(locale, "error");
}

export default function App() {
  const [locale, setLocale] = useState<Locale>("uz");
  const [mode, setMode] = useState<ScanMode>("url");
  const [url, setUrl] = useState("");
  const [qrPayload, setQrPayload] = useState("");
  const [fileLabel, setFileLabel] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ResultView | null>(null);
  const [view, setView] = useState<View>("scan");
  const [user, setUser] = useState<UserProfile | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState<string | null>(null);
  const [history, setHistory] = useState<ScanHistoryItem[]>([]);
  const [consents, setConsents] = useState<ConsentRecord[]>([]);
  const [feed, setFeed] = useState<ThreatFeedSync | null>(null);
  const [emergency, setEmergency] = useState<EmergencyAllowlist | null>(null);
  const [emergencyLogs, setEmergencyLogs] = useState<EmergencyLogItem[]>([]);
  const [confirmToken, setConfirmToken] = useState<string | null>(null);
  const [emergencyMsg, setEmergencyMsg] = useState<string | null>(null);
  const [emergencyBusy, setEmergencyBusy] = useState(false);
  const [online, setOnline] = useState(
    typeof navigator === "undefined" ? true : navigator.onLine,
  );
  const [erasureMsg, setErasureMsg] = useState<string | null>(null);
  const [erasureBusy, setErasureBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [msgText, setMsgText] = useState("");
  const [msgPreviewOk, setMsgPreviewOk] = useState(false);
  const [msgResult, setMsgResult] = useState<string | null>(null);
  const [breachEmail, setBreachEmail] = useState("");
  const [breachResult, setBreachResult] = useState<string | null>(null);
  const [devices, setDevices] = useState<{ id: string; platform: string; app_version: string }[]>(
    [],
  );
  const [guestHistory, setGuestHistory] = useState<GuestScanItem[]>([]);
  const [deviceBusy, setDeviceBusy] = useState<string | null>(null);
  const [threatEvents, setThreatEvents] = useState<
    { event_id: string; category: string; severity: string; score: number | null }[]
  >([]);
  const [notifications, setNotifications] = useState<
    { id: string; level: string; body_key: string; read_at: string | null }[]
  >([]);
  const [reportMsg, setReportMsg] = useState<string | null>(null);
  const [pwdInput, setPwdInput] = useState("");
  const [pwdResult, setPwdResult] = useState<string | null>(null);
  const [riskHistory, setRiskHistory] = useState<
    { id: string; subject_type: string; score: number; created_at: string }[]
  >([]);
  const [dnsDomain, setDnsDomain] = useState("");
  const [dnsResult, setDnsResult] = useState<string | null>(null);
  const [dnsAllowlist, setDnsAllowlist] = useState<
    { id: string; domain: string; note: string | null }[]
  >([]);

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  useEffect(() => {
    const on = () => setOnline(true);
    const off = () => setOnline(false);
    window.addEventListener("online", on);
    window.addEventListener("offline", off);
    return () => {
      window.removeEventListener("online", on);
      window.removeEventListener("offline", off);
    };
  }, []);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setGuestHistory(loadGuestHistory());
      return;
    }
    void fetchMe()
      .then(async (me) => {
        setUser(me);
        clearGuestHistory();
        setGuestHistory([]);
        await registerDevice("web").catch(() => undefined);
      })
      .catch(() => setToken(null));
  }, []);

  async function refreshDashboard() {
    if (!getToken()) {
      setHistory([]);
      setConsents([]);
      return;
    }
    const [
      scans,
      consentRows,
      feedSync,
      allowlist,
      emLogs,
      deviceRows,
      events,
      notifs,
      risks,
      dnsRows,
    ] = await Promise.all([
      fetchScans(),
      fetchConsents(),
      fetchThreatFeedSync(),
      fetchEmergencyAllowlist(),
      fetchEmergencyLogs(),
      fetchDevices().catch(() => []),
      fetchThreatEvents().catch(() => []),
      fetchNotifications().catch(() => []),
      fetchRiskHistory().catch(() => []),
      fetchDnsAllowlist().catch(() => []),
    ]);
    setHistory(scans);
    setConsents(consentRows);
    setFeed(feedSync);
    setEmergency(allowlist);
    setEmergencyLogs(emLogs);
    setDevices(deviceRows);
    setThreatEvents(events);
    setNotifications(notifs);
    setRiskHistory(risks);
    setDnsAllowlist(dnsRows);
  }

  useEffect(() => {
    if (view === "dashboard" && user) {
      void refreshDashboard().catch(() => undefined);
    }
  }, [view, user]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (mode === "url" && !url.trim()) return;
    if (mode === "qr" && !qrPayload.trim()) return;
    setLoading(true);
    setError(null);
    try {
      if (mode === "url") {
        const data = await scanUrl(url.trim());
        setResult({
          title: data.url_normalized,
          score: data.score,
          verdict: data.verdict,
          recommended_action: data.recommended_action,
          scam_family: data.scam_family,
          mitre_tags: data.mitre_tags,
          reasons: data.reasons,
          intent_tags: data.intent_tags,
          campaign_id: data.campaign_id,
          actor_hint: data.actor_hint,
        });
        if (!getToken()) {
          setGuestHistory(
            pushGuestScan({
              mode: "url",
              title: data.url_normalized,
              score: data.score,
              verdict: data.verdict,
              scanned_at: new Date().toISOString(),
            }),
          );
        }
      } else if (mode === "qr") {
        const data = await scanQr(qrPayload.trim());
        setResult({
          title: data.url_normalized ?? `${data.qr_type}: ${data.payload_preview}`,
          score: data.score,
          verdict: data.verdict,
          recommended_action: data.recommended_action,
          scam_family: data.scam_family,
          mitre_tags: data.mitre_tags,
          reasons: data.reasons,
          intent_tags: data.intent_tags,
          campaign_id: data.campaign_id,
          actor_hint: data.actor_hint,
        });
        if (!getToken()) {
          setGuestHistory(
            pushGuestScan({
              mode: "qr",
              title: data.url_normalized ?? data.payload_preview,
              score: data.score,
              verdict: data.verdict,
              scanned_at: new Date().toISOString(),
            }),
          );
        }
      }
    } catch (err) {
      setError(scanErrorMessage(locale, err));
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  async function onFileChange(file: File | null) {
    if (!file) return;
    setFileLabel(file.name);
    setLoading(true);
    setError(null);
    try {
      const hash = await sha256Hex(file);
      const data = await scanFileHash(hash, file.name);
      setResult({
        title: `${file.name} · ${data.sha256.slice(0, 16)}…`,
        score: data.score,
        verdict: data.verdict,
        recommended_action: data.recommended_action,
        scam_family: data.scam_family,
        mitre_tags: data.mitre_tags,
        reasons: data.reasons,
        intent_tags: data.intent_tags,
        campaign_id: data.campaign_id,
      });
      if (!getToken()) {
        setGuestHistory(
          pushGuestScan({
            mode: "file",
            title: file.name,
            score: data.score,
            verdict: data.verdict,
            scanned_at: new Date().toISOString(),
          }),
        );
      }
    } catch (err) {
      setError(scanErrorMessage(locale, err));
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  async function onAuth(kind: "login" | "register") {
    setAuthError(null);
    try {
      const tokens =
        kind === "login"
          ? await login(email.trim(), password)
          : await register(email.trim(), password, locale);
      setToken(tokens.access_token);
      const me = await fetchMe();
      setUser(me);
      clearGuestHistory();
      setGuestHistory([]);
      void registerDevice("web").catch(() => undefined);
      setPassword("");
      setView("dashboard");
    } catch {
      setAuthError(t(locale, "authError"));
    }
  }

  function onLogout() {
    setToken(null);
    setUser(null);
    setHistory([]);
    setConsents([]);
    setView("scan");
  }

  async function onEraseAccount() {
    if (!window.confirm(t(locale, "erasureConfirm"))) return;
    setErasureBusy(true);
    setErasureMsg(null);
    try {
      await eraseAccount();
      onLogout();
      setNotice(t(locale, "erasureDone"));
    } catch {
      setErasureMsg(t(locale, "erasureFail"));
    } finally {
      setErasureBusy(false);
    }
  }

  async function toggleConsent(type: string, granted: boolean) {
    const row = await upsertConsent(type, granted);
    setConsents((prev) => {
      const rest = prev.filter((c) => c.consent_type !== type);
      return [...rest, row];
    });
  }

  async function onEmergencyConfirm() {
    if (!consentGranted("emergency_law_enforcement")) {
      setEmergencyMsg(t(locale, "emergencyNeedConsent"));
      return;
    }
    setEmergencyBusy(true);
    setEmergencyMsg(null);
    try {
      const res = await confirmEmergency(
        ["url_scan", "file_hash", "sms_local"],
        0.95,
        "web-dry-run",
      );
      setConfirmToken(res.confirm_token);
      setEmergencyMsg(`${t(locale, "emergencyConfirm")}: OK`);
    } catch {
      setEmergencyMsg(t(locale, "emergencyFail"));
    } finally {
      setEmergencyBusy(false);
    }
  }

  async function onEmergencyDispatch() {
    if (!confirmToken) return;
    setEmergencyBusy(true);
    setEmergencyMsg(null);
    try {
      const row = await dispatchEmergency(confirmToken, "api");
      setConfirmToken(null);
      setEmergencyMsg(`${t(locale, "emergencyOk")} ${row.evidence_code}`);
      const logs = await fetchEmergencyLogs();
      setEmergencyLogs(logs);
    } catch {
      setEmergencyMsg(t(locale, "emergencyFail"));
    } finally {
      setEmergencyBusy(false);
    }
  }

  function consentGranted(type: string): boolean {
    return consents.find((c) => c.consent_type === type)?.granted === true;
  }

  const canSubmit =
    mode === "url" ? Boolean(url.trim()) : mode === "qr" ? Boolean(qrPayload.trim()) : false;

  return (
    <div className="shell">
      {!online ? (
        <div className="offline-banner" role="status">
          {t(locale, "offlineBanner")}
        </div>
      ) : null}
      <header className="topbar">
        <nav className="nav">
          <button
            type="button"
            className={view === "scan" ? "nav-link active" : "nav-link"}
            onClick={() => setView("scan")}
          >
            {t(locale, "cta")}
          </button>
          <button
            type="button"
            className={view === "dashboard" ? "nav-link active" : "nav-link"}
            onClick={() => setView(user ? "dashboard" : "auth")}
          >
            {t(locale, "dashboard")}
          </button>
          <button
            type="button"
            className={view === "auth" ? "nav-link active" : "nav-link"}
            onClick={() => (user ? onLogout() : setView("auth"))}
          >
            {user ? t(locale, "logout") : t(locale, "auth")}
          </button>
        </nav>
        <label className="lang">
          <span>{t(locale, "lang")}</span>
          <select
            value={locale}
            onChange={(e) => setLocale(e.target.value as Locale)}
            aria-label={t(locale, "lang")}
          >
            {locales.map((l) => (
              <option key={l} value={l}>
                {l.toUpperCase()}
              </option>
            ))}
          </select>
        </label>
      </header>

      {view === "scan" ? (
        <main className="hero">
          <div className="hero-copy">
            <p className="brand">{t(locale, "brand")}</p>
            <h1>{t(locale, "tagline")}</h1>
            <p className="support">{t(locale, "support")}</p>

            <div className="mode-tabs" role="tablist" aria-label="scan mode">
              {(["url", "qr", "file"] as ScanMode[]).map((m) => (
                <button
                  key={m}
                  type="button"
                  role="tab"
                  aria-selected={mode === m}
                  className={mode === m ? "mode active" : "mode"}
                  onClick={() => {
                    setMode(m);
                    setResult(null);
                    setError(null);
                  }}
                >
                  {t(locale, m === "url" ? "modeUrl" : m === "qr" ? "modeQr" : "modeFile")}
                </button>
              ))}
            </div>

            {mode === "file" ? (
              <div className="scan-form">
                <label className="file-pick">
                  <span>{fileLabel || t(locale, "placeholderFile")}</span>
                  <input
                    type="file"
                    onChange={(e) => void onFileChange(e.target.files?.[0] ?? null)}
                    disabled={loading}
                  />
                </label>
              </div>
            ) : (
              <form className="scan-form" onSubmit={onSubmit}>
                <input
                  value={mode === "url" ? url : qrPayload}
                  onChange={(e) =>
                    mode === "url" ? setUrl(e.target.value) : setQrPayload(e.target.value)
                  }
                  placeholder={t(locale, mode === "url" ? "placeholder" : "placeholderQr")}
                  aria-label={mode === "url" ? "URL" : "QR"}
                  autoComplete={mode === "url" ? "url" : "off"}
                  inputMode={mode === "url" ? "url" : "text"}
                />
                <button type="submit" disabled={loading || !canSubmit}>
                  {loading ? t(locale, "scanning") : t(locale, "cta")}
                </button>
              </form>
            )}

            <p className="note">{t(locale, "guestNote")}</p>
            {!user && guestHistory.length > 0 ? (
              <section className="history-block" style={{ marginTop: "1rem" }}>
                <h2 style={{ fontSize: "1rem" }}>{t(locale, "guestHistoryTitle")}</h2>
                <p className="note">{t(locale, "guestHistoryHint")}</p>
                <ul className="history-list">
                  {guestHistory.map((item) => (
                    <li key={`${item.scanned_at}-${item.title}`}>
                      <span className={`score score-${item.verdict}`}>{item.score}</span>
                      <span>{item.title}</span>
                      <span className="hash">{item.mode}</span>
                    </li>
                  ))}
                </ul>
              </section>
            ) : null}
            <p className="privacy">{t(locale, "privacy")}</p>
            {notice ? <p className="note">{notice}</p> : null}
            {error ? <p className="error">{error}</p> : null}
            {result ? (
              <section className="result" aria-live="polite">
                <h2>{t(locale, "result")}</h2>
                <p className="normalized">{result.title}</p>
                <dl className="meta">
                  <div>
                    <dt>{t(locale, "score")}</dt>
                    <dd>
                      <span className={`score score-${result.verdict}`}>{result.score}</span>
                    </dd>
                  </div>
                  <div>
                    <dt>{t(locale, "verdict")}</dt>
                    <dd>{verdictLabel(locale, result.verdict)}</dd>
                  </div>
                  <div>
                    <dt>{t(locale, "action")}</dt>
                    <dd>{tCode(locale, result.recommended_action)}</dd>
                  </div>
                  {result.scam_family ? (
                    <div>
                      <dt>{t(locale, "family")}</dt>
                      <dd>{result.scam_family}</dd>
                    </div>
                  ) : null}
                  {result.intent_tags && result.intent_tags.length > 0 ? (
                    <div>
                      <dt>{t(locale, "intentTags")}</dt>
                      <dd>{result.intent_tags.join(", ")}</dd>
                    </div>
                  ) : null}
                  {result.campaign_id ? (
                    <div>
                      <dt>{t(locale, "campaignId")}</dt>
                      <dd className="hash">{result.campaign_id.slice(0, 13)}…</dd>
                    </div>
                  ) : null}
                </dl>
                {result.mitre_tags.length > 0 ? (
                  <p>
                    <strong>{t(locale, "mitre")}:</strong> {result.mitre_tags.join(", ")}
                  </p>
                ) : null}
                <ul className="reasons">
                  <li className="reasons-title">{t(locale, "reasons")}</li>
                  {result.reasons.map((r) => (
                    <li key={r.code}>{tCode(locale, r.message_key)}</li>
                  ))}
                </ul>
              </section>
            ) : null}
          </div>
          <div className="hero-visual" aria-hidden="true">
            <div className="shield-plane">
              <div className="shield-ring" />
              <div className="shield-core" />
              <div className="scan-beam" />
            </div>
          </div>
        </main>
      ) : null}

      {view === "auth" ? (
        <main className="dashboard auth-panel">
          <p className="brand">{t(locale, "brand")}</p>
          <h1>{t(locale, "auth")}</h1>
          <p className="support">{t(locale, "dashboardHint")}</p>
          <form
            className="auth-form"
            onSubmit={(e) => {
              e.preventDefault();
              void onAuth("login");
            }}
          >
            <label>
              {t(locale, "email")}
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </label>
            <label>
              {t(locale, "password")}
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                autoComplete="current-password"
              />
            </label>
            <div className="auth-actions">
              <button type="submit">{t(locale, "login")}</button>
              <button type="button" className="secondary" onClick={() => void onAuth("register")}>
                {t(locale, "register")}
              </button>
            </div>
          </form>
          {authError ? <p className="error">{authError}</p> : null}
        </main>
      ) : null}

      {view === "dashboard" && user ? (
        <main className="dashboard">
          <p className="brand">{t(locale, "brand")}</p>
          <h1>{t(locale, "dashboard")}</h1>
          <p className="support">
            {t(locale, "signedInAs")}: {user.email}
          </p>

          <section className="consent-block">
            <h2>{t(locale, "consentTitle")}</h2>
            <p>{t(locale, "consentBody")}</p>
            <label className="consent-row">
              <input
                type="checkbox"
                checked={consentGranted("analytics_meta")}
                onChange={(e) => void toggleConsent("analytics_meta", e.target.checked)}
              />
              {t(locale, "consentAnalytics")}
            </label>
            <label className="consent-row">
              <input
                type="checkbox"
                checked={consentGranted("emergency_law_enforcement")}
                onChange={(e) => {
                  void (async () => {
                    const row = await setEmergencyConsent(e.target.checked);
                    setConsents((prev) => {
                      const rest = prev.filter((c) => c.consent_type !== row.consent_type);
                      return [...rest, row];
                    });
                  })().catch(() => undefined);
                }}
              />
              {t(locale, "consentEmergency")}
            </label>
          </section>

          <section className="consent-block">
            <h2>{t(locale, "activityTitle")}</h2>
            <p className="note">{t(locale, "activityHint")}</p>
            {threatEvents.length === 0 ? (
              <p className="note">{t(locale, "noHistory")}</p>
            ) : (
              <ul className="history-list">
                {threatEvents.slice(0, 10).map((e) => (
                  <li key={e.event_id}>
                    <span className="score">{e.severity}</span>
                    <span>
                      {e.category} · {e.score ?? "—"}
                    </span>
                    <span className="hash">{e.event_id.slice(0, 8)}…</span>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="consent-block">
            <h2>{t(locale, "riskHistoryTitle")}</h2>
            <p className="note">{t(locale, "riskHistoryHint")}</p>
            {riskHistory.length === 0 ? (
              <p className="note">{t(locale, "noHistory")}</p>
            ) : (
              <ul className="history-list">
                {riskHistory.slice(0, 10).map((r) => (
                  <li key={r.id}>
                    <span className="score">{r.score}</span>
                    <span>{r.subject_type}</span>
                    <span className="hash">{r.created_at.slice(0, 19)}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="consent-block">
            <h2>{t(locale, "dnsTitle")}</h2>
            <p className="note">{t(locale, "dnsHint")}</p>
            <input
              value={dnsDomain}
              onChange={(e) => setDnsDomain(e.target.value)}
              placeholder="example.uz"
              style={{ width: "100%", marginTop: "0.5rem" }}
            />
            <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem", flexWrap: "wrap" }}>
              <button
                type="button"
                disabled={!dnsDomain.trim()}
                onClick={() => {
                  void dnsCheck(dnsDomain.trim())
                    .then((r) =>
                      setDnsResult(
                        `${r.domain}: ${r.verdict} · score=${r.score}${r.allowlisted ? " · allowlist" : ""}`,
                      ),
                    )
                    .catch(() => setDnsResult(t(locale, "error")));
                }}
              >
                {t(locale, "dnsCheck")}
              </button>
              <button
                type="button"
                className="secondary"
                disabled={!dnsDomain.trim()}
                onClick={() => {
                  void addDnsAllowlist(dnsDomain.trim())
                    .then((row) => {
                      setDnsAllowlist((prev) => [row, ...prev.filter((x) => x.id !== row.id)]);
                      setDnsDomain("");
                      setDnsResult(t(locale, "dnsAdded"));
                    })
                    .catch(() => setDnsResult(t(locale, "error")));
                }}
              >
                {t(locale, "dnsAllow")}
              </button>
            </div>
            {dnsResult ? <p className="note">{dnsResult}</p> : null}
            {dnsAllowlist.length === 0 ? (
              <p className="note">{t(locale, "noHistory")}</p>
            ) : (
              <ul className="history-list">
                {dnsAllowlist.map((d) => (
                  <li key={d.id}>
                    <span>{d.domain}</span>
                    <button
                      type="button"
                      className="secondary"
                      onClick={() => {
                        void removeDnsAllowlist(d.id)
                          .then(() => setDnsAllowlist((prev) => prev.filter((x) => x.id !== d.id)))
                          .catch(() => undefined);
                      }}
                    >
                      {t(locale, "dnsRemove")}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="consent-block">
            <h2>{t(locale, "notificationsTitle")}</h2>
            {notifications.length === 0 ? (
              <p className="note">{t(locale, "noHistory")}</p>
            ) : (
              <ul className="history-list">
                {notifications.slice(0, 10).map((n) => (
                  <li key={n.id}>
                    <span className="score">{n.level}</span>
                    <span>{tCode(locale, n.body_key)}</span>
                    {!n.read_at ? (
                      <button
                        type="button"
                        className="secondary"
                        onClick={() => {
                          void markNotificationRead(n.id)
                            .then(() =>
                              setNotifications((prev) =>
                                prev.map((x) =>
                                  x.id === n.id ? { ...x, read_at: new Date().toISOString() } : x,
                                ),
                              ),
                            )
                            .catch(() => undefined);
                        }}
                      >
                        {t(locale, "markRead")}
                      </button>
                    ) : (
                      <span className="hash">read</span>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="consent-block">
            <h2>{t(locale, "reportTitle")}</h2>
            <p className="note">{t(locale, "reportHint")}</p>
            <button
              type="button"
              onClick={() => {
                const to = new Date();
                const from = new Date(to.getTime() - 30 * 24 * 3600 * 1000);
                void createReport(from.toISOString(), to.toISOString())
                  .then((r) => {
                    const scans = (r.payload as { sections?: { scan?: { count?: number } } })
                      ?.sections?.scan?.count;
                    setReportMsg(`${t(locale, "reportReady")}: ${r.report_id.slice(0, 8)}… (${scans ?? 0})`);
                  })
                  .catch(() => setReportMsg(t(locale, "error")));
              }}
            >
              {t(locale, "reportCta")}
            </button>
            {reportMsg ? <p className="note">{reportMsg}</p> : null}
          </section>

          <section className="consent-block">
            <h2>{t(locale, "pwdTitle")}</h2>
            <p className="note">{t(locale, "pwdHint")}</p>
            <input
              type="password"
              value={pwdInput}
              onChange={(e) => setPwdInput(e.target.value)}
              placeholder="••••••••"
              style={{ width: "100%", marginTop: "0.5rem" }}
              autoComplete="new-password"
            />
            <button
              type="button"
              style={{ marginTop: "0.5rem" }}
              disabled={!pwdInput}
              onClick={() => {
                void passwordHealth(pwdInput)
                  .then((r) => {
                    const pwned = r.pwned_local ? " · pwned_local" : "";
                    setPwdResult(`${r.verdict} · score=${r.score}${pwned}`);
                    setPwdInput("");
                  })
                  .catch(() => setPwdResult(t(locale, "error")));
              }}
            >
              {t(locale, "pwdCta")}
            </button>
            {pwdResult ? <p className="note">{pwdResult}</p> : null}
          </section>

          <section className="consent-block">
            <h2>{t(locale, "msgTitle")}</h2>
            <p>{t(locale, "msgHint")}</p>
            <textarea
              value={msgText}
              onChange={(e) => {
                setMsgText(e.target.value);
                setMsgPreviewOk(false);
                setMsgResult(null);
              }}
              placeholder={t(locale, "msgPlaceholder")}
              rows={4}
              style={{ width: "100%", marginTop: "0.5rem" }}
            />
            {msgText.trim() ? (
              <p className="note">
                {t(locale, "msgPreview")}: {msgText.trim().slice(0, 160)}
              </p>
            ) : null}
            <label className="consent-row">
              <input
                type="checkbox"
                checked={msgPreviewOk}
                onChange={(e) => setMsgPreviewOk(e.target.checked)}
              />
              {t(locale, "msgConfirm")}
            </label>
            <button
              type="button"
              disabled={!msgText.trim() || !msgPreviewOk}
              onClick={() => {
                void reportSuspiciousMessage(msgText.trim())
                  .then((r) => {
                    setMsgResult(
                      `${r.verdict} · score=${r.score} · ${r.scam_family ?? "—"} · ${r.preview}`,
                    );
                  })
                  .catch(() => setMsgResult(t(locale, "error")));
              }}
            >
              {t(locale, "msgSubmit")}
            </button>
            {msgResult ? <p className="note">{msgResult}</p> : null}
          </section>

          <section className="consent-block">
            <h2>{t(locale, "breachTitle")}</h2>
            <p>{t(locale, "breachHint")}</p>
            <input
              type="email"
              value={breachEmail}
              onChange={(e) => setBreachEmail(e.target.value)}
              placeholder="you@example.com"
              style={{ width: "100%", marginTop: "0.5rem" }}
            />
            <button
              type="button"
              style={{ marginTop: "0.5rem" }}
              disabled={!breachEmail.trim()}
              onClick={() => {
                void breachCheck(breachEmail.trim())
                  .then((r) => {
                    if (!r.found) {
                      setBreachResult(t(locale, "breachClean"));
                      return;
                    }
                    const recs = r.recommendations
                      .map((code) => tCode(locale, `breach.rec.${code}`))
                      .join(", ");
                    setBreachResult(
                      `${t(locale, "breachFound")}: ${r.breach_count} · ${r.breaches
                        .map((b) => b.name)
                        .join(", ")} · ${recs}`,
                    );
                  })
                  .catch(() => setBreachResult(t(locale, "error")));
              }}
            >
              {t(locale, "breachCta")}
            </button>
            {breachResult ? <p className="note">{breachResult}</p> : null}
          </section>

          <section className="consent-block">
            <h2>{t(locale, "devicesTitle")}</h2>
            {devices.length === 0 ? (
              <p className="note">{t(locale, "noHistory")}</p>
            ) : (
              <ul className="history-list">
                {devices.map((d) => (
                  <li key={d.id}>
                    <span className="score">{d.platform}</span>
                    <span>{d.app_version}</span>
                    <button
                      type="button"
                      className="secondary"
                      disabled={deviceBusy === d.id}
                      onClick={() => {
                        setDeviceBusy(d.id);
                        void revokeDevice(d.id)
                          .then(() => setDevices((prev) => prev.filter((x) => x.id !== d.id)))
                          .catch(() => undefined)
                          .finally(() => setDeviceBusy(null));
                      }}
                    >
                      {t(locale, "deviceRevoke")}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="consent-block">
            <h2>{t(locale, "erasureTitle")}</h2>
            <p>{t(locale, "erasureBody")}</p>
            <button
              type="button"
              className="secondary"
              disabled={erasureBusy}
              onClick={() => void onEraseAccount()}
            >
              {t(locale, "erasureCta")}
            </button>
            {erasureMsg ? <p className="note">{erasureMsg}</p> : null}
          </section>

          <section className="history-block">
            <h2>{t(locale, "emergencyTitle")}</h2>
            <p className="note">{t(locale, "emergencyHint")}</p>
            <p className="note">{t(locale, "emergencySimulate")}</p>
            {emergency ? (
              <p className="note">
                {emergency.aq039_resolved ? t(locale, "aq039Ok") : t(locale, "aq039Pending")} ·{" "}
                {emergency.dry_run_forced ? t(locale, "dryRunOn") : t(locale, "dryRunOff")}
              </p>
            ) : null}
            <div className="auth-actions" style={{ marginTop: "0.75rem" }}>
              <button
                type="button"
                disabled={emergencyBusy}
                onClick={() => void onEmergencyConfirm()}
              >
                {t(locale, "emergencyConfirm")}
              </button>
              <button
                type="button"
                className="secondary"
                disabled={emergencyBusy || !confirmToken}
                onClick={() => void onEmergencyDispatch()}
              >
                {t(locale, "emergencyDispatch")}
              </button>
            </div>
            {confirmToken ? (
              <p className="note">token: {confirmToken.slice(0, 12)}…</p>
            ) : null}
            {emergencyMsg ? <p className="note">{emergencyMsg}</p> : null}
            <h3 style={{ marginTop: "1rem", fontSize: "0.95rem" }}>
              {t(locale, "emergencyLogs")}
            </h3>
            {emergencyLogs.length === 0 ? (
              <p className="note">{t(locale, "noHistory")}</p>
            ) : (
              <ul className="history-list">
                {emergencyLogs.map((item) => (
                  <li key={item.id}>
                    <span className="score">{item.dry_run ? "DR" : "LV"}</span>
                    <span>
                      {item.status} · {item.channel}
                    </span>
                    <span className="hash">{item.evidence_code}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="history-block">
            <h2>{t(locale, "feedTitle")}</h2>
            <p className="note">{t(locale, "feedHint")}</p>
            {feed ? (
              <p className="note">
                {feed.version} · domains {feed.item_counts.domain ?? 0} · sha256{" "}
                {feed.item_counts.sha256 ?? 0}
              </p>
            ) : null}
          </section>

          <section className="history-block">
            <h2>{t(locale, "history")}</h2>
            {history.length === 0 ? (
              <p className="note">{t(locale, "noHistory")}</p>
            ) : (
              <ul className="history-list">
                {history.map((item) => (
                  <li key={item.scan_id}>
                    <span className={`score score-${item.verdict}`}>{item.score}</span>
                    <span>
                      {item.scan_type} · {item.verdict}
                    </span>
                    <span className="hash">{item.subject_hash.slice(0, 12)}…</span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </main>
      ) : null}

      <footer className="footer">
        <span>Defensive only · No offensive tooling</span>
        {" · "}
        <a href="https://github.com/Kamol0303/CYBERHIMOYA/blob/main/docs/privacy-policy-draft.md">
          Privacy
        </a>
      </footer>
    </div>
  );
}
