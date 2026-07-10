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
    throw err;
  }
  return res.json();
}

applyI18n();

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
      out.textContent = t.rateLimited;
    } else {
      out.textContent = t.scanFailed;
    }
  }
});
