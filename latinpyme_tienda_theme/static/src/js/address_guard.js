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

function fieldWrap(form, name) {
    const field = form.elements[name];
    return field?.closest?.(`.div_${name}, [data-name="${name}"], .mb-3, .form-group`) || field?.parentElement || null;
}

function labelForField(form, name) {
    const field = form.elements[name];
    return field?.id ? field.parentElement?.querySelector(`label[for="${field.id}"]`) : null;
}

function makeZipOptional(form) {
    const requiredFields = form.elements.required_fields;
    if (requiredFields?.value) {
        requiredFields.value = requiredFields.value
            .split(",")
            .map((fieldName) => fieldName.trim())
            .filter((fieldName) => fieldName && fieldName !== "zip")
            .join(",");
    }

    const zip = form.elements.zip;
    if (zip) {
        zip.required = false;
        zip.removeAttribute("required");
        zip.classList.remove("is-invalid");
    }

    const label = labelForField(form, "zip");
    label?.classList.add("label-optional");
    if (label && !label.children.length) {
        label.textContent = label.textContent.replace(/\s*\*+\s*$/, "");
    }
}

function arrangeAddressFields(form) {
    const streetWrap = fieldWrap(form, "street");
    const orderedWraps = ["country_id", "state_id", "city", "zip"]
        .map((fieldName) => fieldWrap(form, fieldName))
        .filter(Boolean);

    if (!streetWrap || !orderedWraps.length) {
        return;
    }

    const row = streetWrap.parentElement;
    if (!row || !orderedWraps.every((wrap) => wrap.parentElement === row)) {
        setAddressFieldLayout(form);
        return;
    }

    streetWrap.after(...orderedWraps);
    setAddressFieldLayout(form);
}

function setAddressFieldLayout(form) {
    [
        ["country_id", "10"],
        ["state_id", "11"],
        ["city", "12"],
        ["zip", "13"],
    ].forEach(([fieldName, order]) => {
        const wrap = fieldWrap(form, fieldName);
        if (!wrap || wrap.hidden || wrap.dataset.lpTiendaAddressGuard) {
            return;
        }
        wrap.classList.remove("col-md-3", "col-md-4", "col-md-5", "col-md-7", "col-md-8", "col-lg-3", "col-lg-4", "col-lg-5", "col-lg-7", "col-lg-8");
        wrap.classList.add("col-12", "col-md-6");
        wrap.style.order = order;
    });
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
    makeZipOptional(form);
    arrangeAddressFields(form);

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
        const result = await super._onChangeCountry(...arguments);
        makeZipOptional(this.addressForm);
        arrangeAddressFields(this.addressForm);
        return result;
    },

    _markRequired(name, required) {
        if (name === "zip") {
            required = false;
        }
        const result = super._markRequired(name, required);
        if (name === "zip" && this.addressForm) {
            makeZipOptional(this.addressForm);
        }
        return result;
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
        makeZipOptional(this.addressForm);
        arrangeAddressFields(this.addressForm);
        return super.saveAddress(...arguments);
    },
});
