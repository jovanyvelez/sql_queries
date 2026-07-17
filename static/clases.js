// clases.js — Sidebar sticky + scrollspy + generacion de ids en headings
(function () {
    "use strict";

    var content = document.querySelector(".clase-content");
    if (!content) return;

    // --- Slugify robusto ----------------------------------------------
    function slugify(texto) {
        return (texto || "")
            .toLowerCase()
            .replace(/<[^>]+>/g, "") // quitar tags HTML embebidos
            .replace(/[áàäâ]/g, "a").replace(/[éèëê]/g, "e")
            .replace(/[íìïî]/g, "i").replace(/[óòöô]/g, "o")
            .replace(/[úùüû]/g, "u").replace(/[ñ]/g, "n")
            .replace(/[^a-z0-9\s-]/g, "")
            .trim()
            .replace(/\s+/g, "-")
            .replace(/-+/g, "-");
    }

    // --- Asignar ids a headings ----------------------------------------
    var headings = Array.from(content.querySelectorAll("h2, h3"));
    headings.forEach(function (h) {
        if (!h.id) {
            // limpiamos contenido (code, etc.) para el slug
            var slug = slugify(h.textContent);
            h.id = slug;
        }
    });

    // --- Actualizar links del TOC existente ----------------------------
    var tocLinks = Array.from(content.querySelectorAll(".toc a"));
    tocLinks.forEach(function (a) {
        var href = a.getAttribute("href");
        if (href && href.charAt(0) === "#") {
            var slug = href.slice(1);
            // ya está apuntando a un slug; no hace falta regenerar
            void slug;
        }
    });

    // --- Construir sidebar ---------------------------------------------
    var sidebar = document.createElement("nav");
    sidebar.className = "clase-sidebar";
    sidebar.setAttribute("aria-label", "Navegación de la clase");
    var sbTitle = document.createElement("h4");
    sbTitle.textContent = "En esta clase";
    sidebar.appendChild(sbTitle);
    var sbList = document.createElement("ul");
    headings.forEach(function (h) {
        var li = document.createElement("li");
        li.className = "sidebar-item sidebar-" + h.tagName.toLowerCase();
        var a = document.createElement("a");
        a.href = "#" + h.id;
        a.textContent = h.textContent;
        a.dataset.target = h.id;
        a.addEventListener("click", function (e) {
            e.preventDefault();
            h.scrollIntoView({ behavior: "smooth", block: "start" });
            history.replaceState(null, "", "#" + h.id);
        });
        li.appendChild(a);
        sbList.appendChild(li);
    });
    sidebar.appendChild(sbList);

    // Envolver contenido + sidebar en layout de dos columnas
    var layout = document.createElement("div");
    layout.className = "clase-layout";
    content.parentNode.insertBefore(layout, content);
    layout.appendChild(sidebar);
    layout.appendChild(content);

    // --- Scrollspy con IntersectionObserver ----------------------------
    var links = Array.from(sidebar.querySelectorAll("a[data-target]"));
    var linkMap = {};
    links.forEach(function (l) { linkMap[l.dataset.target] = l; });

    var activeLink = null;
    function setActive(id) {
        if (activeLink) activeLink.classList.remove("active");
        var next = linkMap[id];
        if (next) { next.classList.add("active"); activeLink = next; }
    }

    if ("IntersectionObserver" in window) {
        var observer = new IntersectionObserver(function (entries) {
            // Elegir el heading más arriba que esté visible
            var visible = entries.filter(function (e) { return e.isIntersecting; });
            if (visible.length === 0) return;
            visible.sort(function (a, b) {
                return a.boundingClientRect.top - b.boundingClientRect.top;
            });
            setActive(visible[0].target.id);
        }, { rootMargin: "-80px 0px -70% 0px", threshold: 0 });
        headings.forEach(function (h) { observer.observe(h); });
    }

    // --- TOC existente: colapsable en mobile ---------------------------
    var toc = content.querySelector(".toc");
    if (toc) {
        // Convertir en <details> en mobile via clase
        var tocTitle = toc.querySelector("h2");
        if (tocTitle && window.matchMedia && window.matchMedia("(max-width: 1024px)").matches) {
            toc.classList.add("toc-collapsible");
            tocTitle.setAttribute("role", "button");
            tocTitle.setAttribute("tabindex", "0");
            tocTitle.addEventListener("click", function () {
                toc.classList.toggle("open");
            });
            tocTitle.addEventListener("keydown", function (e) {
                if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault(); toc.classList.toggle("open");
                }
            });
        }
    }
})();