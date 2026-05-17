(function () {
  "use strict";

  var mobileQuery = window.matchMedia("(max-width: 760px)");

  function forEachNode(nodes, callback) {
    Array.prototype.forEach.call(nodes, callback);
  }

  function setGroupOpen(group, open) {
    var toggle = group.querySelector(".lp-revista-footer__toggle");
    group.classList.toggle("is-open", open);
    if (toggle) {
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    }
  }

  function closeSiblingGroups(group) {
    if (!group.parentElement) {
      return;
    }
    forEachNode(group.parentElement.querySelectorAll(".lp-revista-footer__group.is-open"), function (sibling) {
      if (sibling !== group) {
        setGroupOpen(sibling, false);
      }
    });
  }

  function initFooter(footer) {
    forEachNode(footer.querySelectorAll(".lp-revista-footer__group"), function (group) {
      var toggle = group.querySelector(".lp-revista-footer__toggle");
      if (!toggle) {
        return;
      }

      toggle.addEventListener("click", function () {
        if (!mobileQuery.matches) {
          return;
        }
        var willOpen = !group.classList.contains("is-open");
        closeSiblingGroups(group);
        setGroupOpen(group, willOpen);
      });
    });
  }

  function closeAllFooters() {
    forEachNode(document.querySelectorAll(".lp-revista-footer__group.is-open"), function (group) {
      setGroupOpen(group, false);
    });
  }

  function init() {
    forEachNode(document.querySelectorAll(".lp-revista-footer"), initFooter);
  }

  function handleViewportChange(event) {
    if (!event.matches) {
      closeAllFooters();
    }
  }

  if (mobileQuery.addEventListener) {
    mobileQuery.addEventListener("change", handleViewportChange);
  } else if (mobileQuery.addListener) {
    mobileQuery.addListener(handleViewportChange);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
}());
