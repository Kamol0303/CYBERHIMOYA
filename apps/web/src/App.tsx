import { useEffect, useState, type FormEvent } from "react";
import {
  confirmEmergency,
  dispatchEmergency,
  fetchConsents,
  fetchEmergencyAllowlist,
  fetchEmergencyLogs,
  fetchMe,
  fetchScans,
  fetchThreatFeedSync,
  getToken,
  login,
  register,
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
import { locales, t, type Locale } from "./i18n/messages";
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
};

function verdictLabel(locale: Locale, verdict: Verdict): string {
  return t(locale, verdict);
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

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  useEffect(() => {
    const token = getToken();
    if (!token) return;
    void fetchMe()
      .then(setUser)
      .catch(() => setToken(null));
  }, []);

  async function refreshDashboard() {
    if (!getToken()) {
      setHistory([]);
      setConsents([]);
      return;
    }
    const [scans, consentRows, feedSync, allowlist, emLogs] = await Promise.all([
      fetchScans(),
      fetchConsents(),
      fetchThreatFeedSync(),
      fetchEmergencyAllowlist(),
      fetchEmergencyLogs(),
    ]);
    setHistory(scans);
    setConsents(consentRows);
    setFeed(feedSync);
    setEmergency(allowlist);
    setEmergencyLogs(emLogs);
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
        });
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
        });
      }
    } catch {
      setError(t(locale, "error"));
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
      });
    } catch {
      setError(t(locale, "error"));
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
            <p className="privacy">{t(locale, "privacy")}</p>
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
                    <dd>{result.recommended_action}</dd>
                  </div>
                  {result.scam_family ? (
                    <div>
                      <dt>{t(locale, "family")}</dt>
                      <dd>{result.scam_family}</dd>
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
                    <li key={r.code}>{r.code}</li>
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
                  void toggleConsent("emergency_law_enforcement", e.target.checked);
                  void setEmergencyConsent(e.target.checked).catch(() => undefined);
                }}
              />
              {t(locale, "consentEmergency")}
            </label>
          </section>

          <section className="history-block">
            <h2>{t(locale, "emergencyTitle")}</h2>
            <p className="note">{t(locale, "emergencyHint")}</p>
            {emergency ? (
              <p className="note">
                AQ-039: {emergency.aq039_resolved ? "ok" : "pending"} · dry-run{" "}
                {emergency.dry_run_forced ? "on" : "off"}
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
