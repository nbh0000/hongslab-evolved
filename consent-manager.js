(function initializePrivacyPreferences() {
  "use strict";

  const STORAGE_KEY = "genilo_privacy_preferences_v1";
  const CURRENT_VERSION = 1;
  const DEFAULTS = Object.freeze({ essential:true, analytics:false, version:CURRENT_VERSION });

  function read() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
      if (!saved || saved.version !== CURRENT_VERSION) return { ...DEFAULTS, decided:false };
      return {
        essential:true,
        analytics:saved.analytics === true,
        version:CURRENT_VERSION,
        decided:true,
        updatedAt:String(saved.updatedAt || "")
      };
    } catch {
      return { ...DEFAULTS, decided:false };
    }
  }

  function write(analytics) {
    const value = {
      essential:true,
      analytics:analytics === true,
      version:CURRENT_VERSION,
      updatedAt:new Date().toISOString()
    };
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(value)); } catch {}
    window.dispatchEvent(new CustomEvent("genilo:consent-changed", { detail:value }));
    return value;
  }

  window.GeniloPrivacy = Object.freeze({ key:STORAGE_KEY, read, write });

  function addCommercialNavigation() {
    const nav = document.querySelector(".site-shell-nav");
    if (nav && !nav.querySelector('[data-nav="business"]')) {
      const business = document.createElement("a");
      business.dataset.nav = "business";
      business.href = "/business.html";
      business.textContent = "비즈니스";
      nav.append(business);
    }

    const footerNav = document.querySelector(".site-shell-footer nav");
    if (footerNav) {
      const links = [
        ["/solutions.html", "활용 솔루션"],
        ["/start.html", "시작 플래너"],
        ["/business.html", "비즈니스"],
        ["/trust.html", "신뢰센터"],
        ["/help.html", "도움말"],
        ["/commercial-use.html", "상업적 이용 안내"]
      ];
      for (const [href, label] of links) {
        if (footerNav.querySelector('a[href="' + href + '"]')) continue;
        const link = document.createElement("a");
        link.href = href;
        link.textContent = label;
        footerNav.append(link);
      }
    }
  }

  function buildInterface() {
    addCommercialNavigation();

    const launcher = document.createElement("button");
    launcher.type = "button";
    launcher.className = "privacy-launcher";
    const initialPreferences = read();
    launcher.textContent = "개인정보 설정";
    launcher.setAttribute("aria-label", initialPreferences.decided ? "개인정보 설정" : "개인정보 설정, 선택 분석 꺼짐");
    launcher.setAttribute("aria-haspopup", "dialog");
    launcher.dataset.commercialConsent = "launcher";

    const dialog = document.createElement("dialog");
    dialog.className = "privacy-dialog";
    dialog.setAttribute("aria-labelledby", "privacyDialogTitle");
    dialog.innerHTML = '<form method="dialog"><h2 id="privacyDialogTitle">개인정보 설정</h2><p>서비스에 필요한 저장과 선택 분석을 구분합니다. 선택은 언제든 변경할 수 있습니다.</p><label class="privacy-choice"><input type="checkbox" checked disabled><span><strong>필수 저장</strong><small>로그인 상태, 보안, 결제 진행과 사용자가 요청한 기능에 필요합니다.</small></span></label><label class="privacy-choice"><input id="privacyAnalytics" type="checkbox"><span><strong>선택 분석</strong><small>개인정보·프롬프트를 제외한 전환 이벤트를 서비스 개선 목적으로 전송합니다.</small></span></label><a class="privacy-detail-link" href="/privacy.html">개인정보처리방침 자세히 보기</a><div class="privacy-dialog-actions"><button type="button" class="privacy-close">닫기</button><button type="submit" class="privacy-save" value="save">선택 저장</button></div></form>';

    const open = () => {
      const preferences = read();
      dialog.querySelector("#privacyAnalytics").checked = preferences.analytics;
      if (!dialog.open) dialog.showModal();
    };
    launcher.addEventListener("click", open);
    document.querySelectorAll("[data-open-privacy-settings]").forEach(button => button.addEventListener("click", open));
    dialog.querySelector(".privacy-close").addEventListener("click", () => dialog.close());
    dialog.querySelector("form").addEventListener("submit", event => {
      event.preventDefault();
      write(dialog.querySelector("#privacyAnalytics").checked);
      launcher.setAttribute("aria-label", "개인정보 설정");
      dialog.close();
    });

    document.body.append(launcher, dialog);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", buildInterface, { once:true });
  else buildInterface();
})();
