import re
from pathlib import Path

from markdown_it import MarkdownIt

MD_DIR = Path(__file__).parent.parent
TPL_DIR = Path(__file__).parent / "templates"

ARCHIVOS = {
    0: "CS50_SQL_Clase0_Consultas.md",
    1: "CS50_SQL_Clase1_Relaciones.md",
}

md = MarkdownIt("commonmark")
md.enable("table")


def convertir(clase_num: int):
    texto = (MD_DIR / ARCHIVOS[clase_num]).read_text(encoding="utf-8")
    texto = re.sub(r'!\[([^\]]*)\]\(images/([^)]+)\)', r'![\1](/static/images/\2)', texto)
    html = md.render(texto)

    html = re.sub(r'<table>', '<div class="table-wrapper"><table>', html)
    html = re.sub(r'</table>', '</table></div>', html)

    html = re.sub(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        lambda m: f'<div class="mermaid">\n{m.group(1).strip()}\n</div>',
        html,
        flags=re.DOTALL,
    )

    plantilla = (
        '{% extends "base.html" %}\n'
        '{% block title %}Clase ' + str(clase_num) + ' — CS50 SQL{% endblock %}\n'
        '{% block content %}\n'
        '<div class="clase-content">\n'
        + html +
        '\n</div>\n'
        '{% endblock %}\n'
    )

    salida = TPL_DIR / f"clase{clase_num}.html"
    salida.write_text(plantilla, encoding="utf-8")
    print(f"{salida} — {len(plantilla)} chars")


if __name__ == "__main__":
    convertir(0)
    convertir(1)
    print("Listo.")
