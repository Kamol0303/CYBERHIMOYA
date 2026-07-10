/* Cyber Guardian AI — page banner (FR-062). No DOM rewriting beyond banner root. */
(function () {
  const ROOT_ID = "cga-guardian-banner-root";

  function removeBanner() {
    const el = document.getElementById(ROOT_ID);
    if (el) el.remove();
  }

  function showBanner(payload) {
    removeBanner();
    const root = document.createElement("div");
    root.id = ROOT_ID;
    root.setAttribute("role", "alert");
    root.dataset.verdict = payload.verdict || "suspicious";

    const title = document.createElement("strong");
    title.className = "cga-title";
    title.textContent = `${payload.brand}: ${payload.title}`;

    const meta = document.createElement("span");
    meta.className = "cga-meta";
    meta.textContent = `${payload.scoreLabel}=${payload.score} · ${payload.action || ""}`;

    const actions = document.createElement("div");
    actions.className = "cga-actions";

    const dismiss = document.createElement("button");
    dismiss.type = "button";
    dismiss.textContent = payload.dismiss;
    dismiss.addEventListener("click", () => removeBanner());

    const allow = document.createElement("button");
    allow.type = "button";
    allow.textContent = payload.allow;
    allow.addEventListener("click", () => {
      chrome.runtime.sendMessage({ type: "cga.allow", url: payload.url }, () => {
        removeBanner();
      });
    });

    actions.append(dismiss, allow);
    root.append(title, meta, actions);
    document.documentElement.appendChild(root);
  }

  chrome.runtime.onMessage.addListener((msg) => {
    if (!msg || !msg.type) return;
    if (msg.type === "cga.warn" && msg.payload) {
      showBanner(msg.payload);
    } else if (msg.type === "cga.hide") {
      removeBanner();
    }
  });
})();
