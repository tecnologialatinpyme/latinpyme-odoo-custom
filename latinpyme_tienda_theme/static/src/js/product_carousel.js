/** @odoo-module **/

// Arrow + dot navigation for the ECOMMERCE carousels on the Tienda home.
// No autoplay - the track keeps its native overflow-x/scroll-snap swipe
// behavior (see tienda.scss), this only adds optional manual controls on
// top of it via scrollBy/scrollTo. Dots are grouped by visible "page" of
// slides, not one per product, so categories with 10 products don't end
// up with 10 dots.

function getSlideStep(track) {
    const slide = track.children[0];
    if (!slide) {
        return 0;
    }
    const trackStyle = getComputedStyle(track);
    const gap = parseFloat(trackStyle.columnGap || trackStyle.gap || "0") || 0;
    return slide.getBoundingClientRect().width + gap;
}

function getPageSize(track) {
    const step = getSlideStep(track);
    if (!step) {
        return 1;
    }
    return Math.max(1, Math.round(track.clientWidth / step));
}

function getPageCount(track, pageSize) {
    const count = track.children.length;
    if (!count) {
        return 1;
    }
    return Math.max(1, Math.ceil(count / pageSize));
}

function scrollToPage(track, page, pageSize, smooth) {
    const step = getSlideStep(track);
    const maxLeft = track.scrollWidth - track.clientWidth;
    const left = Math.min(maxLeft, Math.max(0, page * pageSize * step));
    track.scrollTo({ left, behavior: smooth ? "smooth" : "auto" });
}

function initProductCarousel(section) {
    const viewport = section.querySelector(".lp-tienda-product-carousel__viewport");
    const track = section.querySelector(".lp-tienda-product-carousel__track");
    const prevBtn = section.querySelector(".lp-tienda-product-carousel__arrow--prev");
    const nextBtn = section.querySelector(".lp-tienda-product-carousel__arrow--next");
    const dotsWrap = section.querySelector(".lp-tienda-product-carousel__dots");
    if (!viewport || !track || !prevBtn || !nextBtn || !dotsWrap || track.dataset.lpTiendaCarouselBound === "1") {
        return;
    }
    track.dataset.lpTiendaCarouselBound = "1";

    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let pageSize = 1;
    let pageCount = 1;
    let dots = [];

    function currentPage() {
        const step = getSlideStep(track);
        if (!step) {
            return 0;
        }
        const approxIndex = Math.round(track.scrollLeft / step);
        return Math.min(pageCount - 1, Math.round(approxIndex / pageSize));
    }

    function buildDots() {
        dotsWrap.innerHTML = "";
        dots = [];
        for (let i = 0; i < pageCount; i++) {
            const dot = document.createElement("button");
            dot.type = "button";
            dot.className = "lp-tienda-product-carousel__dot";
            dot.setAttribute("aria-label", "Ir a la página " + (i + 1));
            dot.addEventListener("click", () => scrollToPage(track, i, pageSize, !prefersReducedMotion));
            dotsWrap.appendChild(dot);
            dots.push(dot);
        }
    }

    function updateActiveDot() {
        const page = currentPage();
        dots.forEach((dot, index) => dot.classList.toggle("is-active", index === page));
    }

    function updateArrows() {
        const atStart = track.scrollLeft <= 1;
        const atEnd = track.scrollLeft >= track.scrollWidth - track.clientWidth - 1;
        prevBtn.classList.toggle("is-disabled", atStart);
        nextBtn.classList.toggle("is-disabled", atEnd);
    }

    function refresh() {
        pageSize = getPageSize(track);
        pageCount = getPageCount(track, pageSize);
        const hasOverflow = track.scrollWidth > track.clientWidth + 1;
        prevBtn.classList.toggle("lp-tienda-product-carousel__arrow--hidden", !hasOverflow);
        nextBtn.classList.toggle("lp-tienda-product-carousel__arrow--hidden", !hasOverflow);
        buildDots();
        updateActiveDot();
        updateArrows();
    }

    prevBtn.addEventListener("click", () => {
        scrollToPage(track, Math.max(0, currentPage() - 1), pageSize, !prefersReducedMotion);
    });
    nextBtn.addEventListener("click", () => {
        scrollToPage(track, Math.min(pageCount - 1, currentPage() + 1), pageSize, !prefersReducedMotion);
    });

    let scrollTimer = null;
    track.addEventListener(
        "scroll",
        () => {
            window.clearTimeout(scrollTimer);
            scrollTimer = window.setTimeout(() => {
                updateActiveDot();
                updateArrows();
            }, 80);
        },
        { passive: true }
    );

    let resizeTimer = null;
    window.addEventListener("resize", () => {
        window.clearTimeout(resizeTimer);
        resizeTimer = window.setTimeout(refresh, 150);
    });

    refresh();
}

function start() {
    document.querySelectorAll(".lp-tienda-product-carousel").forEach(initProductCarousel);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
} else {
    start();
}
