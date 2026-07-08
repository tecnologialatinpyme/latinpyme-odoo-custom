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
    const existing = form.elements[name];
    if (existing) {
        if (value !== "" && !existing.value) {
            existing.value = value;
        }
        return existing;
    }
    const input = document.createElement("input");
    input.type = "hidden";
    input.name = name;
    input.id = `lp_tienda_${name}`;
    input.value = value;
    hiddenWrap(form, name).appendChild(input);
    return input;
}

function getControlValue(form, name) {
    const control = form?.elements?.[name];
    return typeof control?.value === "string" ? control.value.trim() : "";
}

function inferNitIdentificationTypeValue(form) {
    const vat = getControlValue(form, "vat");
    const preferredNitValue = (() => {
        const select = form?.querySelector?.('select[name="l10n_latam_identification_type_id"]');
        if (select) {
            const nitOption = Array.from(select.options || []).find((option) => {
                return normalizeText(option.textContent).includes("nit");
            });
            if (nitOption?.value) {
                return nitOption.value;
            }
        }

        const anySelectWithNit = Array.from(form?.querySelectorAll?.("select") || []).find((selectNode) => {
            return Array.from(selectNode.options || []).some((option) => normalizeText(option.textContent).includes("nit"));
        });
        if (anySelectWithNit) {
            const nitOption = Array.from(anySelectWithNit.options || []).find((option) => {
                return normalizeText(option.textContent).includes("nit");
            });
            return nitOption?.value || anySelectWithNit.value || "";
        }

        return "";
    })();
    if (vat && preferredNitValue) {
        return preferredNitValue;
    }

    const direct = getControlValue(form, "l10n_latam_identification_type_id");
    if (direct) {
        return direct;
    }

    return "";
}

function syncFiscalFields(form, { finalizeVat = true } = {}) {
    if (!form) {
        return;
    }

    const colombiaSelected = isColombiaSelected(form);
    const vatInput = form.elements.vat;
    if (vatInput && typeof vatInput.value === "string") {
        const digitsOnly = vatInput.value.replace(/[^\d-]/g, "");
        if (digitsOnly !== vatInput.value) {
            const caret = vatInput.selectionStart;
            vatInput.value = digitsOnly;
            if (typeof caret === "number" && vatInput.setSelectionRange) {
                const newPos = Math.max(0, caret - 1);
                vatInput.setSelectionRange(newPos, newPos);
            }
        }
    }
    const vat = getControlValue(form, "vat");
    if (vat && colombiaSelected && finalizeVat) {
        const normalizedVat = normalizeColombianNitValue(vat);
        if (vatInput && vatInput.value !== normalizedVat) {
            vatInput.value = normalizedVat;
        }
        ensureHiddenInput(form, "vat", normalizedVat);
    } else if (vat) {
        ensureHiddenInput(form, "vat", vat);
    }

    const companyTypeTouchedByUser = form.dataset.lpTiendaCompanyTypeTouched === "1";
    const companyType = companyTypeTouchedByUser
        ? getControlValue(form, "company_type")
        : (vat ? "company" : getControlValue(form, "company_type"));
    if (companyType) {
        const companyTypeControl = form.querySelector?.('select[name="company_type"]');
        if (companyTypeControl && companyTypeControl.value !== companyType) {
            companyTypeControl.value = companyType;
            companyTypeControl.dispatchEvent(new Event("change", { bubbles: true }));
        }
        ensureHiddenInput(form, "company_type", companyType);
    }

    const nitType = inferNitIdentificationTypeValue(form);
    if (nitType) {
        const nitTypeControl = form.querySelector?.('select[name="l10n_latam_identification_type_id"]');
        if (nitTypeControl && nitTypeControl.value !== nitType) {
            nitTypeControl.value = nitType;
            nitTypeControl.dispatchEvent(new Event("change", { bubbles: true }));
        }
        ensureHiddenInput(form, "l10n_latam_identification_type_id", nitType);
    } else if (vat && colombiaSelected) {
        const nitValue = setSelectValueByText(form, "l10n_latam_identification_type_id", "NIT");
        if (nitValue) {
            ensureHiddenInput(form, "l10n_latam_identification_type_id", nitValue);
        }
    }
}

