import { useEffect, useState, type FormEvent } from "react";
import {
  scanFileHash,
  scanQr,
  scanUrl,
  sha256Hex,
  type ScanReason,
  type Verdict,
} from "./lib/api";
import { locales, t, type Locale } from "./i18n/messages";
import "./App.css";

type ScanMode = "url" | "qr" | "file";

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
  const [view, setView] = useState<"scan" | "dashboard">("scan");

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

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
            onClick={() => setView("dashboard")}
          >
            {t(locale, "dashboard")}
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
      ) : (
        <main className="dashboard">
          <p className="brand">{t(locale, "brand")}</p>
          <h1>{t(locale, "dashboard")}</h1>
          <p className="support">{t(locale, "dashboardHint")}</p>
          <section className="consent-block">
            <h2>{t(locale, "consentTitle")}</h2>
            <p>{t(locale, "consentBody")}</p>
          </section>
        </main>
      )}

      <footer className="footer">
        <span>Defensive only · No offensive tooling</span>
      </footer>
    </div>
  );
}
