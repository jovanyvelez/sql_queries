// base.js — Prism highlight + botón copiar en snippets + botón volver arriba
(function () {
    "use strict";

    // --- Botón volver arriba ------------------------------------------------
    var topBtn = document.getElementById("back-to-top");
    if (topBtn) {
        window.addEventListener("scroll", function () {
            if (window.scrollY > 400) {
                topBtn.classList.add("visible");
            } else {
                topBtn.classList.remove("visible");
            }
        }, { passive: true });
        topBtn.addEventListener("click", function () {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    // --- Botón copiar en bloques <pre> --------------------------------------
    function añadirBotonCopiar(pre) {
        // Evitar duplicados
        if (pre.parentElement.querySelector(".btn-copiar-snippet")) return;
        var wrapper = document.createElement("div");
        wrapper.className = "snippet-wrapper";
        pre.parentNode.insertBefore(wrapper, pre);
        wrapper.appendChild(pre);

        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "btn-copiar-snippet";
        btn.setAttribute("aria-label", "Copiar código");
        btn.textContent = "Copiar";
        btn.addEventListener("click", function () {
            var code = pre.querySelector("code");
            var texto = code ? code.textContent : pre.textContent;
            navigator.clipboard.writeText(texto).then(function () {
                btn.textContent = "Copiado ✓";
                btn.classList.add("copiado");
                setTimeout(function () {
                    btn.textContent = "Copiar";
                    btn.classList.remove("copiado");
                }, 1500);
            }).catch(function () {
                btn.textContent = "Error";
                setTimeout(function () { btn.textContent = "Copiar"; }, 1500);
            });
        });
        wrapper.appendChild(btn);
    }

    document.querySelectorAll("pre code").forEach(function (codeEl) {
        // Forzar class language-sql si no tiene lenguaje
        if (!/language-/.test(codeEl.className)) {
            codeEl.classList.add("language-sql");
        }
        añadirBotonCopiar(codeEl.parentElement);
    });

    // --- Prism: highlight autodetect (defensive) -----------------------------
    if (window.Prism && typeof window.Prism.highlightAll === "function") {
        window.Prism.highlightAll();
    }

    // --- Dropdowns del nav en móvil (toggle al click) -----------------------
    document.querySelectorAll(".nav-dropdown-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
            // Solo activar el toggle en móvil (cuando el hamburger es visible)
            var hamburger = document.querySelector(".hamburger");
            if (hamburger && getComputedStyle(hamburger).display !== "none") {
                var dd = btn.closest(".nav-dropdown");
                if (dd) dd.classList.toggle("open");
            }
        });
    });
})();