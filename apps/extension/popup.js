const API_BASE = "http://127.0.0.1:8000";

async function scanUrl(url) {
  const res = await fetch(`${API_BASE}/v1/scan/url`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      url,
      context: { source: "extension", client_cache_hit: false },
    }),
  });
  if (!res.ok) throw new Error(`scan_failed_${res.status}`);
  return res.json();
}

document.getElementById("scan").addEventListener("click", async () => {
  const out = document.getElementById("out");
  out.textContent = "Tekshirilmoqda…";
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const url = tab?.url;
    if (!url || !/^https?:/i.test(url)) {
      out.textContent = "Faqat http(s) sahifalar skan qilinadi.";
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
    out.textContent = String(err);
  }
});