function bindFiscalFieldSync(form) {
    if (!form || form.dataset.lpTiendaFiscalSyncBound === "1") {
        return;
    }

    const sync = (event) => {
        if (event?.isTrusted && event.target?.name === "company_type") {
            form.dataset.lpTiendaCompanyTypeTouched = "1";
        }
        const finalizeVat = !event || event.type !== "input";
        syncFiscalFields(form, { finalizeVat });
    };
    ["input", "change", "submit"].forEach((eventName) => {
        form.addEventListener(eventName, sync, true);
    });

    const vat = form.elements.vat;
    const companyType = form.elements.company_type;
    const idType = form.elements.l10n_latam_identification_type_id;
    [vat, companyType, idType].forEach((field) => {
        if (!field?.addEventListener) {
            return;
        }
        field.addEventListener("input", sync, true);
        field.addEventListener("change", sync, true);
        field.addEventListener("blur", sync, true);
    });

    form.dataset.lpTiendaFiscalSyncBound = "1";
    sync();
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

function resolveNamedField(form, name) {
    const field = form.elements[name];
    if (!field || field.nodeType || typeof field.length !== "number") {
        // Single element (or nothing): nodeType is only set on real DOM nodes.
        return field || null;
    }
    // RadioNodeList: multiple elements share this name (e.g. a leftover hidden
    // fallback plus the real field Odoo swapped in). Prefer the visible one.
    const candidates = Array.from(field);
    return candidates.find((el) => el.offsetParent !== null && !el.hidden) || candidates[0] || null;
}

function fieldWrap(form, name) {
    if (!form?.elements) {
        return null;
    }
    const field = resolveNamedField(form, name);
    if (!field?.closest) {
        return field?.parentElement || null;
    }
    const compactName = name.replace(/_id$/, "");
    return field.closest(
        `.div_${name}, .div_${compactName}, [data-name="${name}"], [data-name="${compactName}"], .lp-tienda-address-field, .mb-3, .form-group`
    ) || field.parentElement || null;
}

function isVisibleAddressWrap(wrap) {
    return Boolean(
        wrap
        && !wrap.hidden
        && !wrap.dataset.lpTiendaAddressGuard
        && wrap.offsetParent !== null
    );
}

function labelWrapByText(form, expectedText) {
    const expected = normalizeText(expectedText);
    const label = Array.from(form.querySelectorAll("label")).find((node) => {
        const text = normalizeText(node.textContent);
        return text.includes(expected);
    });
    return label ? wrapperForControl(label) : null;
}

function addressFieldWrap(form, name) {
    const aliases = {
        country_id: ["country_id"],
        state_id: ["state_id"],
        city: ["city", "city_id"],
        zip: ["zip"],
    };
    for (const alias of aliases[name] || [name]) {
        const wrap = fieldWrap(form, alias);
        if (isVisibleAddressWrap(wrap)) {
            return wrap;
        }
    }
    const labelText = {
        country_id: "pais",
        state_id: "departamento",
        city: "ciudad",
        zip: "codigo postal",
    }[name];
    const wrap = labelText ? labelWrapByText(form, labelText) : null;
    return isVisibleAddressWrap(wrap) ? wrap : null;
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

const COLOMBIA_NIT_WEIGHTS = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71];

function isColombiaSelected(form) {
    const country = form?.elements?.country_id;
    const selectedText = country?.selectedOptions?.[0]?.textContent || "";
    return normalizeText(selectedText).includes("colombia");
}

function computeColombianNitCheckDigit(baseDigits) {
    const digits = String(baseDigits || "").replace(/\D/g, "");
    if (!digits) {
        return "";
    }
    const total = digits
        .split("")
        .reverse()
        .reduce((sum, digit, index) => {
            const weight = COLOMBIA_NIT_WEIGHTS[index];
            return sum + (weight ? Number(digit) * weight : 0);
        }, 0);
    const remainder = total % 11;
    return String(remainder > 1 ? 11 - remainder : remainder);
}

function normalizeColombianNitValue(value = "") {
    const raw = String(value || "").trim().replace(/\s+/g, "").replace(/[.]/g, "");
    const match = raw.match(/^(\d+)(?:-(\d))?$/);
    if (!match) {
        return raw;
    }
    const baseDigits = match[1];
    const expectedDigit = computeColombianNitCheckDigit(baseDigits);
    return expectedDigit ? `${baseDigits}-${expectedDigit}` : raw;
}

function setSelectValueByText(form, name, expectedText) {
    const select = form?.querySelector?.(`select[name="${name}"]`);
    if (!select) {
        return "";
    }
    const expected = normalizeText(expectedText);
    const option = Array.from(select.options || []).find((opt) => {
        return normalizeText(opt.textContent).includes(expected);
    });
    if (option && select.value !== option.value) {
        select.value = option.value;
        select.dispatchEvent(new Event("change", { bubbles: true }));
    }
    return select.value || option?.value || "";
}

function isObligationsField(value = "") {
    const text = normalizeText(value);
    return (
        (text.includes("oblig") && text.includes("respons"))
        || (text.includes("l10n_co") && (text.includes("oblig") || text.includes("respons") || text.includes("regimen")))
        || text.includes("fiscal_respons")
        || text.includes("responsibility_ids")
        || text.includes("obligation_ids")
        || (text.includes("regimen") && text.includes("fiscal"))
        || text.includes("fiscal_regimen")
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

function applyHiddenFiscalDefault(field) {
    if (field.tagName === "SELECT") {
        const target = Array.from(field.options || []).find((option) => {
            return normalizeText(option.textContent).includes("no aplica");
        });
        if (target && field.value !== target.value) {
            field.value = target.value;
            field.dispatchEvent(new Event("change", { bubbles: true }));
        }
        return;
    }
    if ((field.tagName === "INPUT" || field.tagName === "TEXTAREA") && !field.value) {
        field.value = "R-99-PN";
        field.dispatchEvent(new Event("input", { bubbles: true }));
        field.dispatchEvent(new Event("change", { bubbles: true }));
    }
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
            field.removeAttribute("required");
            field.classList.remove("is-invalid");
            applyHiddenFiscalDefault(field);
        });
    });
}

