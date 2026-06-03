(function () {
  "use strict";

  function ready(callback) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback, { once: true });
      return;
    }
    callback();
  }

  function storageKey(poll) {
    return "lpRevistaPollVote:" + (poll.dataset.lpPollSource || "config") + ":" + (poll.dataset.lpPollId || "0");
  }

  function setMessage(poll, message, status) {
    var messageNode = poll.querySelector("[data-lp-poll-message]");
    if (!messageNode) {
      return;
    }
    messageNode.textContent = message || "";
    messageNode.hidden = !message;
    messageNode.classList.toggle("is-success", status === "success");
    messageNode.classList.toggle("is-error", status === "error");
  }

  function setSubmitted(poll, submitted) {
    Array.prototype.forEach.call(poll.querySelectorAll("input[type='radio'], [data-lp-poll-submit]"), function (control) {
      control.disabled = submitted;
    });
  }

  function rememberVote(poll) {
    try {
      window.sessionStorage.setItem(storageKey(poll), "1");
    } catch (error) {
      return;
    }
  }

  function hasRememberedVote(poll) {
    try {
      return window.sessionStorage.getItem(storageKey(poll)) === "1";
    } catch (error) {
      return false;
    }
  }

  function selectedOptionLabel(selected) {
    var label = selected ? selected.closest("label") : null;
    var text = label ? label.querySelector("span") : null;
    return text ? text.textContent : "";
  }

  function pollQuestion(poll) {
    var question = poll.querySelector("h3");
    return question ? question.textContent : "";
  }

  function trackPollVote(poll, selected) {
    if (!window.lpRevistaAnalytics || typeof window.lpRevistaAnalytics.track !== "function") {
      return;
    }
    window.lpRevistaAnalytics.track("poll_vote", {
      question: pollQuestion(poll),
      option_label: selectedOptionLabel(selected),
      source_type: poll.dataset.lpPollSource || "config",
      page_path: window.location.pathname || "/",
    });
  }

  function submitVote(poll, button) {
    var selected = poll.querySelector("input[type='radio']:checked");
    if (!selected) {
      setMessage(poll, "Selecciona una opcion antes de votar.", "error");
      return;
    }

    button.disabled = true;
    setMessage(poll, "", "");

    fetch("/revista/poll/vote", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: Date.now(),
        params: {
          source_type: poll.dataset.lpPollSource || "config",
          source_id: parseInt(poll.dataset.lpPollId || "0", 10) || 0,
          option_key: selected.value,
        },
      }),
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (payload) {
        var result = payload && payload.result ? payload.result : {};
        if (result.ok) {
          rememberVote(poll);
          setSubmitted(poll, true);
          setMessage(poll, result.message || "¡Gracias! Tu voto ha sido registrado.", "success");
          if (!result.duplicate) {
            trackPollVote(poll, selected);
          }
          return;
        }
        button.disabled = false;
        setMessage(poll, result.message || "No pudimos registrar tu voto en este momento. Intentalo de nuevo mas tarde.", "error");
      })
      .catch(function () {
        button.disabled = false;
        setMessage(poll, "No pudimos registrar tu voto en este momento. Intentalo de nuevo mas tarde.", "error");
      });
  }

  function initPoll(poll) {
    if (poll.dataset.lpPollReady === "1") {
      return;
    }
    poll.dataset.lpPollReady = "1";

    var button = poll.querySelector("[data-lp-poll-submit]");
    if (!button) {
      return;
    }

    if (hasRememberedVote(poll)) {
      setSubmitted(poll, true);
      setMessage(poll, "Ya registramos tu voto en esta encuesta.", "success");
      return;
    }

    button.addEventListener("click", function () {
      submitVote(poll, button);
    });
  }

  ready(function () {
    Array.prototype.forEach.call(document.querySelectorAll(".lp-revista [data-lp-poll]"), initPoll);
  });
}());
