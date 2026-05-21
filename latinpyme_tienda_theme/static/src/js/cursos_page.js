(function () {
    "use strict";

    const COURSE_CARD = {
        sectionTitle: "cursos de auditor en sg-sst",
        title: "Charla sin costo - Acoso sexual laboral",
        description: "Lo que toda empresa debe revisar antes de una sanción.",
        price: "Sin costo",
        link: "/shop/protocolo-de-acoso-sexual-laboral-157",
        image: "/web/image/product.template/157/image_1024",
        button: "Inscribirme sin costo",
    };

    function normalizeText(value = "") {
        return value
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .replace(/\s+/g, " ")
            .trim();
    }

    function isCursosPage() {
        return window.location.pathname.replace(/\/+$/, "") === "/cursos";
    }

    function sectionFromHeading(heading) {
        return heading.closest("section")
            || heading.closest(".container")
            || heading.parentElement;
    }

    function cardFromTitle(title) {
        return title.closest(".card, article, [class*='card'], [class*='col-'], .col, .item")
            || title.parentElement;
    }

    function findFirstAuditorCard(section) {
        const titles = Array.from(section.querySelectorAll("h3, h4, h5"));
        const currentTitle = titles.find((title) => normalizeText(title.textContent).includes("curso auditor interno"));
        if (currentTitle) {
            return cardFromTitle(currentTitle);
        }
        return Array.from(section.querySelectorAll(".card, article, [class*='card']")).find((card) => {
            return card.querySelector("h3, h4, h5, a, img");
        }) || null;
    }

    function setCardImage(card) {
        const image = card.querySelector("img");
        if (!image) {
            return;
        }
        image.src = COURSE_CARD.image;
        image.alt = COURSE_CARD.title;
        image.loading = "lazy";
    }

    function setCardLink(card) {
        card.querySelectorAll("a").forEach((link) => {
            link.href = COURSE_CARD.link;
            link.setAttribute("aria-label", COURSE_CARD.title);
            const text = normalizeText(link.textContent);
            if (
                link.classList.contains("btn")
                || text.includes("informacion")
                || text.includes("comprar")
                || text.includes("inscrib")
            ) {
                link.textContent = COURSE_CARD.button;
            }
        });
    }

    function setCardText(card) {
        const title = card.querySelector("h3, h4, h5");
        if (title) {
            title.textContent = COURSE_CARD.title;
        }

        const paragraphs = Array.from(card.querySelectorAll("p"));
        const description = paragraphs.find((paragraph) => !paragraph.textContent.includes("$"));
        if (description) {
            description.textContent = COURSE_CARD.description;
        }

        const price = paragraphs.find((paragraph) => paragraph.textContent.includes("$"))
            || Array.from(card.querySelectorAll("span, strong, div")).find((node) => node.textContent.trim().startsWith("$"));
        if (price) {
            price.textContent = COURSE_CARD.price;
        }
    }

    function mountAcosoCourseCard() {
        if (!isCursosPage()) {
            return;
        }

        const headings = Array.from(document.querySelectorAll("h1, h2, h3")).filter((heading) => {
            return normalizeText(heading.textContent).includes(COURSE_CARD.sectionTitle);
        });

        headings.forEach((heading) => {
            const section = sectionFromHeading(heading);
            const card = section ? findFirstAuditorCard(section) : null;
            if (!card || card.dataset.lpTiendaAcosoCourse === "1") {
                return;
            }
            card.dataset.lpTiendaAcosoCourse = "1";
            card.classList.add("lp-tienda-acoso-course-card");
            setCardImage(card);
            setCardText(card);
            setCardLink(card);
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", mountAcosoCourseCard, { once: true });
    } else {
        mountAcosoCourseCard();
    }
}());
