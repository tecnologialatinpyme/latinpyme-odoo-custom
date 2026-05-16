(function () {
  "use strict";

  function ready(callback) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback, { once: true });
      return;
    }
    callback();
  }

  function matchesFilter(element, filter) {
    if (!filter || filter === "all") {
      return true;
    }
    var parts = filter.split(":");
    var kind = parts[0];
    var value = parts[1];
    if (!value) {
      return true;
    }
    if (kind === "type") {
      return (element.dataset.eventTypes || element.dataset.eventType || "").split(" ").indexOf(value) !== -1;
    }
    if (kind === "modality") {
      return (element.dataset.eventModalities || element.dataset.eventModality || "").split(" ").indexOf(value) !== -1;
    }
    return true;
  }

  function initCalendar(calendar) {
    if (calendar.dataset.lpProgramCalendarReady === "1") {
      return;
    }
    calendar.dataset.lpProgramCalendarReady = "1";

    var activeFilter = "all";
    var drawer = calendar.querySelector(".lp-revista-program-drawer");
    var drawerContent = calendar.querySelector("[data-program-drawer-content]");
    var filterButtons = document.querySelectorAll("[data-program-filter]");
    var days = calendar.querySelectorAll(".lp-revista-year-day.has-events");
    var months = calendar.querySelectorAll(".lp-revista-year-month");
    var upcomingCards = document.querySelectorAll(".lp-revista-program-upcoming-card");
    var noFilter = calendar.querySelector(".lp-revista-program-no-filter");

    function getDayCards(day) {
      var template = day.querySelector(".lp-revista-program-day-template");
      if (!template) {
        return [];
      }
      return Array.prototype.slice.call(template.querySelectorAll(".lp-revista-program-detail-card"));
    }

    function getFilteredDayCount(day, filter) {
      return getDayCards(day).filter(function (card) {
        return matchesFilter(card, filter);
      }).length;
    }

    function setDayCount(day, count) {
      var button = day.querySelector(".lp-revista-year-day__button");
      if (!button) {
        return;
      }
      var badge = button.querySelector("em");
      button.dataset.eventCount = String(count);
      day.dataset.filteredEventCount = String(count);
      if (badge) {
        badge.textContent = String(count);
        badge.hidden = count < 1 || (activeFilter === "all" && count < 2);
      }
    }

    function setMonthCount(month, count) {
      var label = month.querySelector(".lp-revista-year-month__header span");
      if (label) {
        label.textContent = count + (count === 1 ? " evento" : " eventos");
      }
    }

    function setDrawer(open) {
      if (!drawer) {
        return;
      }
      drawer.classList.toggle("is-open", open);
      drawer.setAttribute("aria-hidden", open ? "false" : "true");
      document.documentElement.classList.toggle("lp-revista-program-drawer-open", open);
    }

    function closeDrawer() {
      setDrawer(false);
    }

    function showDay(day) {
      if (!matchesFilter(day, activeFilter)) {
        return;
      }
      var template = day.querySelector(".lp-revista-program-day-template");
      if (!template || !drawerContent) {
        return;
      }
      drawerContent.innerHTML = template.innerHTML;
      var visibleCards = 0;
      Array.prototype.forEach.call(drawerContent.querySelectorAll(".lp-revista-program-detail-card"), function (card) {
        if (!matchesFilter(card, activeFilter)) {
          card.remove();
          return;
        }
        visibleCards += 1;
      });
      if (!visibleCards) {
        return;
      }
      setDrawer(true);
    }

    function applyFilter(filter) {
      activeFilter = filter || "all";
      var visibleDayCount = 0;

      Array.prototype.forEach.call(filterButtons, function (button) {
        button.classList.toggle("is-active", button.dataset.programFilter === activeFilter);
      });

      Array.prototype.forEach.call(days, function (day) {
        var filteredCount = getFilteredDayCount(day, activeFilter);
        var isMatch = filteredCount > 0;
        if (isMatch) {
          visibleDayCount += 1;
        }
        setDayCount(day, filteredCount);
        day.classList.toggle("is-filter-muted", !isMatch);
        day.classList.toggle("is-filter-hit", isMatch && activeFilter !== "all");
      });

      Array.prototype.forEach.call(months, function (month) {
        var monthEventCount = 0;
        Array.prototype.forEach.call(month.querySelectorAll(".lp-revista-year-day.has-events"), function (day) {
          monthEventCount += parseInt(day.dataset.filteredEventCount || "0", 10);
        });
        var hasMatch = monthEventCount > 0;
        setMonthCount(month, monthEventCount);
        month.classList.toggle("is-filter-empty", !hasMatch && activeFilter !== "all");
      });

      Array.prototype.forEach.call(upcomingCards, function (card) {
        card.hidden = !matchesFilter(card, activeFilter);
      });

      if (noFilter) {
        noFilter.hidden = visibleDayCount > 0 || activeFilter === "all";
      }
    }

    Array.prototype.forEach.call(days, function (day) {
      var button = day.querySelector(".lp-revista-year-day__button");
      if (!button) {
        return;
      }
      button.addEventListener("click", function () {
        showDay(day);
      });
    });

    Array.prototype.forEach.call(filterButtons, function (button) {
      button.addEventListener("click", function () {
        applyFilter(button.dataset.programFilter || "all");
        closeDrawer();
      });
    });

    if (drawer) {
      Array.prototype.forEach.call(drawer.querySelectorAll("[data-program-drawer-close]"), function (button) {
        button.addEventListener("click", closeDrawer);
      });
    }

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        closeDrawer();
      }
    });

    applyFilter("all");
  }

  ready(function () {
    Array.prototype.forEach.call(document.querySelectorAll("[data-lp-program-calendar]"), initCalendar);
  });
})();
