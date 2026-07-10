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
        // Once the customer finishes typing (blur/change), place the dash
        // before the last digit if they didn't type one themselves. This is
        // pure formatting: the digit itself is never changed, only where the
        // dash goes - only applies for Colombia, where a NIT check digit is
        // expected in that position.
        if (finalizeVat && colombiaSelected) {
            const plainDigits = vatInput.value.match(/^(\d{2,})$/);
            if (plainDigits) {
                vatInput.value = `${plainDigits[1].slice(0, -1)}-${plainDigits[1].slice(-1)}`;
            }
        }
    }
    const vat = getControlValue(form, "vat");
    if (vat) {
        ensureHiddenInput(form, "vat", vat);
    }
    if (colombiaSelected) {
        warnOnColombianNitMismatch(form, vat);
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

    // Tipo Cliente drives the identification type: Independiente (person)
    // defaults to Cedula de ciudadania and Empresa defaults to NIT - but only
    // until the customer manually picks a different option themselves; from
    // then on their choice is respected until Tipo Cliente changes again.
    const idTypeTouchedByUser = form.dataset.lpTiendaIdTypeTouched === "1";
    if (idTypeTouchedByUser) {
        return;
    }

    if (companyType === "person") {
        const cedulaValue = setSelectValueByText(form, "l10n_latam_identification_type_id", "ciudadania");
        if (cedulaValue) {
            ensureHiddenInput(form, "l10n_latam_identification_type_id", cedulaValue);
            return;
        }
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
            // Switching Tipo Cliente should re-apply its sensible default
            // (Cedula for Independiente, NIT for Empresa) rather than keep
            // whatever identification type the customer had picked before.
            delete form.dataset.lpTiendaIdTypeTouched;
        }
        if (event?.isTrusted && event.target?.name === "l10n_latam_identification_type_id") {
            form.dataset.lpTiendaIdTypeTouched = "1";
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

// Odoo already shows a single "*" for required fields via pure CSS
// (`.col-form-label:not(.label-optional)::after`). Some l10n-specific labels
// (e.g. Colombia's "Tipo Cliente", "NIT") additionally bake a literal "*"
// into their text, producing a visible "* *". Strip any literal asterisk so
// the native CSS rule stays the single source of truth for the indicator.
function stripLiteralAsterisk(label) {
    if (!label) {
        return;
    }
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

function stripLiteralLabelAsterisks(form) {
    form.querySelectorAll(".col-form-label, label").forEach(stripLiteralAsterisk);
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
    stripLiteralAsterisk(label);
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

// The NIT stays fully manual: we never rewrite what the customer types. We
// only show a non-blocking, informational note when the check digit they
// typed doesn't match the DIAN formula, in case it helps them catch a typo.
function warnOnColombianNitMismatch(form, vat) {
    const wrap = fieldWrap(form, "vat");
    let note = wrap?.querySelector('[data-lp-tienda-nit-check="1"]');

    const raw = String(vat || "").trim().replace(/\s+/g, "").replace(/[.]/g, "");
    const match = raw.match(/^(\d+)-(\d)$/);
    if (!match) {
        note?.remove();
        return;
    }

    const [, baseDigits, typedDigit] = match;
    const expectedDigit = computeColombianNitCheckDigit(baseDigits);
    if (!expectedDigit || typedDigit === expectedDigit) {
        note?.remove();
        return;
    }

    if (!note && wrap) {
        note = document.createElement("small");
        note.dataset.lpTiendaNitCheck = "1";
        note.className = "lp-tienda-nit-check-note form-text text-danger d-block mt-1";
        wrap.appendChild(note);
    }
    if (note) {
        note.textContent = `Revisa el NIT: según la fórmula del DIAN, el dígito de verificación esperado es ${expectedDigit}.`;
    }
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

function isRegimeField(value = "") {
    const text = normalizeText(value);
    return (
        (text.includes("regimen") && text.includes("fiscal"))
        || text.includes("fiscal_regimen")
        || (text.includes("l10n_co") && text.includes("regimen"))
    );
}

function isObligationsField(value = "") {
    const text = normalizeText(value);
    return (
        isRegimeField(value)
        || (text.includes("oblig") && text.includes("respons"))
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
    if (field.tagName === "INPUT" || field.tagName === "TEXTAREA") {
        if (!field.value) {
            field.value = "R-99-PN";
            field.dispatchEvent(new Event("input", { bubbles: true }));
            field.dispatchEvent(new Event("change", { bubbles: true }));
        }
        if (field.tagName === "INPUT" && field.type !== "hidden") {
            field.setAttribute("autocomplete", "off");
            field.type = "hidden";
        }
    }
}

function collectFieldWrappers(form, matcher) {
    const wrappers = new Set();
    form.querySelectorAll("input, select, textarea").forEach((field) => {
        const wrap = wrapperForControl(field);
        const label = field.id ? wrap?.querySelector(`label[for="${field.id}"]`) : null;
        const dataName = field.closest("[data-name]")?.dataset?.name || "";
        if (matcher(field.name) || matcher(field.id) || matcher(dataName) || matcher(label?.textContent)) {
            wrappers.add(wrap);
        }
    });
    form.querySelectorAll("label").forEach((label) => {
        if (matcher(label.textContent)) {
            wrappers.add(wrapperForControl(label));
        }
    });
    return wrappers;
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

    // Both Regimen fiscal (plain <select>) and Obligaciones y responsabilidades
    // (Odoo SelectMenu/Owl widget, which Odoo itself already renders on top of a
    // hidden native <select> carrying the real field name) are safe to hide via
    // CSS: we only ever set `.value` + dispatch `change` on the underlying native
    // control, we never simulate clicks inside the SelectMenu popover, so its
    // positioning logic is never triggered. The control is never `disabled`, so
    // it keeps submitting normally with the form.
    function hideFieldWrap(wrap, applyDefault) {
        if (!wrap || wrap.dataset.lpTiendaAddressGuard) {
            return;
        }
        wrap.querySelectorAll("input, select, textarea").forEach(applyDefault);
        wrap.hidden = true;
        wrap.style.display = "none";
        wrap.classList.add("d-none", "lp-tienda-address-field--hidden-obligations");
        wrap.querySelectorAll("input, select, textarea").forEach((field) => {
            removeRequiredField(form, field.name);
            field.required = false;
            field.removeAttribute("required");
            field.classList.remove("is-invalid");
        });
    }

    // Regimen fiscal: default to "No Aplica".
    collectFieldWrappers(form, isRegimeField).forEach((wrap) => {
        hideFieldWrap(wrap, (field) => applyHiddenFiscalDefault(field));
    });

    // Obligaciones y responsabilidades: default to "R-99-PN" (No aplica - Otros).
    collectFieldWrappers(form, (value) => isObligationsField(value) && !isRegimeField(value)).forEach((wrap) => {
        hideFieldWrap(wrap, (field) => {
            if (field.value) {
                return;
            }
            if (field.tagName === "SELECT") {
                const target = Array.from(field.options || []).find((option) => {
                    return normalizeText(option.textContent).includes("r-99-pn");
                });
                if (target) {
                    field.value = target.value;
                    field.dispatchEvent(new Event("change", { bubbles: true }));
                }
                return;
            }
            if (field.tagName === "INPUT" || field.tagName === "TEXTAREA") {
                field.value = "R-99-PN";
                field.dispatchEvent(new Event("input", { bubbles: true }));
                field.dispatchEvent(new Event("change", { bubbles: true }));
            }
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
    normalizeAddressContactGrid(form);
    normalizeAddressLocationGrid(form);
    normalizeAddressFiscalGrid(form);
    normalizeFullWidthField(form, "company_type");
    stripLiteralLabelAsterisks(form);
}

// Tipo Cliente drives which fiscal fields appear below it; keep it spanning
// the full form width instead of the native half-width column.
function normalizeFullWidthField(form, fieldName) {
    const wrap = addressFieldWrap(form, fieldName);
    if (!isVisibleAddressWrap(wrap)) {
        return;
    }
    stripGridClasses(wrap);
    wrap.classList.add("lp-tienda-address-field", "lp-tienda-address-field--full");
}

function normalizeFieldGroup(form, groupFields, className, datasetKey) {
    const fields = groupFields
        .map((name) => [name, addressFieldWrap(form, name)])
        .filter(([, wrap]) => isVisibleAddressWrap(wrap));

    if (!fields.length) {
        return;
    }

    const grid = ensureAddressGroupRow(form, className, datasetKey, fields[0][1]);
    fields.forEach(([fieldName, wrap]) => {
        const previousParent = wrap.parentElement;
        wrap.dataset.lpTiendaAddressField = fieldName;
        stripGridClasses(wrap);
        wrap.classList.add("lp-tienda-address-field", `lp-tienda-address-field--${fieldName}`);
        if (previousParent !== grid) {
            grid.appendChild(wrap);
            collapseEmptyAddressRow(previousParent);
        }
    });
}

// Name/email/phone are the native contact fields Odoo already shows first;
// pairing email+phone keeps them on the same flex grid as every other row
// below so every row's right edge lines up consistently.
function normalizeAddressContactGrid(form) {
    normalizeFieldGroup(form, ["email", "phone"], "lp-tienda-address-contact-grid", "lpTiendaAddressContactGrid");
}

// Company name / identification type / NIT flow as a single distributed
// row instead of a rigid 2-then-1 split: each field grows to fill the row
// (a lone field stretches full width instead of leaving an empty gap), and
// it self-adjusts automatically whichever fields Tipo Cliente shows or hides.
function normalizeAddressFiscalGrid(form) {
    normalizeFieldGroup(
        form,
        ["company_name", "l10n_latam_identification_type_id", "vat"],
        "lp-tienda-address-fiscal-grid",
        "lpTiendaAddressFiscalGrid",
    );
}

function normalizeAddressLocationGrid(form) {
    normalizeFieldGroup(
        form,
        ["country_id", "state_id", "city"],
        "lp-tienda-address-location-grid",
        "lpTiendaAddressLocationGrid",
    );
    normalizeFieldGroup(form, ["street", "zip"], "lp-tienda-address-street-row", "lpTiendaAddressStreetRow");
}

function ensureAddressGroupRow(form, className, datasetKey, referenceWrap) {
    const existing = form.querySelector(`.${className}`);
    if (existing) {
        existing.classList.add("lp-tienda-address-fields");
        return existing;
    }

    const row = document.createElement("div");
    row.className = `${className} lp-tienda-address-fields`;
    row.dataset[datasetKey] = "1";

    if (referenceWrap?.parentElement) {
        referenceWrap.insertAdjacentElement("beforebegin", row);
    } else {
        form.appendChild(row);
    }
    return row;
}

function collapseEmptyAddressRow(row) {
    if (
        !row
        || row.dataset.lpTiendaAddressLocationGrid
        || row.dataset.lpTiendaAddressStreetRow
        || row.dataset.lpTiendaAddressFiscalGrid
    ) {
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
