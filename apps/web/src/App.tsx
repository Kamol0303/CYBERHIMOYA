import { useEffect, useState, type FormEvent } from "react";
import { scanUrl, type UrlScanResponse, type Verdict } from "./lib/api";
import { locales, t, type Locale } from "./i18n/messages";
import "./App.css";

function verdictLabel(locale: Locale, verdict: Verdict): string {
  return t(locale, verdict);
}

export default function App() {
  const [locale, setLocale] = useState<Locale>("uz");
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<UrlScanResponse | null>(null);
  const [view, setView] = useState<"scan" | "dashboard">("scan");

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await scanUrl(url.trim());
      setResult(data);
    } catch {
      setError(t(locale, "error"));
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

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
            <form className="scan-form" onSubmit={onSubmit}>
              <input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder={t(locale, "placeholder")}
                aria-label="URL"
                autoComplete="url"
                inputMode="url"
              />
              <button type="submit" disabled={loading || !url.trim()}>
                {loading ? t(locale, "scanning") : t(locale, "cta")}
              </button>
            </form>
            <p className="note">{t(locale, "guestNote")}</p>
            <p className="privacy">{t(locale, "privacy")}</p>
            {error ? <p className="error">{error}</p> : null}
            {result ? (
              <section className="result" aria-live="polite">
                <h2>{t(locale, "result")}</h2>
                <p className="normalized">{result.url_normalized}</p>
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
