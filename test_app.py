"""
Pruebas automatizadas completas para la aplicación de Biblioteca y Préstamos.
Verifica:
1. Inicialización y sembrado de base de datos.
2. Autenticación de Admin y Lector.
3. Control de acceso y permisos por rol.
4. CRUD de Libros.
5. Flujo de préstamos (solicitud, inventario de copias, devolución).
6. Búsqueda y filtrado de catálogo.
"""

import os
import tempfile
import unittest

import database as db
from app import app


class BibliotecaTestCase(unittest.TestCase):
    def setUp(self):
        self.original_db_path = db.DB_PATH
        self.db_fd, self.db_path = tempfile.mkstemp()
        db.DB_PATH = self.db_path

        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.secret_key = "test-secret-key"
        self.client = app.test_client()

        # Inicializar y sembrar
        db.init_db()
        db.seed_db()

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
        db.DB_PATH = self.original_db_path

    # ----------------------------------------------------
    # Autenticación y Sesiones
    # ----------------------------------------------------
    def login(self, username, password):
        return self.client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def logout(self):
        return self.client.get("/logout", follow_redirects=True)

    def test_login_admin(self):
        """Verifica que el administrador puede iniciar sesión y acceder al dashboard."""
        response = self.login("admin", "admin123")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Panel de Control de la Biblioteca", response.data)
        self.assertIn(b"Administrador Principal", response.data)

    def test_login_lector(self):
        """Verifica que el lector puede iniciar sesión y es redirigido al catálogo."""
        response = self.login("lector", "lector123")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Catálogo de Libros".encode(), response.data)
        self.assertIn("Ana García Lectora".encode(), response.data)

    def test_login_invalid(self):
        """Verifica el rechazo de credenciales incorrectas."""
        response = self.login("admin", "contraseñaincorrecta")
        self.assertIn("Usuario o contraseña incorrectos".encode(), response.data)

    def test_register_reader(self):
        """Verifica el registro de un nuevo lector."""
        response = self.client.post(
            "/register",
            data={
                "username": "nuevolector",
                "full_name": "Nuevo Lector Demo",
                "email": "nuevo@correo.com",
                "password": "password123",
                "confirm_password": "password123",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("¡Cuenta de lector creada con éxito!".encode(), response.data)

        # Iniciar sesión con el nuevo usuario
        login_res = self.login("nuevolector", "password123")
        self.assertIn(b"Nuevo Lector Demo", login_res.data)

    # ----------------------------------------------------
    # Control de Permisos
    # ----------------------------------------------------
    def test_admin_routes_forbidden_for_reader(self):
        """Verifica que un lector no puede acceder al dashboard ni crear libros."""
        self.login("lector", "lector123")

        # Intento de acceso a dashboard
        res = self.client.get("/dashboard", follow_redirects=True)
        self.assertIn(b"Acceso denegado: Se requieren permisos de Administrador", res.data)

        # Intento de acceso a nuevo libro
        res2 = self.client.get("/books/new", follow_redirects=True)
        self.assertIn(b"Acceso denegado", res2.data)

    # ----------------------------------------------------
    # CRUD de Libros
    # ----------------------------------------------------
    def test_create_and_read_book(self):
        """Verifica la creación y visualización de un libro por parte del Admin."""
        self.login("admin", "admin123")

        # Crear libro
        res = self.client.post(
            "/books/new",
            data={
                "title": "Clean Code",
                "author": "Robert C. Martin",
                "isbn": "978-0132350884",
                "category": "Tecnología / Programación",
                "total_copies": "5",
                "publication_year": "2008",
                "description": "Manual de estilo para el desarrollo ágil de software.",
            },
            follow_redirects=True,
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Clean Code", res.data)
        self.assertIn(b"Robert C. Martin", res.data)

        # Comprobar en catálogo
        cat_res = self.client.get("/catalog?q=Clean Code")
        self.assertIn(b"Clean Code", cat_res.data)

    def test_edit_book(self):
        """Verifica la edición de un libro existente."""
        self.login("admin", "admin123")

        # El libro id=1 es 'Cien años de soledad'
        res = self.client.post(
            "/books/1/edit",
            data={
                "title": "Cien años de soledad (Edición Conmemorativa)",
                "author": "Gabriel García Márquez",
                "isbn": "978-0307474728",
                "category": "Ficción / Realismo Mágico",
                "total_copies": "6",
                "publication_year": "1967",
                "description": "Edición especial conmemorativa.",
            },
            follow_redirects=True,
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"actualizado exitosamente", res.data)

        book = db.get_book_by_id(1)
        self.assertEqual(book["title"], "Cien años de soledad (Edición Conmemorativa)")
        self.assertEqual(book["total_copies"], 6)

    # ----------------------------------------------------
    # Flujo de Préstamos y Disponibilidad
    # ----------------------------------------------------
    def test_loan_request_and_return_flow(self):
        """Verifica que un lector puede solicitar un libro, se descuenta del stock y luego se reintegra al devolver."""
        self.login("lector", "lector123")

        # Seleccionar libro con copias disponibles (ej. libro 2: Don Quijote)
        book_before = db.get_book_by_id(2)
        initial_avail = book_before["available_copies"]
        self.assertGreater(initial_avail, 0)

        # Solicitar préstamo
        req_res = self.client.post("/loans/request/2", data={"days": "14", "notes": "Para examen"}, follow_redirects=True)
        self.assertEqual(req_res.status_code, 200)
        self.assertIn("Préstamo de &#39;Don Quijote de la Mancha&#39; registrado con éxito".encode(), req_res.data)

        # Comprobar que el inventario bajó en 1
        book_after_loan = db.get_book_by_id(2)
        self.assertEqual(book_after_loan["available_copies"], initial_avail - 1)

        # Obtener el préstamo recién creado
        conn = db.get_db()
        loan = conn.execute("SELECT id FROM loans WHERE user_id = 2 AND book_id = 2 AND status = 'activo'").fetchone()
        conn.close()
        self.assertIsNotNone(loan)

        # Lector devuelve el libro
        ret_res = self.client.post(f"/loans/{loan['id']}/return", follow_redirects=True)
        self.assertEqual(ret_res.status_code, 200)
        self.assertIn("devuelto con éxito".encode(), ret_res.data)

        # Comprobar que el inventario volvió al valor inicial
        book_after_return = db.get_book_by_id(2)
        self.assertEqual(book_after_return["available_copies"], initial_avail)

    def test_duplicate_loan_prevention(self):
        """Verifica que un mismo usuario no pueda solicitar dos veces el mismo libro simultáneamente."""
        self.login("lector", "lector123")

        # Primer préstamo de libro 5 (Ficciones)
        self.client.post("/loans/request/5", data={"days": "14"}, follow_redirects=True)

        # Segundo intento de préstamo del mismo libro
        res = self.client.post("/loans/request/5", data={"days": "14"}, follow_redirects=True)
        self.assertIn("ya tiene un préstamo activo de este mismo libro".encode(), res.data)

    def test_catalog_search_and_filter(self):
        """Verifica la búsqueda por texto y filtro por categoría."""
        res_search = self.client.get("/catalog?q=Quijote")
        self.assertIn(b"Don Quijote de la Mancha", res_search.data)
        self.assertNotIn(b"1984", res_search.data)

        res_cat = self.client.get("/catalog?category=Tecnología / Programación")
        self.assertIn(b"Python Crash Course", res_cat.data)


if __name__ == "__main__":
    unittest.main()

