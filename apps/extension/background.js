/* Cyber Guardian AI — defensive phishing banner (FR-062). No credential capture. */
const API_BASE = "http://127.0.0.1:8000";
const CACHE_TTL_MS = 5 * 60 * 1000;
const FEED_TTL_MS = 60 * 60 * 1000;
const scanCache = new Map();

/** Offline seed — mirrors API KNOWN_MALICIOUS_DOMAINS (defensive reputation only). */
const SEED_MALICIOUS = [
  "pay-click-uz.tk",
  "gov-subsidy-uz.xyz",
  "telegram-bonus-uz.ml",
  "iiv-fine-pay.ru.com",
  "click-payme-secure.cf",
];

const STR = {
  uz: {
    brand: "Cyber Guardian AI",
    warn: "Shubhali sahifa",
    block: "Xavfli sahifa",
    score: "Risk",
    dismiss: "Yopish",
    allow: "Shu sessiyada ruxsat",
  },
  ru: {
    brand: "Cyber Guardian AI",
    warn: "Подозрительная страница",
    block: "Опасная страница",
    score: "Риск",
    dismiss: "Закрыть",
    allow: "Разрешить в этой сессии",
  },
  en: {
    brand: "Cyber Guardian AI",
    warn: "Suspicious page",
    block: "Dangerous page",
    score: "Risk",
    dismiss: "Dismiss",
    allow: "Allow this session",
  },
};

function locale() {
  const lang = (navigator.language || "uz").slice(0, 2).toLowerCase();
  return STR[lang] ? lang : "uz";
}

function hostnameOf(url) {
  try {
    return new URL(url).hostname.toLowerCase().replace(/^www\./, "");
  } catch {
    return "";
  }
}

async function loadLocalIocs() {
  const { iocCache } = await chrome.storage.local.get("iocCache");
  if (iocCache?.domains?.length) {
    return iocCache;
  }
  return { domains: SEED_MALICIOUS, version: "seed", at: 0 };
}

async function syncThreatFeed() {
  const { iocCache } = await chrome.storage.local.get("iocCache");
  if (iocCache?.at && Date.now() - iocCache.at < FEED_TTL_MS) {
    return iocCache;
  }
  try {
    const res = await fetch(`${API_BASE}/v1/threat-feed/sync`);
    if (!res.ok) throw new Error("feed_sync_failed");
    const data = await res.json();
    const domains = (data.items || [])
      .filter((i) => i.kind === "domain" && i.severity === "malicious")
      .map((i) => String(i.value).toLowerCase());
    const cache = {
      domains: domains.length ? domains : SEED_MALICIOUS,
      version: data.version || "unknown",
      at: Date.now(),
    };
    await chrome.storage.local.set({ iocCache: cache });
    return cache;
  } catch {
    return loadLocalIocs();
  }
}

function localHit(host, domains) {
  if (!host) return false;
  return domains.some((d) => host === d || host.endsWith("." + d));
}

async function isAllowed(url) {
  const { allowlist = {} } = await chrome.storage.session.get("allowlist");
  return Boolean(allowlist[url]);
}

async function allowUrl(url) {
  const { allowlist = {} } = await chrome.storage.session.get("allowlist");
  allowlist[url] = Date.now();
  await chrome.storage.session.set({ allowlist });
}

async function scanUrl(url) {
  const cached = scanCache.get(url);
  if (cached && Date.now() - cached.at < CACHE_TTL_MS) {
    return cached.data;
  }
  const res = await fetch(`${API_BASE}/v1/scan/url`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      url,
      context: { source: "extension_nav", client_cache_hit: false },
    }),
  });
  if (!res.ok) {
    const err = new Error(`scan_failed_${res.status}`);
    err.status = res.status;
    throw err;
  }
  const data = await res.json();
  scanCache.set(url, { at: Date.now(), data });
  return data;
}

function setBadge(tabId, verdict) {
  if (verdict === "malicious") {
    chrome.action.setBadgeBackgroundColor({ tabId, color: "#b42318" });
    chrome.action.setBadgeText({ tabId, text: "!" });
  } else if (verdict === "suspicious") {
    chrome.action.setBadgeBackgroundColor({ tabId, color: "#b54708" });
    chrome.action.setBadgeText({ tabId, text: "?" });
  } else {
    chrome.action.setBadgeText({ tabId, text: "" });
  }
}

function warnTab(tabId, payload) {
  chrome.tabs.sendMessage(tabId, { type: "cga.warn", payload }).catch(() => {});
}

async function protectTab(tabId, url) {
  if (!url || !/^https?:/i.test(url)) {
    return;
  }
  if (await isAllowed(url)) {
    setBadge(tabId, "clean");
    chrome.tabs.sendMessage(tabId, { type: "cga.hide" }).catch(() => {});
    return;
  }

  const t = STR[locale()];
  const host = hostnameOf(url);
  const iocs = await loadLocalIocs();
  if (localHit(host, iocs.domains || SEED_MALICIOUS)) {
    setBadge(tabId, "malicious");
    warnTab(tabId, {
      brand: t.brand,
      title: t.block,
      scoreLabel: t.score,
      score: 95,
      verdict: "malicious",
      action: "block_and_warn",
      dismiss: t.dismiss,
      allow: t.allow,
      url,
    });
    // Still try cloud scan for explainability when online.
  }

  try {
    const data = await scanUrl(url);
    setBadge(tabId, data.verdict);
    if (data.verdict === "malicious" || data.verdict === "suspicious") {
      warnTab(tabId, {
        brand: t.brand,
        title: data.verdict === "malicious" ? t.block : t.warn,
        scoreLabel: t.score,
        score: data.score,
        verdict: data.verdict,
        action: data.recommended_action,
        dismiss: t.dismiss,
        allow: t.allow,
        url,
      });
    } else if (!localHit(host, iocs.domains || SEED_MALICIOUS)) {
      chrome.tabs.sendMessage(tabId, { type: "cga.hide" }).catch(() => {});
    }
  } catch {
    /* offline / quota — local IOC banner already shown if hit */
  }
}

chrome.runtime.onInstalled.addListener(() => {
  void syncThreatFeed();
});

chrome.runtime.onStartup.addListener(() => {
  void syncThreatFeed();
});

void syncThreatFeed();

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.url) {
    void protectTab(tabId, tab.url);
  }
});

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "cga.allow" && msg.url) {
    void allowUrl(msg.url).then(() => sendResponse({ ok: true }));
    return true;
  }
  if (msg?.type === "cga.rescan" && msg.url && typeof msg.tabId === "number") {
    void protectTab(msg.tabId, msg.url).then(() => sendResponse({ ok: true }));
    return true;
  }
  if (msg?.type === "cga.syncFeed") {
    void syncThreatFeed().then((c) => sendResponse({ ok: true, version: c.version }));
    return true;
  }
  return false;
});
