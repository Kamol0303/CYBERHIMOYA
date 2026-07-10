/* FR-063 — installed extension permission analyzer (defensive warning only). */
(function () {
  const HIGH_PERMS = new Set([
    "debugger",
    "proxy",
    "webRequest",
    "webRequestBlocking",
    "cookies",
    "nativeMessaging",
    "management",
    "privacy",
    "tabs",
    "history",
    "downloads",
    "clipboardRead",
    "clipboardWrite",
  ]);

  function riskFor(ext) {
    const perms = [...(ext.permissions || []), ...(ext.hostPermissions || [])];
    const hits = [];
    for (const p of perms) {
      if (HIGH_PERMS.has(p) || p === "<all_urls>" || p === "*://*/*") {
        hits.push(p);
      }
    }
    let level = "ok";
    if (hits.length >= 3) level = "high";
    else if (hits.length >= 1) level = "medium";
    // Unknown + high host access → warn even if not in chrome store metadata.
    if (!ext.installType || ext.installType === "development" || ext.installType === "sideload") {
      if (hits.length) level = level === "ok" ? "medium" : "high";
    }
    return { level, hits };
  }

  async function analyze() {
    const out = document.getElementById("ext-out");
    if (!chrome.management?.getAll) {
      out.textContent = "management API unavailable";
      return;
    }
    const list = await chrome.management.getAll();
    const rows = list
      .filter((e) => e.type === "extension" && e.id !== chrome.runtime.id)
      .map((e) => {
        const r = riskFor(e);
        return { name: e.name, enabled: e.enabled, ...r };
      })
      .filter((r) => r.level !== "ok")
      .sort((a, b) => (a.level === "high" ? -1 : 1));

    if (!rows.length) {
      out.textContent = "No high-permission warnings.";
      return;
    }
    out.textContent = rows
      .map((r) => `${r.level.toUpperCase()} · ${r.name}\n  ${r.hits.join(", ")}`)
      .join("\n\n");
  }

  document.getElementById("ext-analyze")?.addEventListener("click", () => {
    void analyze();
  });
})();
