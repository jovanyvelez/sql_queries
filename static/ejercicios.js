// ejercicios.js — CodeMirror por ejercicio + probar + pista + estado persistido
(function () {
    "use strict";

    var ESTADO_KEY = "ejercicios_resueltos";
    var MAX_FILAS = 30;

    function leerEstado() {
        try { return JSON.parse(localStorage.getItem(ESTADO_KEY) || "{}"); }
        catch (e) { return {}; }
    }
    function guardarEstado(estado) {
        try { localStorage.setItem(ESTADO_KEY, JSON.stringify(estado)); }
        catch (e) { /* storage disabled */ }
    }

    function renderEstado() {
        var estado = leerEstado();
        document.querySelectorAll("[data-estado-id]").forEach(function (el) {
            var id = el.getAttribute("data-estado-id");
            if (estado[id]) {
                el.hidden = false;
                el.textContent = "✓ Resuelto";
                el.className = "ejercicio-estado estado-resuelto";
            } else {
                el.hidden = true;
            }
        });
    }

    var editores = {};

    function initEditores() {
        document.querySelectorAll(".solucion-textarea").forEach(function (textarea) {
            var id = textarea.getAttribute("data-ejercicio-id");
            if (editores[id]) return;
            var cm = window.CodeMirror.fromTextArea(textarea, {
                mode: "text/x-sql",
                theme: "dracula",
                lineNumbers: true,
                indentWithTabs: true,
                indentUnit: 2,
                extraKeys: {
                    "Ctrl-Enter": function () { probar(id); },
                    "Cmd-Enter": function () { probar(id); },
                    "Ctrl-Space": "autocomplete",
                },
            });
            cm.getWrapperElement().classList.add("cm-ejercicio");
            editores[id] = cm;
        });
    }

    async function probar(id) {
        var cm = editores[id];
        if (!cm) return;
        var sql = cm.getValue().trim();
        if (!sql) { mostrarFeedback(id, "warning", "Escribe una consulta primero."); return; }

        var btn = document.querySelector('.btn-probar[data-ejercicio-id="' + id + '"]');
        if (btn) { btn.disabled = true; btn.textContent = "Probando…"; }

        try {
            var resp = await fetch("/ejercicios/probar/" + encodeURIComponent(id), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ sql: sql }),
            });
            var data = await resp.json();
            renderFeedback(id, data);
            if (data.ok) {
                var estado = leerEstado();
                estado[id] = true;
                guardarEstado(estado);
                renderEstado();
            }
        } catch (e) {
            mostrarFeedback(id, "error", "No se pudo conectar: " + e.message);
        } finally {
            if (btn) { btn.disabled = false; btn.textContent = "Probar mi SQL"; }
        }
    }

    function mostrarFeedback(id, tipo, mensaje) {
        var fb = document.querySelector('[data-feedback-id="' + id + '"]');
        if (!fb) return;
        fb.hidden = false;
        var clase = tipo === "ok" ? "feedback-ok"
            : tipo === "error" ? "feedback-error" : "feedback-warning";
        fb.innerHTML = '<span class="feedback-badge ' + clase + '">'
            + (tipo === "ok" ? "✓ Correcto" : tipo === "error" ? "✗ Revisar" : "⚠ Atención")
            + "</span><div class='feedback-msg'>" + escapeHtml(mensaje) + "</div>";
    }

    function renderFeedback(id, data) {
        var fb = document.querySelector('[data-feedback-id="' + id + '"]');
        if (!fb) return;
        fb.hidden = false;
        var html = "";

        if (data.ok) {
            html += '<span class="feedback-badge feedback-ok">✓ Correcto</span>';
            html += '<div class="feedback-msg">¡Tu consulta produce el resultado esperado!</div>';
        } else {
            var titulo = data.mensaje === "wrong-columns" ? "Columnas incorrectas"
                : data.mensaje === "wrong-order" ? "Orden incorrecto"
                : data.mensaje === "wrong-rows" ? "Resultado incorrecto"
                : data.mensaje === "execution-error" ? "Error de ejecución"
                : data.mensaje === "invalid" ? "Consulta no válida"
                : "Revisar";
            html += '<span class="feedback-badge feedback-error">✗ ' + escapeHtml(titulo) + "</span>";
            // Diagnóstico principal (mensaje pedagógico en español)
            if (data.diagnostico) {
                html += '<div class="feedback-msg feedback-diag">' + escapeHtml(data.diagnostico) + "</div>";
            }
            // Error técnico bajo <details> (disponible pero no ruidoso)
            if (data.error && (data.mensaje === "execution-error" || data.mensaje === "invalid" || data.mensaje === "server-error")) {
                html += '<details class="error-tecnico"><summary>Ver error técnico</summary><pre class="error-tecnico-pre">' + escapeHtml(data.error) + "</pre></details>";
            }
            // Comparación lado a lado (solo si hay columnas que comparar)
            if (data.columnas_esperadas && data.columnas_obtenidas
                && data.columnas_esperadas.length > 0) {
                html += '<div class="comparacion-tablas">';
                html += '<div class="comparacion-col"><h4>Esperado</h4>' + tablaHtml(data.columnas_esperadas, data.filas_esperadas) + "</div>";
                html += '<div class="comparacion-col"><h4>Tu resultado</h4>' + tablaHtml(data.columnas_obtenidas, data.filas_obtenidas) + "</div>";
                html += "</div>";
            }
        }
        fb.innerHTML = html;
    }

    function tablaHtml(columnas, filas) {
        if (!columnas || columnas.length === 0) return '<div class="feedback-msg">Sin filas</div>';
        var html = '<div class="comparacion-wrapper"><table class="tabla-comparacion"><thead><tr>';
        columnas.forEach(function (c) { html += "<th>" + escapeHtml(c) + "</th>"; });
        html += "</tr></thead><tbody>";
        var n = Math.min(filas.length, MAX_FILAS);
        for (var i = 0; i < n; i++) {
            html += "<tr>";
            columnas.forEach(function (c) {
                var v = filas[i][c];
                if (v === null || v === undefined) html += '<td style="color:#6e7681;font-style:italic">NULL</td>';
                else html += "<td>" + escapeHtml(String(v)) + "</td>";
            });
            html += "</tr>";
        }
        html += "</tbody></table></div>";
        if (filas.length > MAX_FILAS) {
            html += '<div class="feedback-msg">Mostrando ' + MAX_FILAS + ' de ' + filas.length + " filas.</div>";
        }
        return html;
    }

    function escapeHtml(s) {
        return String(s)
            .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
    }

    function initBotones() {
        document.querySelectorAll(".btn-probar").forEach(function (btn) {
            btn.addEventListener("click", function () {
                probar(btn.getAttribute("data-ejercicio-id"));
            });
        });
        document.querySelectorAll(".btn-pista").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var id = btn.getAttribute("data-ejercicio-id");
                var pista = document.querySelector('[data-pista-id="' + id + '"]');
                if (!pista) return;
                pista.hidden = !pista.hidden;
                btn.textContent = pista.hidden ? "Ver pista" : "Ocultar pista";
            });
        });
    }

    // init
    initEditores();
    initBotones();
    renderEstado();
})();