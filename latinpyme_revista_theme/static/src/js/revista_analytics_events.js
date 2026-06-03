(function () {
  "use strict";

  var DATA_PREFIX = "data-analytics-";
  var URL_KEYS = {
    article_url: true,
    file_url: true,
    page_path: true,
    target_url: true,
    video_url: true,
  };
  var SENSITIVE_PATTERNS = [
    /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i,
    /(?:\+?\d[\s().-]*){7,}/,
    /\b(?:dni|ruc|nit|cedula|c[eé]dula|pasaporte)\b/i,
  ];
  var DOWNLOAD_PATTERN = /\.(pdf|doc|docx|xls|xlsx|ppt|pptx|zip)(?:[?#]|$)/i;

  function isTrackingAvailable() {
    return typeof window.gtag === "function";
  }

  function normalizeText(value, limit) {
    if (value === undefined || value === null) {
      return "";
    }
    return String(value).replace(/\s+/g, " ").trim().slice(0, limit || 160);
  }

  function hasSensitiveData(value) {
    var text = normalizeText(value, 500);
    if (!text) {
      return false;
    }
    return SENSITIVE_PATTERNS.some(function (pattern) {
      return pattern.test(text);
    });
  }

  function cleanParam(key, value) {
    var normalized = normalizeText(value, URL_KEYS[key] ? 500 : 160);
    if (!normalized) {
      return "";
    }
    if (!URL_KEYS[key] && hasSensitiveData(normalized)) {
      return "";
    }
    return normalized;
  }

  function setParam(params, key, value) {
    var cleaned = cleanParam(key, value);
    if (cleaned) {
      params[key] = cleaned;
    }
  }

  function dataKey(attributeName) {
    return attributeName.slice(DATA_PREFIX.length).replace(/-/g, "_");
  }

  function readAnalyticsParams(element) {
    var params = {};
    Array.prototype.forEach.call(element.attributes || [], function (attribute) {
      if (attribute.name.indexOf(DATA_PREFIX) !== 0) {
        return;
      }
      var key = dataKey(attribute.name);
      if (key === "event") {
        return;
      }
      setParam(params, key, attribute.value);
    });
    return params;
  }

  function pagePath() {
    return window.location.pathname || "/";
  }

  function pageTitle() {
    return document.title || "";
  }

  function linkTarget(element) {
    var link = element.closest("a[href]");
    if (link) {
      return link.href || link.getAttribute("href") || "";
    }
    if (element.action) {
      return element.action;
    }
    return "";
  }

  function linkText(element) {
    var value = element.getAttribute("data-analytics-link-text")
      || element.getAttribute("aria-label")
      || element.getAttribute("title")
      || "";
    if (!value) {
      value = element.textContent || "";
    }
    return value;
  }

  function closestBlock(element) {
    return element.closest("[data-analytics-block-name]");
  }

  function derivePosition(element, eventName) {
    var item = element.closest("[data-analytics-item]");
    var block = closestBlock(element) || element.closest(".lp-revista");
    var selector;
    var nodes;
    var index;

    if (item && block) {
      selector = "[data-analytics-item='" + item.getAttribute("data-analytics-item") + "']";
      nodes = Array.prototype.slice.call(block.querySelectorAll(selector));
      index = nodes.indexOf(item);
      if (index >= 0) {
        return String(index + 1);
      }
    }

    if (block) {
      selector = "[data-analytics-event='" + eventName + "']";
      nodes = Array.prototype.slice.call(block.querySelectorAll(selector));
      index = nodes.indexOf(element);
      if (index >= 0) {
        return String(index + 1);
      }
    }
    return "";
  }

  function fileNameFromUrl(url) {
    try {
      var pathname = new URL(url, window.location.origin).pathname;
      var parts = pathname.split("/");
      return decodeURIComponent(parts[parts.length - 1] || "");
    } catch (error) {
      return "";
    }
  }

  function isWhatsappUrl(url) {
    return /(?:wa\.me|wa\.link|whatsapp\.com)/i.test(url || "");
  }

  function normalizeEventName(eventName, params) {
    if (eventName === "click_site_link" && isWhatsappUrl(params.target_url)) {
      params.cta_type = params.cta_type || "other";
      return "click_whatsapp";
    }
    if (eventName === "click_site_link" && DOWNLOAD_PATTERN.test(params.target_url || "")) {
      params.file_url = params.file_url || params.target_url;
      params.file_name = params.file_name || fileNameFromUrl(params.target_url);
      return "download_media_kit";
    }
    return eventName;
  }

  function enrichBaseParams(element, eventName, params) {
    var target = linkTarget(element);
    var block = closestBlock(element);

    setParam(params, "page_path", params.page_path || pagePath());
    setParam(params, "page_title", params.page_title || pageTitle());

    if (target) {
      setParam(params, "target_url", params.target_url || target);
    }
    if (!params.link_text && eventName.indexOf("click_") === 0) {
      setParam(params, "link_text", linkText(element));
    }
    if (block && !params.block_name) {
      setParam(params, "block_name", block.getAttribute("data-analytics-block-name"));
    }
    if (!params.position) {
      setParam(params, "position", derivePosition(element, eventName));
    }
    if (eventName === "click_article" && !params.article_url) {
      setParam(params, "article_url", params.target_url);
    }
    if (eventName === "share_article" && !params.article_url) {
      setParam(params, "article_url", params.target_url);
    }
    if (eventName === "download_media_kit") {
      setParam(params, "file_url", params.file_url || params.target_url);
      setParam(params, "file_name", params.file_name || fileNameFromUrl(params.file_url || params.target_url));
    }
  }

  function sendEvent(eventName, params) {
    if (!isTrackingAvailable() || !eventName) {
      return;
    }
    try {
      window.gtag("event", eventName, params || {});
    } catch (error) {
      return;
    }
  }

  function track(eventName, params) {
    var payload = {};
    Object.keys(params || {}).forEach(function (key) {
      setParam(payload, key, params[key]);
    });
    setParam(payload, "page_path", payload.page_path || pagePath());
    sendEvent(eventName, payload);
  }

  function trackHomeBlock(element, params) {
    var block = element.closest("[data-analytics-home-block='1']");
    var payload = {};

    if (!block) {
      return;
    }
    setParam(payload, "block_name", params.block_name || block.getAttribute("data-analytics-block-name"));
    setParam(payload, "article_title", params.article_title || "");
    setParam(payload, "target_url", params.target_url || params.article_url || params.video_url || "");
    setParam(payload, "position", params.position || derivePosition(element, "click_home_block"));
    setParam(payload, "page_path", pagePath());
    sendEvent("click_home_block", payload);
  }

  function handleClick(event) {
    var element = event.target.closest("[data-analytics-event]");
    var eventName;
    var params;

    if (!element || !document.documentElement.contains(element)) {
      return;
    }

    eventName = element.getAttribute("data-analytics-event");
    params = readAnalyticsParams(element);
    enrichBaseParams(element, eventName, params);
    eventName = normalizeEventName(eventName, params);
    sendEvent(eventName, params);

    if (eventName !== "click_home_ad_banner" && eventName !== "share_article" && eventName !== "poll_vote") {
      trackHomeBlock(element, params);
    }
  }

  function handleSearchSubmit(event) {
    var form = event.target.closest("form[data-analytics-event='search']");
    var input;
    var term;

    if (!form || !document.documentElement.contains(form)) {
      return;
    }
    input = form.querySelector("input[type='search'], input[name='search'], input[name='q']");
    term = normalizeText(input && input.value, 100);
    if (!term || hasSensitiveData(term)) {
      return;
    }
    track("search", {
      search_term: term,
      page_path: pagePath(),
    });
  }

  function handleCustomEvent(event) {
    var detail = event.detail || {};
    if (!detail.eventName) {
      return;
    }
    track(detail.eventName, detail.params || {});
  }

  document.addEventListener("click", handleClick);
  document.addEventListener("submit", handleSearchSubmit);
  document.addEventListener("lpRevistaAnalytics:event", handleCustomEvent);

  window.lpRevistaAnalytics = {
    track: track,
    trackFormSuccess: function (formName, params) {
      var payload = params || {};
      var eventName = payload.event_name || "generate_lead";
      payload.form_name = formName;
      payload.page_path = payload.page_path || pagePath();
      delete payload.event_name;
      track(eventName, payload);
    },
  };
}());
