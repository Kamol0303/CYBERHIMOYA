const API_BASE = "http://127.0.0.1:8000";

const STR = {
  uz: {
    brand: "Cyber Guardian AI",
    subtitle: "Mudofaa URL skani",
    scan: "Joriy sahifani tekshirish",
    scanning: "Tekshirilmoqda…",
    onlyHttp: "Faqat http(s) sahifalar skan qilinadi.",
    result: "Natija shu yerda…",
    rateLimited: "Mehmon limitti tugadi. Keyinroq urinib ko‘ring.",
    scanFailed: "Skan muvaffaqiyatsiz.",
    sync: "IOC sync",
    feed: "IOC",
  },
  ru: {
    brand: "Cyber Guardian AI",
    subtitle: "Защитное сканирование URL",
    scan: "Проверить текущую страницу",
    scanning: "Проверка…",
    onlyHttp: "Сканируются только http(s) страницы.",
    result: "Результат здесь…",
    rateLimited: "Гостевой лимит исчерпан. Попробуйте позже.",
    scanFailed: "Сканирование не удалось.",
    sync: "IOC sync",
    feed: "IOC",
  },
  en: {
    brand: "Cyber Guardian AI",
    subtitle: "Defensive URL scan",
    scan: "Scan current page",
    scanning: "Scanning…",
    onlyHttp: "Only http(s) pages can be scanned.",
    result: "Result appears here…",
    rateLimited: "Guest quota exceeded. Try again later.",
    scanFailed: "Scan failed.",
    sync: "IOC sync",
    feed: "IOC",
  },
};

function locale() {
  const lang = (navigator.language || "uz").slice(0, 2).toLowerCase();
  return STR[lang] ? lang : "uz";
}

function applyI18n() {
  const t = STR[locale()];
  document.getElementById("brand").textContent = t.brand;
  document.getElementById("subtitle").textContent = t.subtitle;
  document.getElementById("scan").textContent = t.scan;
  document.getElementById("out").textContent = t.result;
  document.getElementById("sync").textContent = t.sync;
}

async function refreshFeedStatus() {
  const t = STR[locale()];
  const el = document.getElementById("feed");
  const { iocCache } = await chrome.storage.local.get("iocCache");
  const n = iocCache?.domains?.length ?? 0;
  const ver = iocCache?.version || "seed";
  el.textContent = `${t.feed}: ${ver} · ${n} domains`;
}

async function scanUrl(url) {
  const res = await fetch(`${API_BASE}/v1/scan/url`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      url,
      context: { source: "extension", client_cache_hit: false },
    }),
  });
  if (!res.ok) {
    const err = new Error(`scan_failed_${res.status}`);
    err.status = res.status;
    const ct = res.headers.get("content-type") || "";
    if (ct.includes("json")) {
      try {
        const body = await res.json();
        if (typeof body.detail === "string" && body.detail.trim()) {
          err.detail = body.detail.trim();
        }
      } catch {
        /* ignore parse errors */
      }
    }
    throw err;
  }
  return res.json();
}

applyI18n();
void refreshFeedStatus();

document.getElementById("sync").addEventListener("click", () => {
  chrome.runtime.sendMessage({ type: "cga.syncFeed" }, () => {
    void refreshFeedStatus();
  });
});

document.getElementById("scan").addEventListener("click", async () => {
  const t = STR[locale()];
  const out = document.getElementById("out");
  out.textContent = t.scanning;
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const url = tab?.url;
    if (!url || !/^https?:/i.test(url)) {
      out.textContent = t.onlyHttp;
      return;
    }
    const data = await scanUrl(url);
    out.textContent = [
      data.url_normalized,
      `score=${data.score} verdict=${data.verdict}`,
      `action=${data.recommended_action}`,
      (data.mitre_tags || []).join(", "),
    ]
      .filter(Boolean)
      .join("\n");
  } catch (err) {
    if (err && err.status === 429) {
      out.textContent = err.detail || t.rateLimited;
    } else {
      out.textContent = t.scanFailed;
    }
  }
});