function applyAddressAdjustments(form) {
    if (!form) {
        return;
    }
    syncFiscalFields(form);
    makeZipOptional(form);
    hideObligationsControl(form);
    arrangeAddressFields(form);
}

function arrangeAddressFields(form) {
    insertAddressSectionHeadings(form);
    normalizeAddressLocationGrid(form);
    setAddressFieldLayout(form);
}

function ensureSectionHeading(form, beforeFieldName, headingId, label) {
    const wrap = fieldWrap(form, beforeFieldName);
    if (!isVisibleAddressWrap(wrap) || !wrap.parentElement) {
        return;
    }
    if (form.querySelector(`[data-lp-tienda-heading="${headingId}"]`)) {
        return;
    }
    const heading = document.createElement("div");
    heading.className = "lp-tienda-address-section-heading w-100";
    heading.dataset.lpTiendaHeading = headingId;
    heading.textContent = label;
    wrap.insertAdjacentElement("beforebegin", heading);
}

function insertAddressSectionHeadings(form) {
    ensureSectionHeading(form, "company_type", "fiscal", "Datos de facturación");
    ensureSectionHeading(form, "street", "address", "Dirección");
}

function normalizeAddressLocationGrid(form) {
    const locationFields = [
        ["country_id", addressFieldWrap(form, "country_id")],
        ["state_id", addressFieldWrap(form, "state_id")],
        ["city", addressFieldWrap(form, "city")],
    ].filter(([, wrap]) => wrap);

    if (locationFields.length) {
        const grid = ensureAddressGroupRow(
            form,
            "lp-tienda-address-location-grid",
            "lpTiendaAddressLocationGrid",
            locationFields[0][1],
        );
        locationFields.forEach(([fieldName, wrap]) => {
            const previousParent = wrap.parentElement;
            wrap.dataset.lpTiendaAddressField = fieldName;
            if (previousParent !== grid) {
                grid.appendChild(wrap);
                collapseEmptyAddressRow(previousParent);
            }
        });
    }

    const streetWrap = addressFieldWrap(form, "street");
    const zipWrap = addressFieldWrap(form, "zip");
    if (streetWrap && zipWrap) {
        const streetRow = ensureAddressGroupRow(
            form,
            "lp-tienda-address-street-row",
            "lpTiendaAddressStreetRow",
            streetWrap,
        );
        [["street", streetWrap], ["zip", zipWrap]].forEach(([fieldName, wrap]) => {
            const previousParent = wrap.parentElement;
            wrap.dataset.lpTiendaAddressField = fieldName;
            if (previousParent !== streetRow) {
                streetRow.appendChild(wrap);
                collapseEmptyAddressRow(previousParent);
            }
        });
    }
}

