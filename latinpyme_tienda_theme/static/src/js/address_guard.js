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
    if (!form?.elements) {
        return null;
    }
    const field = form.elements[name];
    if (!field?.closest) {
        return field?.parentElement || null;
    }
    const compactName = name.replace(/_id$/, "");
    return field.closest(
        `.div_${name}, .div_${compactName}, [data-name="${name}"], [data-name="${compactName}"], .lp-tienda-address-field, .mb-3, .form-group`
    ) || field.parentElement || null;
}

function labelForField(form, name) {
    const field = form.elements[name];
    return field?.id ? fieldWrap(form, name)?.querySelector(`label[for="${field.id}"]`) : null;
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
    if (label) {
        label.childNodes.forEach((node) => {
            if (node.nodeType === Node.TEXT_NODE) {
                node.nodeValue = node.nodeValue.replace(/\s*\*+\s*$/, "");
            }
        });
        label.querySelectorAll("span, sup").forEach((node) => {
            if (node.textContent.trim() === "*") {
                node.remove();
            }
        });
    }
}

function normalizeText(value = "") {
    return value
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase();
}

function isObligationsField(value = "") {
    const text = normalizeText(value);
    return (
        (text.includes("oblig") && text.includes("respons"))
        || (text.includes("l10n_co") && (text.includes("oblig") || text.includes("respons")))
        || text.includes("fiscal_respons")
        || text.includes("responsibility_ids")
        || text.includes("obligation_ids")
    );
}

function wrapperForControl(control) {
    return control?.closest?.(
        "[class*='div_'], [data-name], .lp-tienda-address-field, .mb-3, .form-group"
    ) || control?.parentElement || null;
}

function removeRequiredField(form, fieldName) {
    const requiredFields = form.elements.required_fields;
    if (!requiredFields?.value || !fieldName) {
        return;
    }
    requiredFields.value = requiredFields.value
        .split(",")
        .map((name) => name.trim())
        .filter((name) => name && name !== fieldName && !isObligationsField(name))
        .join(",");
}

function hideObligationsControl(form) {
    if (!form?.querySelectorAll) {
        return;
    }

    const requiredFields = form.elements.required_fields;
    if (requiredFields?.value) {
        requiredFields.value = requiredFields.value
            .split(",")
            .map((name) => name.trim())
            .filter((name) => name && !isObligationsField(name))
            .join(",");
    }

    const wrappers = new Set();
    form.querySelectorAll("input, select, textarea").forEach((field) => {
        const wrap = wrapperForControl(field);
        const label = field.id ? wrap?.querySelector(`label[for="${field.id}"]`) : null;
        const dataName = field.closest("[data-name]")?.dataset?.name || "";
        if (
            isObligationsField(field.name)
            || isObligationsField(field.id)
            || isObligationsField(dataName)
            || isObligationsField(label?.textContent)
        ) {
            wrappers.add(wrap);
        }
    });

    form.querySelectorAll("label").forEach((label) => {
        if (isObligationsField(label.textContent)) {
            wrappers.add(wrapperForControl(label));
        }
    });

    wrappers.forEach((wrap) => {
        if (!wrap || wrap.dataset.lpTiendaAddressGuard) {
            return;
        }
        wrap.hidden = true;
        wrap.style.display = "none";
        wrap.classList.add("d-none", "lp-tienda-address-field--hidden-obligations");
        wrap.querySelectorAll("input, select, textarea").forEach((field) => {
            removeRequiredField(form, field.name);
            field.required = false;
            field.disabled = true;
            field.removeAttribute("required");
            field.classList.remove("is-invalid");
        });
    });
}

function applyAddressAdjustments(form) {
    if (!form) {
        return;
    }
    makeZipOptional(form);
    hideObligationsControl(form);
    arrangeAddressFields(form);
}

function arrangeAddressFields(form) {
    markAddressParent(form);
    setAddressFieldLayout(form);
}

function markAddressParent(form) {
    const wrappers = ["country_id", "state_id", "city", "zip"]
        .map((fieldName) => fieldWrap(form, fieldName))
        .filter((wrap) => wrap && !wrap.hidden && !wrap.dataset.lpTiendaAddressGuard);
    const parent = wrappers[0]?.parentElement;
    if (parent && wrappers.every((wrap) => wrap.parentElement === parent)) {
        parent.classList.add("lp-tienda-address-fields", "row");
    }
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
        Array.from(wrap.classList).forEach((className) => {
            if (
                className.startsWith("col-")
                || className.startsWith("col-md-")
                || className.startsWith("col-lg-")
                || className.startsWith("col-xl-")
                || className.startsWith("offset-")
                || className.startsWith("order-")
                || className.startsWith("flex-grow-")
                || className === "w-100"
            ) {
                wrap.classList.remove(className);
            }
        });
        wrap.classList.add("lp-tienda-address-field", `lp-tienda-address-field--${fieldName}`, "col-12", "col-md-6");
        wrap.style.order = order;
        wrap.style.width = "";
        wrap.style.flex = "";
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
    applyAddressAdjustments(form);

    return form;
}

patch(CustomerAddress.prototype, {
    async start() {
        ensureAddressCompatibility(this.el);
        if (typeof super.start !== "function") {
            return;
        }
        try {
            const result = await super.start(...arguments);
            if (this.addressForm) {
                applyAddressAdjustments(this.addressForm);
            }
            return result;
        } catch (error) {
            const message = error?.message || "";
            if (error instanceof TypeError && message.includes("dispatchEvent")) {
                if (this.addressForm) {
                    applyAddressAdjustments(this.addressForm);
                }
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
        const result = super.setup(...arguments);
        applyAddressAdjustments(this.addressForm);
        return result;
    },

    async willStart() {
        if (!ensureAddressCompatibility(this.el)?.country_id?.value) {
            return;
        }
        const result = await super.willStart(...arguments);
        applyAddressAdjustments(this.addressForm);
        return result;
    },

    async _onChangeCountry() {
        if (!this.addressForm?.country_id?.value) {
            return;
        }
        const result = await super._onChangeCountry(...arguments);
        applyAddressAdjustments(this.addressForm);
        return result;
    },

    _markRequired(name, required) {
        if (name === "zip") {
            required = false;
        }
        const result = super._markRequired(name, required);
        if (this.addressForm) {
            applyAddressAdjustments(this.addressForm);
        }
        return result;
    },

    _showInput(name) {
        const input = this.addressForm?.[name];
        if (!input?.parentElement) {
            return;
        }
        const result = super._showInput(...arguments);
        applyAddressAdjustments(this.addressForm);
        return result;
    },

    _hideInput(name) {
        const input = this.addressForm?.[name];
        if (!input?.parentElement) {
            return;
        }
        const result = super._hideInput(...arguments);
        applyAddressAdjustments(this.addressForm);
        return result;
    },

    _getInputDiv(name) {
        return fieldWrap(this.addressForm, name);
    },

    async saveAddress() {
        if (!this.addressForm) {
            return;
        }
        applyAddressAdjustments(this.addressForm);
        return super.saveAddress(...arguments);
    },
});
