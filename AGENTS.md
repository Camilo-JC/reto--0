# AGENTS.md

## Proyecto
Aplicación web en Python para registrar libros y préstamos de biblioteca.
Permite gestionar el catálogo e inventario con roles de administrador y lector.

## Stack
- Backend: Python 3.14 con Flask 3.1.3
- Base de datos: SQLite3 con Row factory
- Variables de entorno: python-dotenv
- Plantillas y Frontend: Jinja2, Bootstrap 5.3 y Bootstrap Icons
- Calidad y pruebas: pytest, Ruff y pre-commit

## Comandos
- Instalar dependencias: pip install -r requirements.txt
- Ejecutar servidor: python run.py
- Pruebas automatizadas: python -m pytest -v
- Revisión de estilo y linting: ruff check .

## Estructura
- app.py: Rutas Flask, autenticación, control de sesiones y lógica de negocio.
- database.py: Conexión SQLite3, esquemas, transacciones de stock y consultas.
- run.py: Script de inicialización y arranque del servidor web.
- templates/: Plantillas HTML Jinja2 con diseño responsivo Bootstrap 5.
- static/: Archivos estáticos de hojas de estilo CSS personalizadas.
- requirements.txt: Lista de dependencias del entorno de producción.
- .env.example: Plantilla con las variables de entorno requeridas.
- .gitignore: Reglas de exclusión para Git (oculta .venv, .env, *.db y cache).
- tests/: Pruebas automatizadas (humo y regresión de fallos).

## Qué no hacer
- No modificar las pruebas para que pasen: corregir siempre el código de la aplicación.
- No escribir claves ni secretos directamente en el código fuente.
- No instalar dependencias sin explicar su propósito y justificación técnica.
- No hacer commit ni push automáticamente sin autorización explícita.

## Lecciones aprendidas
- Control de acceso: las operaciones no autorizadas sobre recursos de otro usuario se rechazan con código 403 Forbidden, nunca con redirección 302.