function ensureAddressGroupRow(form, className, datasetKey, referenceWrap) {
    const existing = form.querySelector(`.${className}`);
    if (existing) {
        existing.classList.add("lp-tienda-address-fields", "row");
        return existing;
    }

    const row = document.createElement("div");
    row.className = `${className} lp-tienda-address-fields row`;
    row.dataset[datasetKey] = "1";

    if (referenceWrap?.parentElement) {
        referenceWrap.insertAdjacentElement("beforebegin", row);
    } else {
        form.appendChild(row);
    }
    return row;
}

function collapseEmptyAddressRow(row) {
    if (!row || row.dataset.lpTiendaAddressLocationGrid || row.dataset.lpTiendaAddressStreetRow) {
        return;
    }
    const hasVisibleChildren = Array.from(row.children || []).some((child) => {
        return !child.hidden && child.offsetParent !== null && !child.dataset.lpTiendaAddressGuard;
    });
    if (!hasVisibleChildren && row.classList?.contains("row")) {
        row.hidden = true;
    }
}

function stripGridClasses(wrap) {
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
}

function setAddressFieldLayout(form) {
    [
        ["country_id", "1", "col-md-6"],
        ["state_id", "2", "col-md-6"],
        ["city", "3", "col-md-6"],
    ].forEach(([fieldName, order, widthClass]) => {
        const wrap = addressFieldWrap(form, fieldName);
        if (!wrap) {
            return;
        }
        stripGridClasses(wrap);
        wrap.classList.add("lp-tienda-address-field", `lp-tienda-address-field--${fieldName}`, "col-12", widthClass);
        wrap.style.order = order;
        wrap.style.width = "";
        wrap.style.flex = "";
    });

    [
        ["street", "1", "col-md-8"],
        ["zip", "2", "col-md-4"],
    ].forEach(([fieldName, order, widthClass]) => {
        const wrap = addressFieldWrap(form, fieldName);
        if (!wrap) {
            return;
        }
        stripGridClasses(wrap);
        wrap.classList.add("lp-tienda-address-field", `lp-tienda-address-field--${fieldName}`, "col-12", widthClass);
        wrap.style.order = order;
        wrap.style.width = "";
        wrap.style.flex = "";
    });
}

function bindLocationObserver(form) {
    if (!form || form.dataset.lpTiendaLocationObserverBound === "1") {
        return;
    }

    let debounceId = null;
    const observer = new MutationObserver((mutations) => {
        const isOwnMutation = mutations.every((mutation) => {
            return mutation.target?.dataset?.lpTiendaAddressLocationGrid === "1";
        });
        if (isOwnMutation) {
            return;
        }
        if (debounceId) {
            clearTimeout(debounceId);
        }
        debounceId = setTimeout(() => {
            arrangeAddressFields(form);
        }, 120);
    });
    observer.observe(form, { childList: true, subtree: true });

    form.dataset.lpTiendaLocationObserverBound = "1";
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
    ensureHiddenInput(form, "vat");
    ensureHiddenInput(form, "company_type");
    ensureHiddenInput(form, "l10n_latam_identification_type_id");
    ensureHiddenSelect(form, "country_id");
    ensureHiddenSelect(form, "state_id");
    applyAddressAdjustments(form);
    bindFiscalFieldSync(form);
    bindLocationObserver(form);

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
