"""
Script principal de ejecución para la aplicación BiblioTech.
Inicializa la base de datos con datos de ejemplo si es necesario
y arranca el servidor web.
"""

from app import app, setup_application

if __name__ == "__main__":
    setup_application()
    print("=" * 60)
    print("   SISTEMA DE GESTIÓN DE LIBROS Y PRÉSTAMOS (BiblioTech)")
    print("=" * 60)
    print("Base de datos inicializada correctamente.")
    print("Credenciales de prueba disponibles:")
    print("  - Administrador : usuario 'admin'  / contraseña 'admin123'")
    print("  - Lector Demo   : usuario 'lector' / contraseña 'lector123'")
    print("-" * 60)
    print("Iniciando servidor web en: http://127.0.0.1:5000")
    print("Presiona CTRL + C para detener el servidor.")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)

