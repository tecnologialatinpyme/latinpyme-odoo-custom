/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { WebsiteSale } from "@website_sale/interactions/website_sale";
import { localization } from "@web/core/l10n/localization";
import { insertThousandsSep } from "@web/core/utils/numbers";

// Reuses Odoo's own combination-info result (price, list_price,
// has_discounted_price, currency_precision) to render a "cupos" summary.
// Does not compute or duplicate any pricing/discount logic: the numbers
// come straight from the pricelist RPC that Odoo already performs on
// quantity change.

function getCurrencyParts(priceEl) {
    const valueEl = priceEl.querySelector(".oe_currency_value");
    if (!valueEl) {
        return null;
    }
    const fullText = priceEl.textContent;
    const valueText = valueEl.textContent;
    const idx = fullText.indexOf(valueText);
    if (idx === -1) {
        return null;
    }
    return {
        before: fullText.slice(0, idx),
        after: fullText.slice(idx + valueText.length),
    };
}

function formatWithSameCurrency(priceEl, amount, precision) {
    const formatted = amount.toFixed(Number.isInteger(precision) ? precision : 2).split(".");
    const { thousandsSep, decimalPoint, grouping } = localization;
    formatted[0] = insertThousandsSep(formatted[0], thousandsSep, grouping);
    const numberText = formatted.join(decimalPoint);
    const parts = getCurrencyParts(priceEl);
    return parts ? `${parts.before}${numberText}${parts.after}` : numberText;
}

function pluralizeCupos(qty) {
    const n = Math.max(1, Math.round(qty || 1));
    return `${n} ${n === 1 ? "cupo" : "cupos"}`;
}

function updateCuposSummary(parent, combination) {
    const summary = parent.querySelector("[data-lp-tienda-cupos-summary]");
    if (!summary) {
        return;
    }
    const priceEl = parent.querySelector(".oe_price");
    const qtyInput = parent.querySelector('input[name="add_qty"]');
    const qty = Math.max(1, parseFloat(qtyInput?.value || "1"));
    const precision = combination.currency_precision;
    const unitPrice = combination.price;
    const listPrice = combination.list_price;
    const hasDiscount = !!combination.has_discounted_price;

    const countEl = parent.querySelector(".lp-tienda-cupos-count");
    if (countEl) {
        countEl.textContent = pluralizeCupos(qty);
    }

    if (!priceEl) {
        return;
    }

    const unitPriceEl = summary.querySelector("[data-lp-cupos-unit-price]");
    if (unitPriceEl) {
        unitPriceEl.textContent = priceEl.textContent.trim();
    }

    const totalPriceEl = summary.querySelector("[data-lp-cupos-total-price]");
    if (totalPriceEl) {
        totalPriceEl.textContent = formatWithSameCurrency(priceEl, unitPrice * qty, precision);
    }

    const savingsRow = summary.querySelector("[data-lp-cupos-savings-row]");
    const savingsEl = summary.querySelector("[data-lp-cupos-savings]");
    if (savingsRow && savingsEl) {
        if (hasDiscount && listPrice > unitPrice) {
            savingsEl.textContent = formatWithSameCurrency(
                priceEl,
                (listPrice - unitPrice) * qty,
                precision
            );
            savingsRow.classList.remove("d-none");
        } else {
            savingsRow.classList.add("d-none");
        }
    }
}

patch(WebsiteSale.prototype, {
    _onChangeCombination(ev, parent, combination) {
        super._onChangeCombination(ev, parent, combination);
        updateCuposSummary(parent, combination);
    },
});

// Instant label feedback while the price RPC (triggered natively by Odoo) is
// still in flight; the summary values above stay authoritative once it
// resolves.
document.addEventListener(
    "change",
    (ev) => {
        const input = ev.target;
        if (!input.matches || !input.matches('input[name="add_qty"]')) {
            return;
        }
        const parent = input.closest(".js_product");
        const countEl = parent?.querySelector(".lp-tienda-cupos-count");
        if (countEl) {
            countEl.textContent = pluralizeCupos(parseFloat(input.value || "1"));
        }
    },
    true
);
