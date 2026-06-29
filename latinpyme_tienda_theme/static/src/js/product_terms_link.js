/** @odoo-module **/

function rewriteProductTermsLink(root = document) {
    if (!window.location?.pathname?.startsWith("/shop")) {
        return;
    }
    root
        .querySelectorAll(
            'a[href="/terms"], ' +
            'a[href$="/terms"], ' +
            'a[href*="/terms?"]'
        )
        .forEach((link) => {
            link.setAttribute("href", "/terminos-de-uso");
        });
}

function startObserver() {
    if (typeof document === "undefined") {
        return;
    }

    rewriteProductTermsLink();

    if (!document.body) {
        return;
    }

    const observer = new MutationObserver(() => {
        rewriteProductTermsLink();
    });
    observer.observe(document.body, { childList: true, subtree: true });
    window.setTimeout(() => observer.disconnect(), 5000);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startObserver, { once: true });
} else {
    startObserver();
}
