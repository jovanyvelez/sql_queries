# Contribuir

Gracias por tu interes en contribuir a este proyecto educativo.

## Como contribuir

1. Haz un fork del repositorio
2. Crea una rama: `git checkout -b mi-mejora`
3. Haz tus cambios
4. Ejecuta la app localmente y prueba que todo funcione:
   ```bash
   cd app
   cp .env-sample .env   # editar con tu DATABASE_URL
   uv run fastapi dev main.py
   ```
5. Haz commit con mensajes descriptivos
6. Abre un Pull Request

## Estilo de codigo

- Python: sigue el estilo existente (sin comentarios innecesarios, funciones pequenas)
- SQL: nombres de tablas/columnas en espanol, comillas dobles para identificadores
- HTML/CSS: un solo archivo `static/estilos.css`, templates que extienden `base.html`

## Reportar bugs

Usa la plantilla de bug report en Issues. Incluye la consulta SQL que causa el problema si aplica.

## Licencia

Al contribuir, aceptas que tu codigo se distribuya bajo la licencia MIT del proyecto.
