/** @odoo-module **/

function rewriteProductTermsLink(root) {
    var path = (window.location && window.location.pathname) || "";
    if (path.indexOf("/shop") !== 0) {
        return;
    }
    root = root || document;
    root
        .querySelectorAll(
            'a[href="/terms"], ' +
            'a[href$="/terms"], ' +
            'a[href*="/terms?"]'
        )
        .forEach(function (link) {
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

    rewriteProductTermsLink(document);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startObserver, { once: true });
} else {
    startObserver();
}
