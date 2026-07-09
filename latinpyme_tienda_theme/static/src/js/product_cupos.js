/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { WebsiteSale } from "@website_sale/interactions/website_sale";
import { rpc } from "@web/core/network/rpc";
import { localization } from "@web/core/l10n/localization";
import { insertThousandsSep } from "@web/core/utils/numbers";

// Reuses Odoo's own combination-info RPC (the same one the native +/- quantity
// selector triggers) to price each "cupos" card. No pricing/discount logic is
// computed here: every number comes from the pricelist resolved server-side.

const lastComboKeyByParent = new WeakMap();

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

function getCuposBlock(parent) {
    return parent.querySelector(".lp-tienda-cupos-block");
}

function setActiveCard(block, qty) {
    const target = Math.max(1, Math.round(qty || 1));
    block.querySelectorAll(".lp-tienda-cupos-card").forEach((card) => {
        const isActive = parseInt(card.dataset.lpCuposOption, 10) === target;
        card.classList.toggle("is-active", isActive);
        card.setAttribute("aria-pressed", isActive ? "true" : "false");
    });
}

function updateCuposTotal(parent, combination) {
    const summary = parent.querySelector("[data-lp-tienda-cupos-summary]");
    const priceEl = parent.querySelector(".oe_price");
    if (!summary || !priceEl) {
        return;
    }
    const qtyInput = parent.querySelector('input[name="add_qty"]');
    const qty = Math.max(1, parseFloat(qtyInput?.value || "1"));
    const totalPriceEl = summary.querySelector("[data-lp-cupos-total-price]");
    if (totalPriceEl) {
        totalPriceEl.textContent = formatWithSameCurrency(
            priceEl,
            combination.price * qty,
            combination.currency_precision
        );
    }
}

/**
 * Fetches the unit price for each cupos card (1 to 4) using the same public
 * RPC the native quantity selector uses, and fills in price + savings badge.
 */
async function refreshCuposCardPrices(parent) {
    const block = getCuposBlock(parent);
    if (!block) {
        return;
    }
    const cards = Array.from(block.querySelectorAll(".lp-tienda-cupos-card"));
    if (!cards.length) {
        return;
    }
    const productTemplateId = parseInt(parent.querySelector(".product_template_id")?.value);
    if (!productTemplateId) {
        return;
    }
    const productId = parseInt(parent.querySelector(".product_id")?.value) || 0;
    const combination = Array.from(
        parent.querySelectorAll("input.js_variant_change:checked, select.js_variant_change")
    ).map((el) => parseInt(el.value));
    const uomId = parseInt(parent.querySelector('input[name="uom_id"]:checked')?.value) || undefined;

    let results;
    try {
        results = await Promise.all(
            cards.map((card) =>
                rpc("/website_sale/get_combination_info", {
                    product_template_id: productTemplateId,
                    product_id: productId,
                    combination,
                    add_qty: parseInt(card.dataset.lpCuposOption, 10),
                    uom_id: uomId,
                }).then((info) => ({ card, info }))
            )
        );
    } catch {
        // Native mechanism unavailable (offline, combination invalid, ...):
        // leave cards without a price rather than showing a stale/invented one.
        return;
    }

    const priceEl = parent.querySelector(".oe_price");
    if (!priceEl) {
        return;
    }
    const baseline = results.find((r) => parseInt(r.card.dataset.lpCuposOption, 10) === 1);
    const basePrice = baseline ? baseline.info.price : null;
    const minPrice = Math.min(...results.map((r) => r.info.price));

    for (const { card, info } of results) {
        const priceSpan = card.querySelector("[data-lp-cupos-option-price]");
        if (priceSpan) {
            priceSpan.textContent = `${formatWithSameCurrency(
                priceEl,
                info.price,
                info.currency_precision
            )} c/u`;
        }
        const badge = card.querySelector("[data-lp-cupos-option-badge]");
        if (!badge) {
            continue;
        }
        const isDiscounted = basePrice !== null && info.price < basePrice;
        if (isDiscounted && info.price === minPrice) {
            badge.textContent = "Mejor valor";
            badge.classList.remove("d-none");
        } else if (isDiscounted) {
            badge.textContent = "Ahorra";
            badge.classList.remove("d-none");
        } else {
            badge.classList.add("d-none");
        }
    }
}

patch(WebsiteSale.prototype, {
    _onChangeCombination(ev, parent, combination) {
        super._onChangeCombination(ev, parent, combination);

        const block = getCuposBlock(parent);
        if (!block) {
            return;
        }
        const qtyInput = parent.querySelector('input[name="add_qty"]');
        setActiveCard(block, parseFloat(qtyInput?.value || "1"));
        updateCuposTotal(parent, combination);

        const comboKey = combination.display_name || "";
        if (lastComboKeyByParent.get(parent) !== comboKey) {
            lastComboKeyByParent.set(parent, comboKey);
            refreshCuposCardPrices(parent);
        }
    },
});

document.addEventListener(
    "click",
    (ev) => {
        const card = ev.target.closest(".lp-tienda-cupos-card");
        if (!card) {
            return;
        }
        const parent = card.closest(".js_product");
        const input = parent?.querySelector('input[name="add_qty"]');
        if (!input) {
            return;
        }
        const qty = parseInt(card.dataset.lpCuposOption, 10);
        if (!qty) {
            return;
        }
        setActiveCard(getCuposBlock(parent), qty);
        if (parseFloat(input.value) !== qty) {
            input.value = qty;
            input.dispatchEvent(new Event("change", { bubbles: true }));
        }
    },
    true
);

// No separate "on load" fetch is needed: Odoo's own WebsiteSale.start() already
// triggers a combination-info call for every product page (to compute the
// "out of stock" state), which reaches our patched _onChangeCombination above
// and performs the first cards price fetch.
