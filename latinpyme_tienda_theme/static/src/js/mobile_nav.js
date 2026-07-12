/** @odoo-module **/

// Mobile hamburger menu for the Tienda masthead. Native <select>/hover-based
// dropdowns don't work on touch devices, so below the tablet breakpoint the
// nav panel is hidden by default and toggled via this button, and each
// dropdown item expands on click instead of relying on :hover.

const MOBILE_BREAKPOINT = 899;

function closeDropdown(item) {
    item.classList.remove("is-open");
    item.querySelector(".lp-tienda-nav__toggle")?.setAttribute("aria-expanded", "false");
}

function closeMobileNav(toggle, nav) {
    nav.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.classList.remove("is-active");
    document.body.classList.remove("lp-tienda-nav-open");
    nav.querySelectorAll(".lp-tienda-nav__item--dropdown.is-open").forEach(closeDropdown);
}

function initMobileNav(root) {
    const toggle = root.querySelector(".lp-tienda-nav-toggle");
    const nav = root.querySelector(".lp-tienda-nav");
    if (!toggle || !nav || toggle.dataset.lpTiendaNavBound === "1") {
        return;
    }
    toggle.dataset.lpTiendaNavBound = "1";

    toggle.addEventListener("click", () => {
        const isOpen = !nav.classList.contains("is-open");
        if (isOpen) {
            nav.classList.add("is-open");
            toggle.setAttribute("aria-expanded", "true");
            toggle.classList.add("is-active");
            document.body.classList.add("lp-tienda-nav-open");
        } else {
            closeMobileNav(toggle, nav);
        }
    });

    nav.querySelectorAll(".lp-tienda-nav__item--dropdown").forEach((item) => {
        const dropdownToggle = item.querySelector(".lp-tienda-nav__toggle");
        dropdownToggle?.addEventListener("click", (ev) => {
            if (window.innerWidth > MOBILE_BREAKPOINT) {
                return;
            }
            ev.preventDefault();
            const isOpen = item.classList.contains("is-open");
            nav.querySelectorAll(".lp-tienda-nav__item--dropdown.is-open").forEach(closeDropdown);
            if (!isOpen) {
                item.classList.add("is-open");
                dropdownToggle.setAttribute("aria-expanded", "true");
            }
        });
    });

    nav.querySelectorAll(".lp-tienda-nav__link:not(.lp-tienda-nav__toggle), .lp-tienda-nav__dropdown-link").forEach((link) => {
        link.addEventListener("click", () => closeMobileNav(toggle, nav));
    });
}

function start() {
    document.querySelectorAll(".lp-tienda-masthead").forEach(initMobileNav);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
} else {
    start();
}
