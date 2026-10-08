(() => {
  const tag = document.currentScript;
  const id = tag && tag.dataset.measurementId;
  const notice = document.getElementById("analytics-consent");
  const settings = document.getElementById("analytics-settings");
  const key = "vpsdeals.analytics.choice";
  if (!id || !notice || !settings) return;

  function readChoice() {
    try { return localStorage.getItem(key); } catch (_) { return null; }
  }
  function saveChoice(value) {
    try { localStorage.setItem(key, value); } catch (_) { /* This visit still uses the choice. */ }
  }
  function loadAnalytics() {
    if (window.vpsDealsAnalyticsLoaded) return;
    window.vpsDealsAnalyticsLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("consent", "default", {
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied",
      analytics_storage: "denied"
    });
    window.gtag("consent", "update", { analytics_storage: "granted" });
    window.gtag("js", new Date());
    window.gtag("config", id);
    const script = document.createElement("script");
    script.async = true;
    script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(id);
    document.head.appendChild(script);
  }

  settings.addEventListener("click", () => { notice.hidden = false; });
  notice.querySelector('[data-analytics-choice="allow"]').addEventListener("click", () => {
    saveChoice("allow");
    notice.hidden = true;
    loadAnalytics();
  });
  notice.querySelector('[data-analytics-choice="decline"]').addEventListener("click", () => {
    const wasLoaded = Boolean(window.vpsDealsAnalyticsLoaded);
    saveChoice("decline");
    notice.hidden = true;
    if (wasLoaded) {
      window.gtag("consent", "update", { analytics_storage: "denied" });
      window.location.reload();
    }
  });

  const choice = readChoice();
  if (choice === "allow") loadAnalytics();
  else if (choice !== "decline") notice.hidden = false;
})();
