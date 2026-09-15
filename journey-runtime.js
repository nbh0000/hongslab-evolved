const NETWORK_STATUS_CLASS = "network-status";
const RECOVERY_DELAY_MS = 4000;

export function normalizedPath(value, base = globalThis.location?.href || "https://genilo.kr/") {
  try {
    const url = new URL(value, base);
    let pathname = url.pathname.replace(/\/index\.html$/i, "/").replace(/\/$/, "") || "/";
    if (pathname === "/apps.html") pathname = "/apps";
    return pathname;
  } catch {
    return "";
  }
}

export function connectivityMessage(online) {
  return online
    ? "인터넷 연결이 복구되었습니다. 중단된 작업은 상태를 확인한 뒤 직접 다시 시도해 주세요."
    : "인터넷 연결이 끊겼습니다. 입력 내용은 유지하고 연결이 복구된 뒤 직접 다시 시도해 주세요.";
}

export function safeExternalRel(current = "") {
  return [...new Set(`${current} noopener noreferrer`.trim().split(/\s+/).filter(Boolean))].join(" ");
}

export function hardenExternalLinks(root = document) {
  const origin = globalThis.location?.origin;
  if (!origin) return 0;
  let changed = 0;
  root.querySelectorAll('a[href][target="_blank"]').forEach(link => {
    let url;
    try {
      url = new URL(link.href, globalThis.location.href);
    } catch {
      return;
    }
    if (url.origin === origin) return;
    const rel = safeExternalRel(link.getAttribute("rel") || "");
    if (link.getAttribute("rel") !== rel) {
      link.setAttribute("rel", rel);
      changed += 1;
    }
  });
  return changed;
}

export function markCurrentNavigation(root = document) {
  const current = normalizedPath(globalThis.location?.href || "/");
  let marked = 0;
  root.querySelectorAll('nav a[href], footer a[href]').forEach(link => {
    const target = normalizedPath(link.href);
    if (target && target === current) {
      link.setAttribute("aria-current", "page");
      marked += 1;
    } else if (link.getAttribute("aria-current") === "page") {
      link.removeAttribute("aria-current");
    }
  });
  return marked;
}

export function focusHashTarget(hash = globalThis.location?.hash || "") {
  if (!hash || hash === "#") return false;
  let id;
  try {
    id = decodeURIComponent(hash.slice(1));
  } catch {
    return false;
  }
  const target = document.getElementById(id);
  if (!target) return false;
  if (!target.matches('a[href],button,input,select,textarea,[tabindex]')) target.tabIndex = -1;
  target.focus({ preventScroll:true });
  return document.activeElement === target;
}

function createNetworkStatus() {
  const existing = document.querySelector(`.${NETWORK_STATUS_CLASS}`);
  if (existing) return existing;
  const status = document.createElement("div");
  status.className = NETWORK_STATUS_CLASS;
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  status.setAttribute("aria-atomic", "true");
  status.hidden = true;
  document.body.append(status);
  return status;
}

export function installConnectivityStatus({ recoveryDelay = RECOVERY_DELAY_MS } = {}) {
  const status = createNetworkStatus();
  let experiencedOffline = !navigator.onLine;
  let recoveryTimer = 0;

  const render = online => {
    window.clearTimeout(recoveryTimer);
    document.documentElement.dataset.network = online ? "online" : "offline";
    if (!online) experiencedOffline = true;
    if (online && !experiencedOffline) {
      status.hidden = true;
      status.textContent = "";
      return;
    }
    status.dataset.state = online ? "online" : "offline";
    status.textContent = connectivityMessage(online);
    status.hidden = false;
    if (online) {
      recoveryTimer = window.setTimeout(() => {
        status.hidden = true;
        status.textContent = "";
        experiencedOffline = false;
      }, recoveryDelay);
    }
  };

  window.addEventListener("offline", () => render(false));
  window.addEventListener("online", () => render(true));
  render(navigator.onLine);
  return { status, render };
}

function installHashFocus() {
  document.addEventListener("click", event => {
    const link = event.target.closest('a[href^="#"]');
    if (!link || link.getAttribute("href") === "#") return;
    window.setTimeout(() => focusHashTarget(link.hash), 0);
  });
  window.addEventListener("hashchange", () => focusHashTarget());
}

function initializeJourneyRuntime() {
  document.documentElement.dataset.journeyReady = "true";
  markCurrentNavigation();
  hardenExternalLinks();
  installHashFocus();
  installConnectivityStatus();
  window.addEventListener("pageshow", () => {
    markCurrentNavigation();
    hardenExternalLinks();
  });
  document.dispatchEvent(new CustomEvent("genilo:journey-ready"));
}

if (typeof document !== "undefined") {
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initializeJourneyRuntime, { once:true });
  else initializeJourneyRuntime();
}
