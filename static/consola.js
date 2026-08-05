// consola.js — CodeMirror SQL + ejecución por fetch + historial + CSV
(function () {
    "use strict";

    var textarea = document.getElementById("sql-textarea");
    if (!textarea) return;

    var HISTORY_KEY = "sql_consola_historial";
    var MAX_HISTORY = 20;

    // --- CodeMirror ---------------------------------------------------------
    var editor = window.CodeMirror.fromTextArea(textarea, {
        mode: "text/x-sql",
        theme: "dracula",
        lineNumbers: true,
        indentWithTabs: true,
        indentUnit: 2,
        smartIndent: true,
        extraKeys: {
            "Ctrl-Enter": ejecutar,
            "Cmd-Enter": ejecutar,
            "Ctrl-Space": "autocomplete",
        },
    });

    // --- Historial ----------------------------------------------------------
    function leerHistorial() {
        try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]"); }
        catch (e) { return []; }
    }
    function guardarHistorial(items) {
        try { localStorage.setItem(HISTORY_KEY, JSON.stringify(items.slice(0, MAX_HISTORY))); }
        catch (e) { /* storage disabled */ }
    }
    function añadirAlHistorial(sql) {
        var items = leerHistorial();
        var idx = items.indexOf(sql);
        if (idx !== -1) items.splice(idx, 1);
        items.unshift(sql);
        guardarHistorial(items);
        renderHistorial();
    }
    function renderHistorial() {
        var sel = document.getElementById("historial-select");
        if (!sel) return;
        var items = leerHistorial();
        var current = sel.value;
        sel.innerHTML = '<option value="">— Consultas recientes —</option>';
        items.forEach(function (sql, i) {
            var opt = document.createElement("option");
            opt.value = sql;
            var label = sql.length > 60 ? sql.slice(0, 60) + "…" : sql;
            opt.textContent = (i + 1) + ". " + label.replace(/\s+/g, " ");
            sel.appendChild(opt);
        });
        sel.value = current;
    }
    var historialSelect = document.getElementById("historial-select");
    if (historialSelect) {
        historialSelect.addEventListener("change", function () {
            if (this.value) editor.setValue(this.value);
        });
        renderHistorial();
    }
    var esquemaSelect = document.getElementById("esquema-select");

    // Cargar SQL y esquema desde URL (?sql=...&esquema=...)
    function cargarDesdeUrl() {
        var params = new URLSearchParams(window.location.search);
        var sqlParam = params.get("sql");
        var esqParam = params.get("esquema");
        if (sqlParam) {
            editor.setValue(decodeURIComponent(sqlParam));
            if (esqParam && esquemaSelect) esquemaSelect.value = esqParam;
            // limpiar la URL para no recargar siempre la misma consulta
            history.replaceState(null, "", window.location.pathname);
            ejecutar();
        }
    }

    // --- Ejecución ----------------------------------------------------------
    var form = document.getElementById("form-consola");
    var btnEjecutar = document.getElementById("btn-ejecutar");
    var btnLimpiar = document.getElementById("btn-limpiar");
    var btnCsv = document.getElementById("btn-csv");
    var statusEl = document.getElementById("consola-status");
    var resultadoArea = document.getElementById("resultado-area");

    var ultimoResultado = null;

    function setStatus(msg, tipo) {
        if (!statusEl) return;
        statusEl.textContent = msg;
        statusEl.className = "consola-status" + (tipo ? " " + tipo : "");
    }

    function renderResultado(data) {
        if (!resultadoArea) return;
        var html = "";
        if (!data.ok) {
            html = '<div class="error-box">' + escapeHtml(data.error || "Error desconocido") + "</div>";
            ultimoResultado = null;
            btnCsv.disabled = true;
        } else if (data.row_count === 0) {
            html = '<div class="resultados-meta"><h2>Resultado (0 filas)</h2></div>' +
                   '<p class="empty">La consulta no devolvio filas.</p>';
            ultimoResultado = { columns: data.columns, rows: [] };
            btnCsv.disabled = false;
        } else if (data.columns.length === 1 && data.columns[0] === "mensaje") {
            html = '<div class="info-box">' + escapeHtml(data.rows[0].mensaje) + "</div>";
            ultimoResultado = null;
            btnCsv.disabled = true;
        } else {
            html = '<div class="resultados-meta"><h2>Resultado (' + data.row_count + (data.truncated ? " (truncado a 50)" : "") + " filas)</h2>" +
                   '<span class="consola-status ok">' + (data.elapsed_ms != null ? data.elapsed_ms + " ms" : "") + "</span></div>";
            html += '<div class="tabla-resultados-wrapper"><table class="tabla-resultados"><thead><tr>';
            data.columns.forEach(function (c) { html += "<th>" + escapeHtml(c) + "</th>"; });
            html += "</tr></thead><tbody>";
            data.rows.forEach(function (fila) {
                html += "<tr>";
                data.columns.forEach(function (c) {
                    var v = fila[c];
                    if (v === null || v === undefined) html += '<td class="null-cell">NULL</td>';
                    else html += "<td>" + escapeHtml(String(v)) + "</td>";
                });
                html += "</tr>";
            });
            html += "</tbody></table></div>";
            ultimoResultado = { columns: data.columns, rows: data.rows };
            btnCsv.disabled = false;
        }
        resultadoArea.innerHTML = html;
    }

    async function ejecutar() {
        var sql = editor.getValue().trim();
        if (!sql) { setStatus("Consulta vacía", "error"); return; }
        var esquema = esquemaSelect ? esquemaSelect.value : "public";
        btnEjecutar.disabled = true;
        setStatus('<span class="spinner"></span>Ejecutando…');
        try {
            var resp = await fetch("/consulta/api", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ sql: sql, esquema: esquema }),
            });
            var data = await resp.json();
            añadirAlHistorial(sql);
            if (data.ok) {
                setStatus("OK · " + (data.elapsed_ms != null ? data.elapsed_ms + " ms" : ""), "ok");
            } else {
                setStatus("Error", "error");
            }
            renderResultado(data);
        } catch (e) {
            setStatus("Error de red", "error");
            renderResultado({ ok: false, error: "No se pudo conectar con el servidor: " + e.message });
        } finally {
            btnEjecutar.disabled = false;
        }
    }

    if (form) {
        form.addEventListener("submit", function (e) {
            // Si JS está activo, interceptar y ejecutar por fetch
            if (window.fetch) {
                e.preventDefault();
                ejecutar();
            }
            // Si fetch no existe (very old browser), dejar que el form POST clásico funcione
        });
    }
    if (btnLimpiar) {
        btnLimpiar.addEventListener("click", function () {
            editor.setValue("");
            if (resultadoArea) resultadoArea.innerHTML = "";
            setStatus("");
            btnCsv.disabled = true;
            editor.focus();
        });
    }

    // --- Exportar CSV -------------------------------------------------------
    function exportarCsv() {
        if (!ultimoResultado || !ultimoResultado.rows.length) return;
        var cols = ultimoResultado.columns;
        var rows = ultimoResultado.rows;
        var lines = [cols.map(csvCell).join(",")];
        rows.forEach(function (r) {
            lines.push(cols.map(function (c) { return csvCell(r[c]); }).join(","));
        });
        var blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8;" });
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url;
        a.download = "consulta_" + Date.now() + ".csv";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    function csvCell(v) {
        if (v === null || v === undefined) return "";
        var s = String(v);
        if (/[",\n;]/.test(s)) return '"' + s.replace(/"/g, '""') + '"';
        return s;
    }
    if (btnCsv) btnCsv.addEventListener("click", exportarCsv);

    // --- utils --------------------------------------------------------------
    function escapeHtml(s) {
        return String(s)
            .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
    }

    editor.focus();
    cargarDesdeUrl();
})();