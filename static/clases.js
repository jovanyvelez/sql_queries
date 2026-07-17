// clases.js — Sidebar sticky + scrollspy + ids + barra de progreso
(function () {
    "use strict";

    var content = document.querySelector(".clase-content");
    if (!content) return;

    var body = document.body;

    // --- Slugify -------------------------------------------------------
    function slugify(texto) {
        return (texto || "")
            .toLowerCase()
            .replace(/<[^>]+>/g, "")
            .replace(/[áàäâ]/g, "a").replace(/[éèëê]/g, "e")
            .replace(/[íìïî]/g, "i").replace(/[óòöô]/g, "o")
            .replace(/[úùüû]/g, "u").replace(/[ñ]/g, "n")
            .replace(/[^a-z0-9\s-]/g, "")
            .trim().replace(/\s+/g, "-").replace(/-+/g, "-");
    }

    // --- Asignar ids a headings ----------------------------------------
    var headings = Array.from(content.querySelectorAll("h2, h3"));
    headings.forEach(function (h) {
        if (!h.id) h.id = slugify(h.textContent);
    });

    // --- Ocultar la TOC inline duplicada (fallback sin JS) -------------
    // La plantilla incluye un <h2>Tabla de Contenidos</h2> + <ul> + <hr>
    var inlineTocTitle = Array.from(content.querySelectorAll("h2"))
        .find(function (h) { return /tabla de contenidos/i.test(h.textContent); });
    if (inlineTocTitle) {
        inlineTocTitle.classList.add("toc-inline-hidden");
        var sib = inlineTocTitle.nextElementSibling;
        while (sib && sib.tagName !== "H2") {
            sib.classList.add("toc-inline-hidden");
            sib = sib.nextElementSibling;
        }
    }

    // --- Titulo de la leccion (desde el h1) ----------------------------
    var lessonTitle = "";
    var h1 = content.querySelector("h1");
    if (h1) lessonTitle = h1.textContent.trim();

    // --- Construir sidebar anidado (h2 > h3) ---------------------------
    var sidebar = document.createElement("aside");
    sidebar.className = "clase-sidebar";
    sidebar.setAttribute("aria-label", "Navegación de la lección");

    if (lessonTitle) {
        var label = document.createElement("p");
        label.className = "clase-sidebar-label";
        label.textContent = "Lección";
        sidebar.appendChild(label);
        var titleEl = document.createElement("p");
        titleEl.className = "clase-sidebar-title";
        titleEl.textContent = lessonTitle;
        sidebar.appendChild(titleEl);
    }

    var sbList = document.createElement("ul");
    sbList.className = "clase-sidebar-nav";
    var currentH2Li = null;
    var currentSubList = null;

    headings.forEach(function (h) {
        if (h.tagName === "H2") {
            var li = document.createElement("li");
            li.className = "nav-section";
            var a = document.createElement("a");
            a.href = "#" + h.id;
            a.textContent = h.textContent;
            a.dataset.target = h.id;
            a.className = "nav-link nav-link-h2";
            bindClick(a, h);
            li.appendChild(a);
            sbList.appendChild(li);
            currentH2Li = li;
            currentSubList = null;
        } else {
            // h3: anidar bajo el último h2
            if (!currentH2Li) return;
            if (!currentSubList) {
                currentSubList = document.createElement("ul");
                currentSubList.className = "nav-sublist";
                currentH2Li.appendChild(currentSubList);
            }
            var subLi = document.createElement("li");
            var subA = document.createElement("a");
            subA.href = "#" + h.id;
            subA.textContent = h.textContent;
            subA.dataset.target = h.id;
            subA.className = "nav-link nav-link-h3";
            bindClick(subA, h);
            subLi.appendChild(subA);
            currentSubList.appendChild(subLi);
        }
    });
    sidebar.appendChild(sbList);

    function bindClick(a, h) {
        a.addEventListener("click", function (e) {
            e.preventDefault();
            h.scrollIntoView({ behavior: "smooth", block: "start" });
            history.replaceState(null, "", "#" + h.id);
        });
    }

    // --- Barra de progreso de lectura ----------------------------------
    var progress = document.createElement("div");
    progress.className = "clase-progress";
    var progressFill = document.createElement("div");
    progressFill.className = "clase-progress-fill";
    progress.appendChild(progressFill);
    body.appendChild(progress);

    // --- Montar layout --------------------------------------------------
    var layout = document.createElement("div");
    layout.className = "clase-layout";
    content.parentNode.insertBefore(layout, content);
    layout.appendChild(sidebar);
    layout.appendChild(content);
    body.classList.add("has-clase-sidebar");

    // --- Scrollspy ------------------------------------------------------
    var links = Array.from(sidebar.querySelectorAll("a[data-target]"));
    var linkMap = {};
    links.forEach(function (l) { linkMap[l.dataset.target] = l; });

    var activeLink = null;
    function setActive(id) {
        if (activeLink) activeLink.classList.remove("active");
        var next = linkMap[id];
        if (next) {
            next.classList.add("active");
            activeLink = next;
            // expandir el section padre si es h3
            var parentLi = next.closest(".nav-section");
            if (parentLi) parentLi.classList.add("open");
        }
    }

    if ("IntersectionObserver" in window) {
        var observer = new IntersectionObserver(function (entries) {
            var visible = entries.filter(function (e) { return e.isIntersecting; });
            if (visible.length === 0) return;
            visible.sort(function (a, b) {
                return a.boundingClientRect.top - b.boundingClientRect.top;
            });
            setActive(visible[0].target.id);
        }, { rootMargin: "-90px 0px -65% 0px", threshold: 0 });
        headings.forEach(function (h) { observer.observe(h); });
    }

    // --- Progreso de scroll --------------------------------------------
    function updateProgress() {
        var docEl = document.documentElement;
        var total = docEl.scrollHeight - docEl.clientHeight;
        var pct = total > 0 ? (docEl.scrollTop / total) * 100 : 0;
        progressFill.style.width = Math.min(100, Math.max(0, pct)) + "%";
    }
    window.addEventListener("scroll", updateProgress, { passive: true });
    window.addEventListener("resize", updateProgress, { passive: true });
    updateProgress();
})();