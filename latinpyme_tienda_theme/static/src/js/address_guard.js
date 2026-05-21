import { CustomerAddress } from "@portal/interactions/address";
import { patch } from "@web/core/utils/patch";

// Odoo's address interaction expects these fields to exist on the checkout form.
// Keep the guard local to the address form and only create missing hidden fallbacks.
function hiddenWrap(form, name) {
    const wrap = document.createElement("div");
    wrap.hidden = true;
    wrap.dataset.lpTiendaAddressGuard = name;
    form.appendChild(wrap);
    return wrap;
}

function ensureHiddenInput(form, name, value = "") {
    if (form.elements[name]) {
        return form.elements[name];
    }
    const input = document.createElement("input");
    input.type = "hidden";
    input.name = name;
    input.id = `lp_tienda_${name}`;
    input.value = value;
    hiddenWrap(form, name).appendChild(input);
    return input;
}

function ensureHiddenSelect(form, name) {
    const select = form.querySelector(`select[name="${name}"]`);
    if (select) {
        return select;
    }
    const existing = form.elements[name];
    const value = existing?.value || "";
    if (existing?.removeAttribute) {
        existing.dataset.lpTiendaOriginalName = name;
        existing.removeAttribute("name");
    }
    const hiddenSelect = document.createElement("select");
    hiddenSelect.name = name;
    hiddenSelect.id = `lp_tienda_${name}`;
    hiddenSelect.hidden = true;
    hiddenSelect.appendChild(new Option("", ""));
    if (value) {
        hiddenSelect.appendChild(new Option(value, value, true, true));
    }
    hiddenWrap(form, name).appendChild(hiddenSelect);
    return hiddenSelect;
}

function ensureAddressCompatibility(root) {
    const form = root?.querySelector?.("form.address_autoformat");
    if (!form) {
        return null;
    }

    ensureHiddenInput(form, "address_type", "billing");
    ensureHiddenInput(form, "required_fields");
    ensureHiddenInput(form, "street");
    ensureHiddenInput(form, "zip");
    ensureHiddenInput(form, "city");
    ensureHiddenInput(form, "phone");
    ensureHiddenSelect(form, "country_id");
    ensureHiddenSelect(form, "state_id");

    return form;
}

patch(CustomerAddress.prototype, {
    async start() {
        ensureAddressCompatibility(this.el);
        if (typeof super.start !== "function") {
            return;
        }
        try {
            return await super.start(...arguments);
        } catch (error) {
            const message = error?.message || "";
            if (error instanceof TypeError && message.includes("dispatchEvent")) {
                return;
            }
            throw error;
        }
    },

    setup() {
        const form = ensureAddressCompatibility(this.el);
        if (!form) {
            this.addressForm = null;
            return;
        }
        return super.setup(...arguments);
    },

    async willStart() {
        if (!ensureAddressCompatibility(this.el)?.country_id?.value) {
            return;
        }
        return super.willStart(...arguments);
    },

    async _onChangeCountry() {
        if (!this.addressForm?.country_id?.value) {
            return;
        }
        return super._onChangeCountry(...arguments);
    },

    _showInput(name) {
        const input = this.addressForm?.[name];
        if (!input?.parentElement) {
            return;
        }
        return super._showInput(...arguments);
    },

    _hideInput(name) {
        const input = this.addressForm?.[name];
        if (!input?.parentElement) {
            return;
        }
        return super._hideInput(...arguments);
    },

    _getInputDiv(name) {
        return this.addressForm?.[name]?.parentElement || null;
    },

    async saveAddress() {
        if (!this.addressForm) {
            return;
        }
        return super.saveAddress(...arguments);
    },
});
