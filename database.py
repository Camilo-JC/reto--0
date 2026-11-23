"""
Módulo de base de datos para la aplicación de Gestión de Libros y Préstamos.
Utiliza SQLite3 estándar con Row factory para consultas estructuradas.
"""

import sqlite3
import os
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash

DB_NAME = "biblioteca.db"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_NAME)


def get_db():
    """Obtiene una conexión a la base de datos con acceso a columnas por nombre."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Inicializa las tablas de la base de datos si no existen."""
    conn = get_db()
    cursor = conn.cursor()

    # Tabla de Usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'lector')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabla de Libros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            total_copies INTEGER NOT NULL DEFAULT 1,
            available_copies INTEGER NOT NULL DEFAULT 1,
            publication_year INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabla de Préstamos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            loan_date DATE NOT NULL,
            due_date DATE NOT NULL,
            return_date DATE,
            status TEXT NOT NULL CHECK(status IN ('activo', 'devuelto', 'vencido')),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def seed_db():
    """Inserta datos de prueba por defecto si la base de datos está vacía."""
    conn = get_db()
    cursor = conn.cursor()

    # Comprobar si ya existen usuarios
    cursor.execute("SELECT COUNT(*) as count FROM users")
    if cursor.fetchone()["count"] == 0:
        # Usuarios iniciales
        users = [
            (
                "admin",
                generate_password_hash("admin123"),
                "Administrador Principal",
                "admin@biblioteca.local",
                "admin",
            ),
            (
                "lector",
                generate_password_hash("lector123"),
                "Ana García Lectora",
                "ana.lector@biblioteca.local",
                "lector",
            ),
            (
                "carlos",
                generate_password_hash("carlos123"),
                "Carlos Martínez",
                "carlos.m@correo.local",
                "lector",
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO users (username, password_hash, full_name, email, role)
            VALUES (?, ?, ?, ?, ?)
        """,
            users,
        )

    # Comprobar si ya existen libros
    cursor.execute("SELECT COUNT(*) as count FROM books")
    if cursor.fetchone()["count"] == 0:
        sample_books = [
            (
                "Cien años de soledad",
                "Gabriel García Márquez",
                "978-0307474728",
                "Ficción / Realismo Mágico",
                "La obra maestra de Gabriel García Márquez narra la historia de la familia Buendía a lo largo de siete generaciones en el mítico pueblo de Macondo.",
                5,
                4,
                1967,
            ),
            (
                "Don Quijote de la Mancha",
                "Miguel de Cervantes",
                "978-8420412146",
                "Clásico / Novela",
                "Las aventuras del ingenioso hidalgo Don Quijote y su fiel escudero Sancho Panza por las tierras de la Mancha.",
                4,
                4,
                1605,
            ),
            (
                "El principito",
                "Antoine de Saint-Exupéry",
                "978-0156013987",
                "Infantil / Filosofía",
                "Un clásico poético que aborda el sentido de la vida, la amistad y el amor a través de los ojos de un pequeño príncipe de otro planeta.",
                6,
                5,
                1943,
            ),
            (
                "1984",
                "George Orwell",
                "978-0451524935",
                "Ciencia Ficción / Distopía",
                "Una inquietante advertencia sobre el totalitarismo, la vigilancia masiva y el control de la información en una sociedad opresiva.",
                4,
                3,
                1949,
            ),
            (
                "Ficciones",
                "Jorge Luis Borges",
                "978-0307950925",
                "Ficción / Cuentos",
                "Colección fundamental de relatos laberínticos, metafísicos y detectivescos del gran maestro argentino.",
                3,
                3,
                1944,
            ),
            (
                "Python Crash Course",
                "Eric Matthes",
                "978-1593279288",
                "Tecnología / Programación",
                "Guía práctica y completa para aprender a programar en Python desde cero hasta proyectos avanzados.",
                5,
                4,
                2019,
            ),
            (
                "Breve historia del tiempo",
                "Stephen Hawking",
                "978-8491990475",
                "Ciencia / Divulgación",
                "Explicación fascinante y accesible sobre los misterios del cosmos, los agujeros negros y el Big Bang.",
                3,
                3,
                1988,
            ),
            (
                "El amor en los tiempos del cólera",
                "Gabriel García Márquez",
                "978-0307389732",
                "Romance / Ficción",
                "La inolvidable historia de amor entre Florentino Ariza y Fermina Daza que perdura por más de medio siglo.",
                4,
                4,
                1985,
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO books (title, author, isbn, category, description, total_copies, available_copies, publication_year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            sample_books,
        )

    # Comprobar si ya existen préstamos
    cursor.execute("SELECT COUNT(*) as count FROM loans")
    if cursor.fetchone()["count"] == 0:
        today = date.today()
        # Prestamo activo
        loan1_date = (today - timedelta(days=5)).isoformat()
        loan1_due = (today + timedelta(days=9)).isoformat()

        # Prestamo activo
        loan2_date = (today - timedelta(days=2)).isoformat()
        loan2_due = (today + timedelta(days=12)).isoformat()

        # Prestamo devuelto
        loan3_date = (today - timedelta(days=20)).isoformat()
        loan3_due = (today - timedelta(days=6)).isoformat()
        loan3_returned = (today - timedelta(days=7)).isoformat()

        # Prestamo vencido (activo pero superó fecha de vencimiento)
        loan4_date = (today - timedelta(days=18)).isoformat()
        loan4_due = (today - timedelta(days=4)).isoformat()

        loans = [
            (2, 1, loan1_date, loan1_due, None, "activo", "Primer préstamo de Ana"),
            (2, 4, loan2_date, loan2_due, None, "activo", "Lectura mensual"),
            (3, 3, loan3_date, loan3_due, loan3_returned, "devuelto", "Devuelto en perfecto estado"),
            (3, 6, loan4_date, loan4_due, None, "vencido", "Pendiente de devolución urgente"),
        ]
        cursor.executemany(
            """
            INSERT INTO loans (user_id, book_id, loan_date, due_date, return_date, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            loans,
        )

    conn.commit()
    conn.close()


def update_overdue_loans():
    """Actualiza automáticamente a 'vencido' los préstamos activos cuya fecha límite ya pasó."""
    conn = get_db()
    cursor = conn.cursor()
    today_str = date.today().isoformat()
    cursor.execute(
        """
        UPDATE loans 
        SET status = 'vencido'
        WHERE status = 'activo' AND due_date < ?
    """,
        (today_str,),
    )
    conn.commit()
    conn.close()


# ==========================================
# Funciones de Usuarios
# ==========================================
def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user


def get_user_by_username(username):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user


def get_user_by_email(email):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user


def get_all_users():
    conn = get_db()
    users = conn.execute(
        """
        SELECT u.*, 
               (SELECT COUNT(*) FROM loans l WHERE l.user_id = u.id AND l.status IN ('activo', 'vencido')) as active_loans_count
        FROM users u 
        ORDER BY u.role ASC, u.full_name ASC
    """
    ).fetchall()
    conn.close()
    return users


def create_user(username, password, full_name, email, role="lector"):
    conn = get_db()
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    try:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, full_name, email, role)
            VALUES (?, ?, ?, ?, ?)
        """,
            (username.strip(), password_hash, full_name.strip(), email.strip().lower(), role),
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id, None
    except sqlite3.IntegrityError as e:
        error_msg = str(e)
        if "users.username" in error_msg:
            return None, "El nombre de usuario ya está registrado."
        elif "users.email" in error_msg:
            return None, "El correo electrónico ya está registrado."
        return None, "Error de integridad: el usuario o correo ya existe."
    finally:
        conn.close()


# ==========================================
# Funciones de Libros
# ==========================================
def get_all_books(search_query=None, category=None, available_only=False):
    conn = get_db()
    query = "SELECT * FROM books WHERE 1=1"
    params = []

    if search_query:
        query += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ?)"
        wildcard = f"%{search_query.strip()}%"
        params.extend([wildcard, wildcard, wildcard])

    if category:
        query += " AND category = ?"
        params.append(category)

    if available_only:
        query += " AND available_copies > 0"

    query += " ORDER BY title ASC"

    books = conn.execute(query, params).fetchall()
    conn.close()
    return books


def get_book_categories():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT category FROM books ORDER BY category ASC").fetchall()
    conn.close()
    return [r["category"] for r in rows if r["category"]]


def get_book_by_id(book_id):
    conn = get_db()
    book = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    conn.close()
    return book


def create_book(title, author, isbn, category, description, total_copies, publication_year=None):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO books (title, author, isbn, category, description, total_copies, available_copies, publication_year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                title.strip(),
                author.strip(),
                isbn.strip(),
                category.strip(),
                description.strip() if description else "",
                int(total_copies),
                int(total_copies),  # Inicialmente todas disponibles
                int(publication_year) if publication_year else None,
            ),
        )
        conn.commit()
        book_id = cursor.lastrowid
        return book_id, None
    except sqlite3.IntegrityError as e:
        if "books.isbn" in str(e):
            return None, "Ya existe un libro con ese código ISBN."
        return None, "Error al registrar el libro."
    finally:
        conn.close()


def update_book(book_id, title, author, isbn, category, description, total_copies, publication_year=None):
    conn = get_db()
    cursor = conn.cursor()
    current_book = get_book_by_id(book_id)
    if not current_book:
        conn.close()
        return False, "Libro no encontrado."

    # Calcular copias prestadas actualmente
    borrowed_copies = current_book["total_copies"] - current_book["available_copies"]
    new_total = int(total_copies)

    if new_total < borrowed_copies:
        conn.close()
        return (
            False,
            f"No puedes reducir el total a {new_total} copias porque hay {borrowed_copies} actualmente prestadas.",
        )

    new_available = new_total - borrowed_copies

    try:
        cursor.execute(
            """
            UPDATE books 
            SET title = ?, author = ?, isbn = ?, category = ?, description = ?,
                total_copies = ?, available_copies = ?, publication_year = ?
            WHERE id = ?
        """,
            (
                title.strip(),
                author.strip(),
                isbn.strip(),
                category.strip(),
                description.strip() if description else "",
                new_total,
                new_available,
                int(publication_year) if publication_year else None,
                book_id,
            ),
        )
        conn.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        if "books.isbn" in str(e):
            return False, "Ya existe otro libro con ese código ISBN."
        return False, "Error al actualizar el libro."
    finally:
        conn.close()


def delete_book(book_id):
    conn = get_db()
    cursor = conn.cursor()
    # Comprobar si hay préstamos activos
    active_loans = cursor.execute(
        "SELECT COUNT(*) as count FROM loans WHERE book_id = ? AND status IN ('activo', 'vencido')",
        (book_id,),
    ).fetchone()["count"]

    if active_loans > 0:
        conn.close()
        return False, "No se puede eliminar el libro porque tiene préstamos activos pendientes de devolución."

    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return True, None


# ==========================================
# Funciones de Préstamos
# ==========================================
def get_all_loans(status=None, user_id=None):
    conn = get_db()
    query = """
        SELECT l.*, 
               b.title as book_title, b.author as book_author, b.isbn as book_isbn,
               u.full_name as user_name, u.email as user_email, u.username as username
        FROM loans l
        JOIN books b ON l.book_id = b.id
        JOIN users u ON l.user_id = u.id
        WHERE 1=1
    """
    params = []

    if status and status != "todos":
        query += " AND l.status = ?"
        params.append(status)

    if user_id:
        query += " AND l.user_id = ?"
        params.append(user_id)

    query += " ORDER BY CASE l.status WHEN 'vencido' THEN 1 WHEN 'activo' THEN 2 ELSE 3 END, l.loan_date DESC"

    loans = conn.execute(query, params).fetchall()
    conn.close()
    return loans


def get_loan_by_id(loan_id):
    conn = get_db()
    query = """
        SELECT l.*, 
               b.title as book_title, b.author as book_author, b.isbn as book_isbn,
               u.full_name as user_name, u.email as user_email, u.username as username
        FROM loans l
        JOIN books b ON l.book_id = b.id
        JOIN users u ON l.user_id = u.id
        WHERE l.id = ?
    """
    loan = conn.execute(query, (loan_id,)).fetchone()
    conn.close()
    return loan


def create_loan(user_id, book_id, days=14, notes=None):
    """Crea un nuevo préstamo, disminuyendo las copias disponibles del libro."""
    conn = get_db()
    cursor = conn.cursor()

    # Verificar disponibilidad del libro
    book = cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if not book:
        conn.close()
        return None, "Libro no encontrado."

    if book["available_copies"] <= 0:
        conn.close()
        return None, "No hay ejemplares disponibles de este libro para préstamo."

    # Verificar si el usuario ya tiene un préstamo activo de este mismo libro
    existing_loan = cursor.execute(
        "SELECT id FROM loans WHERE user_id = ? AND book_id = ? AND status IN ('activo', 'vencido')",
        (user_id, book_id),
    ).fetchone()

    if existing_loan:
        conn.close()
        return None, "El usuario ya tiene un préstamo activo de este mismo libro."

    today = date.today()
    due_date = today + timedelta(days=days)

    try:
        # Registrar préstamo
        cursor.execute(
            """
            INSERT INTO loans (user_id, book_id, loan_date, due_date, status, notes)
            VALUES (?, ?, ?, ?, 'activo', ?)
        """,
            (user_id, book_id, today.isoformat(), due_date.isoformat(), notes),
        )
        loan_id = cursor.lastrowid

        # Disminuir copias disponibles
        cursor.execute(
            """
            UPDATE books
            SET available_copies = available_copies - 1
            WHERE id = ?
        """,
            (book_id,),
        )

        conn.commit()
        return loan_id, None
    except Exception as e:
        conn.rollback()
        return None, f"Error al registrar préstamo: {str(e)}"
    finally:
        conn.close()


def return_loan(loan_id):
    """Marca un préstamo como devuelto y reintegra el ejemplar al catálogo."""
    conn = get_db()
    cursor = conn.cursor()

    loan = cursor.execute("SELECT * FROM loans WHERE id = ?", (loan_id,)).fetchone()
    if not loan:
        conn.close()
        return False, "Préstamo no encontrado."

    if loan["status"] == "devuelto":
        conn.close()
        return False, "Este préstamo ya ha sido devuelto anteriormente."

    today_str = date.today().isoformat()

    try:
        # Actualizar préstamo
        cursor.execute(
            """
            UPDATE loans 
            SET status = 'devuelto', return_date = ?
            WHERE id = ?
        """,
            (today_str, loan_id),
        )

        # Restaurar copia en el libro
        cursor.execute(
            """
            UPDATE books
            SET available_copies = available_copies + 1
            WHERE id = ?
        """,
            (loan["book_id"],),
        )

        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, f"Error al procesar devolución: {str(e)}"
    finally:
        conn.close()


# ==========================================
# Estadísticas y Métricas (Dashboard)
# ==========================================
def get_dashboard_metrics():
    """Calcula las métricas principales para el panel administrativo."""
    update_overdue_loans()
    conn = get_db()
    cursor = conn.cursor()

    total_books = cursor.execute("SELECT COUNT(*) as count FROM books").fetchone()["count"]
    total_copies = cursor.execute("SELECT COALESCE(SUM(total_copies), 0) as total FROM books").fetchone()["total"]
    available_copies = cursor.execute(
        "SELECT COALESCE(SUM(available_copies), 0) as available FROM books"
    ).fetchone()["available"]

    active_loans = cursor.execute(
        "SELECT COUNT(*) as count FROM loans WHERE status = 'activo'"
    ).fetchone()["count"]
    overdue_loans = cursor.execute(
        "SELECT COUNT(*) as count FROM loans WHERE status = 'vencido'"
    ).fetchone()["count"]
    returned_loans = cursor.execute(
        "SELECT COUNT(*) as count FROM loans WHERE status = 'devuelto'"
    ).fetchone()["count"]

    total_readers = cursor.execute(
        "SELECT COUNT(*) as count FROM users WHERE role = 'lector'"
    ).fetchone()["count"]

    recent_loans = cursor.execute(
        """
        SELECT l.*, b.title as book_title, u.full_name as user_name
        FROM loans l
        JOIN books b ON l.book_id = b.id
        JOIN users u ON l.user_id = u.id
        ORDER BY l.created_at DESC
        LIMIT 5
    """
    ).fetchall()

    conn.close()

    return {
        "total_books": total_books,
        "total_copies": total_copies,
        "available_copies": available_copies,
        "active_loans": active_loans,
        "overdue_loans": overdue_loans,
        "returned_loans": returned_loans,
        "total_readers": total_readers,
        "recent_loans": recent_loans,
    }

