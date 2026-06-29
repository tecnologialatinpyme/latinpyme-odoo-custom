/** @odoo-module **/

function initCarousel(carousel) {
  const track = carousel.querySelector(".lp-tienda-product-carousel__track");
  const prevButton = carousel.querySelector(".lp-tienda-product-carousel__control--prev");
  const nextButton = carousel.querySelector(".lp-tienda-product-carousel__control--next");

  if (!track || !prevButton || !nextButton) {
    return;
  }

  const step = () => Math.max(track.clientWidth * 0.85, 240);
  let rafId = null;

  const updateState = () => {
    const maxScrollLeft = Math.max(track.scrollWidth - track.clientWidth - 1, 0);
    const isScrollable = maxScrollLeft > 0;
    const atStart = track.scrollLeft <= 0;
    const atEnd = track.scrollLeft >= maxScrollLeft;

    carousel.classList.toggle("is-scrollable", isScrollable);
    prevButton.disabled = !isScrollable || atStart;
    nextButton.disabled = !isScrollable || atEnd;
  };

  const scheduleUpdate = () => {
    if (rafId) {
      cancelAnimationFrame(rafId);
    }
    rafId = requestAnimationFrame(updateState);
  };

  prevButton.addEventListener("click", () => {
    track.scrollBy({ left: -step(), behavior: "smooth" });
  });

  nextButton.addEventListener("click", () => {
    track.scrollBy({ left: step(), behavior: "smooth" });
  });

  track.addEventListener("scroll", scheduleUpdate, { passive: true });

  if ("ResizeObserver" in window) {
    const observer = new ResizeObserver(scheduleUpdate);
    observer.observe(track);
    observer.observe(carousel);
  } else {
    window.addEventListener("resize", scheduleUpdate);
  }

  updateState();
}

function initAllCarousels() {
  document.querySelectorAll(".lp-tienda-product-carousel").forEach(initCarousel);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initAllCarousels, { once: true });
} else {
  initAllCarousels();
}
