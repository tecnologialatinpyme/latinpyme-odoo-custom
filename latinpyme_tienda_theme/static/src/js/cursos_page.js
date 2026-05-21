(function () {
    "use strict";

    const COURSE_CARD = {
        sectionTitle: "cursos de auditor en sg-sst",
        title: "Protocolo Sexual Laboral",
        description: "Lo que toda empresa debe revisar antes de una sanción.",
        price: "$150.000 COP",
        link: "/shop/protocolo-de-acoso-sexual-laboral-157",
        image: "/web/image/product.template/157/image_1024",
        button: "Mas información...",
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

    function isVisibleNode(node) {
        const rect = node.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
    }

    function cardFromTitle(title) {
        let node = title.parentElement;
        while (node && node !== document.body) {
            if (
                node.querySelector("h3, h4, h5")
                && node.querySelector("img")
                && node.querySelector("a")
            ) {
                return node;
            }
            if (node.matches(".card, article, .item, [class*='col-'], .col")) {
                return node;
            }
            node = node.parentElement;
        }
        return title.parentElement;
    }

    function isFirstAuditorTitle(title) {
        const text = normalizeText(title.textContent);
        const compactText = text.replace(/\s+/g, "");
        return (
            !text.includes("integral")
            && (
                compactText.startsWith("1.cursoauditorinterno")
                || compactText.startsWith("1cursoauditorinterno")
            )
        );
    }

    function findFirstAuditorCard(section) {
        const titles = Array.from(section.querySelectorAll("h3, h4, h5"));
        const currentTitle = titles.find((title) => isFirstAuditorTitle(title));
        if (currentTitle) {
            return cardFromTitle(currentTitle);
        }
        return null;
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

    function cardLinks(card) {
        return [
            ...(card.matches("a") ? [card] : []),
            ...Array.from(card.querySelectorAll("a")),
        ];
    }

    function setCardLink(card) {
        cardLinks(card).forEach((link) => {
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

    function removeDuplicatedIds(card) {
        card.removeAttribute("id");
        card.querySelectorAll("[id]").forEach((node) => node.removeAttribute("id"));
    }

    function normalizeCourseCardHeight(card) {
        card.style.minHeight = "";
        card.style.height = "";
        card.querySelectorAll("[style]").forEach((node) => {
            node.style.minHeight = "";
            node.style.height = "";
        });
    }

    function createAcosoCourseCard(baseCard) {
        const card = baseCard.cloneNode(true);
        removeDuplicatedIds(card);
        normalizeCourseCardHeight(card);
        card.dataset.lpTiendaAcosoCourse = "1";
        card.dataset.lpTiendaAuditorCard = "1";
        card.classList.add("lp-tienda-acoso-course-card");
        setCardImage(card);
        setCardText(card);
        setCardLink(card);
        return card;
    }

    function markAuditorCards(section) {
        section.classList.add("lp-tienda-auditor-courses");
        const cards = new Set();
        section.querySelectorAll("h3, h4, h5").forEach((title) => {
            const card = cardFromTitle(title);
            if (card) {
                cards.add(card);
            }
        });
        cards.forEach((card) => {
            card.dataset.lpTiendaAuditorCard = "1";
            normalizeCourseCardHeight(card);
        });
    }

    function mountAcosoCourseCard() {
        if (!isCursosPage()) {
            return;
        }

        const headings = Array.from(document.querySelectorAll("h1, h2, h3")).filter((heading) => {
            return isVisibleNode(heading) && normalizeText(heading.textContent).includes(COURSE_CARD.sectionTitle);
        });

        headings.forEach((heading) => {
            const section = sectionFromHeading(heading);
            if (!section || section.querySelector("[data-lp-tienda-acoso-course='1']")) {
                return;
            }
            markAuditorCards(section);
            const firstAuditorCard = findFirstAuditorCard(section);
            if (!firstAuditorCard?.parentElement) {
                return;
            }
            firstAuditorCard.dataset.lpTiendaFirstAuditorCourse = "1";
            const acosoCard = createAcosoCourseCard(firstAuditorCard);
            firstAuditorCard.parentElement.insertBefore(acosoCard, firstAuditorCard);
            window.requestAnimationFrame(() => {
                firstAuditorCard.scrollIntoView({ behavior: "auto", block: "nearest", inline: "nearest" });
                acosoCard.scrollIntoView({ behavior: "auto", block: "nearest", inline: "start" });
            });
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", mountAcosoCourseCard, { once: true });
    } else {
        mountAcosoCourseCard();
    }
}());
