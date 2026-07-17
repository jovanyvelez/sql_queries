import re
from pathlib import Path

from markdown_it import MarkdownIt

MD_DIR = Path(__file__).parent.parent
TPL_DIR = Path(__file__).parent / "templates"
CONTENT_DIR = TPL_DIR / "content"

ARCHIVOS = {
    0: ("CS50_SQL_Clase0_Consultas.md", "consultas"),
    1: ("CS50_SQL_Clase1_Relaciones.md", "relaciones"),
}

md = MarkdownIt("commonmark")
md.enable("table")


def convertir(clase_num: int):
    nombre_md, curso = ARCHIVOS[clase_num]
    texto = (MD_DIR / nombre_md).read_text(encoding="utf-8")
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

    # Parcial de contenido plano (sin layout) para que services/modulos.py lo parta en módulos
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    parcial = CONTENT_DIR / f"{curso}.html"
    parcial.write_text(html.strip() + "\n", encoding="utf-8")
    print(f"{parcial} — {len(html)} chars")


if __name__ == "__main__":
    convertir(0)
    convertir(1)
    print("Listo.")