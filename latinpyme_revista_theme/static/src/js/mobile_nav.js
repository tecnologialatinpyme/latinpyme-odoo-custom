(function () {
  "use strict";

  var mobileQuery = window.matchMedia("(max-width: 760px)");

  function forEachNode(nodes, callback) {
    Array.prototype.forEach.call(nodes, callback);
  }

  function directChildByClass(parent, className) {
    for (var i = 0; i < parent.children.length; i += 1) {
      if (parent.children[i].classList.contains(className)) {
        return parent.children[i];
      }
    }
    return null;
  }

  function directToggle(item) {
    return directChildByClass(item, "lp-revista-nav__toggle") || directChildByClass(item, "lp-revista-nav__subtoggle");
  }

  function setItemOpen(item, open) {
    var toggle = directToggle(item);
    item.classList.toggle("is-open", open);
    if (toggle) {
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    }
  }

  function closeDescendants(item) {
    forEachNode(item.querySelectorAll(".is-open"), function (openItem) {
      setItemOpen(openItem, false);
    });
  }

  function closeSiblings(item) {
    if (!item.parentElement) {
      return;
    }
    forEachNode(item.parentElement.children, function (sibling) {
      if (sibling !== item && sibling.classList && sibling.classList.contains("is-open")) {
        closeDescendants(sibling);
        setItemOpen(sibling, false);
      }
    });
  }

  function closeNav(masthead) {
    var toggle = masthead.querySelector(".lp-revista-mobile-toggle");
    masthead.classList.remove("is-mobile-nav-open");
    if (toggle) {
      toggle.setAttribute("aria-expanded", "false");
    }
    forEachNode(masthead.querySelectorAll(".is-open"), function (item) {
      setItemOpen(item, false);
    });
  }

  function openNav(masthead) {
    var toggle = masthead.querySelector(".lp-revista-mobile-toggle");
    masthead.classList.add("is-mobile-nav-open");
    if (toggle) {
      toggle.setAttribute("aria-expanded", "true");
    }
  }

  function initMasthead(masthead) {
    var toggle = masthead.querySelector(".lp-revista-mobile-toggle");
    var close = masthead.querySelector(".lp-revista-mobile-close");
    var backdrop = masthead.querySelector(".lp-revista-mobile-backdrop");
    var nav = masthead.querySelector(".lp-revista-nav");

    if (!toggle || !nav) {
      return;
    }

    toggle.addEventListener("click", function () {
      if (masthead.classList.contains("is-mobile-nav-open")) {
        closeNav(masthead);
      } else {
        openNav(masthead);
      }
    });

    [close, backdrop].forEach(function (control) {
      if (control) {
        control.addEventListener("click", function () {
          closeNav(masthead);
        });
      }
    });

    forEachNode(nav.querySelectorAll(".lp-revista-nav__toggle, .lp-revista-nav__subtoggle"), function (button) {
      button.addEventListener("click", function (event) {
        if (!mobileQuery.matches) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();

        var item = button.closest(".lp-revista-nav__item--dropdown, .lp-revista-nav__subitem");
        if (!item) {
          return;
        }

        var willOpen = !item.classList.contains("is-open");
        closeSiblings(item);
        closeDescendants(item);
        setItemOpen(item, willOpen);
      });
    });

    forEachNode(nav.querySelectorAll("a[href]"), function (link) {
      link.addEventListener("click", function () {
        if (mobileQuery.matches) {
          closeNav(masthead);
        }
      });
    });
  }

  function init() {
    forEachNode(document.querySelectorAll(".lp-revista-masthead"), initMasthead);
  }

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      forEachNode(document.querySelectorAll(".lp-revista-masthead.is-mobile-nav-open"), closeNav);
    }
  });

  function handleViewportChange(event) {
    if (!event.matches) {
      forEachNode(document.querySelectorAll(".lp-revista-masthead"), closeNav);
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
