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
      Array.prototype.forEach.call(drawerContent.querySelectorAll(".lp-revista-program-detail-card"), function (card) {
        card.hidden = !matchesFilter(card, activeFilter);
      });
      setDrawer(true);
    }

    function applyFilter(filter) {
      activeFilter = filter || "all";
      var visibleDayCount = 0;

      Array.prototype.forEach.call(filterButtons, function (button) {
        button.classList.toggle("is-active", button.dataset.programFilter === activeFilter);
      });

      Array.prototype.forEach.call(days, function (day) {
        var isMatch = matchesFilter(day, activeFilter);
        if (isMatch) {
          visibleDayCount += 1;
        }
        day.classList.toggle("is-filter-muted", !isMatch);
        day.classList.toggle("is-filter-hit", isMatch && activeFilter !== "all");
      });

      Array.prototype.forEach.call(months, function (month) {
        var hasMatch = !!month.querySelector(".lp-revista-year-day.has-events:not(.is-filter-muted)");
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
