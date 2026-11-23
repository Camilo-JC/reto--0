"""
Aplicación Web de Gestión de Libros y Préstamos
Desarrollada en Flask con SQLite3, control de roles (Admin y Lector)
y diseño responsivo con Bootstrap 5.
"""

import os
from datetime import date
from functools import wraps

from dotenv import load_dotenv

load_dotenv()
from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

import database as db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# ==========================================
# Helpers de Autenticación y Contexto
# ==========================================
@app.before_request
def load_logged_in_user():
    """Carga los datos del usuario en sesión en la variable global g."""
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = db.get_user_by_id(user_id)
        if g.user is None:
            session.clear()


@app.context_processor
def inject_today():
    """Inyecta la fecha de hoy para comparaciones en plantillas."""
    return {"today_date": date.today().isoformat()}


def login_required(view):
    """Decorador para rutas que requieren estar autenticado."""
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Por favor inicia sesión para acceder a esta página.", "warning")
            return redirect(url_for("login", next=request.url))
        return view(**kwargs)

    return wrapped_view


def admin_required(view):
    """Decorador para rutas exclusivas de usuarios Administradores."""
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Por favor inicia sesión para acceder a esta página.", "warning")
            return redirect(url_for("login", next=request.url))
        if g.user["role"] != "admin":
            flash("Acceso denegado: Se requieren permisos de Administrador.", "danger")
            return redirect(url_for("catalog"))
        return view(**kwargs)

    return wrapped_view


# ==========================================
# Rutas de Autenticación
# ==========================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user is not None:
        if g.user["role"] == "admin":
            return redirect(url_for("dashboard"))
        return redirect(url_for("catalog"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = db.get_user_by_username(username)

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["full_name"] = user["full_name"]

            flash(f"¡Bienvenido(a), {user['full_name']}!", "success")
            next_page = request.args.get("next")
            if next_page and not next_page.startswith("//") and not next_page.startswith("http"):
                return redirect(next_page)

            if user["role"] == "admin":
                return redirect(url_for("dashboard"))
            return redirect(url_for("catalog"))
        else:
            flash("Usuario o contraseña incorrectos.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registro público para nuevos usuarios Lectores."""
    if g.user is not None:
        return redirect(url_for("catalog"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = []
        if not username or len(username) < 3:
            errors.append("El nombre de usuario debe tener al menos 3 caracteres.")
        if not full_name:
            errors.append("El nombre completo es obligatorio.")
        if not email or "@" not in email:
            errors.append("Ingresa un correo electrónico válido.")
        if not password or len(password) < 6:
            errors.append("La contraseña debe tener al menos 6 caracteres.")
        if password != confirm_password:
            errors.append("Las contraseñas no coinciden.")

        if errors:
            for err in errors:
                flash(err, "danger")
        else:
            _user_id, error = db.create_user(
                username=username,
                password=password,
                full_name=full_name,
                email=email,
                role="lector",
            )
            if error:
                flash(error, "danger")
            else:
                flash("¡Cuenta de lector creada con éxito! Ya puedes iniciar sesión.", "success")
                return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for("login"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not check_password_hash(g.user["password_hash"], current_password):
            flash("La contraseña actual es incorrecta.", "danger")
        elif len(new_password) < 6:
            flash("La nueva contraseña debe tener al menos 6 caracteres.", "danger")
        elif new_password != confirm_password:
            flash("La confirmación de la nueva contraseña no coincide.", "danger")
        else:
            conn = db.get_db()
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (generate_password_hash(new_password), g.user["id"]),
            )
            conn.commit()
            conn.close()
            flash("Contraseña actualizada exitosamente.", "success")
            return redirect(url_for("profile"))

    # Estadísticas del usuario
    conn = db.get_db()
    my_loans_count = conn.execute(
        "SELECT COUNT(*) as count FROM loans WHERE user_id = ?", (g.user["id"],)
    ).fetchone()["count"]
    active_loans_count = conn.execute(
        "SELECT COUNT(*) as count FROM loans WHERE user_id = ? AND status IN ('activo', 'vencido')",
        (g.user["id"],),
    ).fetchone()["count"]
    conn.close()

    return render_template("profile.html", my_loans_count=my_loans_count, active_loans_count=active_loans_count)


# ==========================================
# Rutas Principales y Catálogo
# ==========================================
@app.route("/")
def index():
    if g.user is None:
        return redirect(url_for("catalog"))
    if g.user["role"] == "admin":
        return redirect(url_for("dashboard"))
    return redirect(url_for("catalog"))


@app.route("/dashboard")
@admin_required
def dashboard():
    metrics = db.get_dashboard_metrics()
    return render_template("dashboard.html", metrics=metrics)


@app.route("/catalog")
def catalog():
    """Catálogo de libros visible para todos los usuarios y visitantes."""
    search_query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    available_only = request.args.get("available") == "1"

    books = db.get_all_books(
        search_query=search_query if search_query else None,
        category=category if category else None,
        available_only=available_only,
    )
    categories = db.get_book_categories()

    # Si el usuario es lector, verificar qué libros tiene ya prestados
    borrowed_book_ids = set()
    if g.user and g.user["role"] == "lector":
        conn = db.get_db()
        rows = conn.execute(
            "SELECT book_id FROM loans WHERE user_id = ? AND status IN ('activo', 'vencido')",
            (g.user["id"],),
        ).fetchall()
        conn.close()
        borrowed_book_ids = {r["book_id"] for r in rows}

    return render_template(
        "catalog.html",
        books=books,
        categories=categories,
        search_query=search_query,
        selected_category=category,
        available_only=available_only,
        borrowed_book_ids=borrowed_book_ids,
    )


@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = db.get_book_by_id(book_id)
    if not book:
        flash("Libro no encontrado.", "danger")
        return redirect(url_for("catalog"))

    user_has_loan = False
    active_loan = None
    if g.user and g.user["role"] == "lector":
        conn = db.get_db()
        active_loan = conn.execute(
            "SELECT * FROM loans WHERE user_id = ? AND book_id = ? AND status IN ('activo', 'vencido')",
            (g.user["id"], book_id),
        ).fetchone()
        conn.close()
        if active_loan:
            user_has_loan = True

    # Si es admin, mostrar historial de préstamos del libro
    loan_history = []
    if g.user and g.user["role"] == "admin":
        conn = db.get_db()
        loan_history = conn.execute(
            """
            SELECT l.*, u.full_name as user_name, u.email as user_email
            FROM loans l
            JOIN users u ON l.user_id = u.id
            WHERE l.book_id = ?
            ORDER BY l.loan_date DESC
            LIMIT 10
        """,
            (book_id,),
        ).fetchall()
        conn.close()

    return render_template(
        "book_detail.html",
        book=book,
        user_has_loan=user_has_loan,
        active_loan=active_loan,
        loan_history=loan_history,
    )


# ==========================================
# Gestión de Libros (Admin)
# ==========================================
@app.route("/books/new", methods=["GET", "POST"])
@admin_required
def book_create():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        isbn = request.form.get("isbn", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        total_copies = request.form.get("total_copies", "1").strip()
        pub_year = request.form.get("publication_year", "").strip()

        if not title or not author or not isbn or not category:
            flash("Por favor completa los campos obligatorios (Título, Autor, ISBN, Categoría).", "danger")
        else:
            try:
                total_copies_int = int(total_copies)
                if total_copies_int < 1:
                    raise ValueError()
            except ValueError:
                flash("El número total de ejemplares debe ser un entero positivo.", "danger")
                return render_template("book_form.html", action="new", form_data=request.form)

            pub_year_val = int(pub_year) if pub_year and pub_year.isdigit() else None

            book_id, error = db.create_book(
                title=title,
                author=author,
                isbn=isbn,
                category=category,
                description=description,
                total_copies=total_copies_int,
                publication_year=pub_year_val,
            )

            if error:
                flash(error, "danger")
                return render_template("book_form.html", action="new", form_data=request.form)

            flash(f"Libro '{title}' registrado correctamente con {total_copies_int} copias.", "success")
            return redirect(url_for("book_detail", book_id=book_id))

    return render_template("book_form.html", action="new", form_data={})


@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
@admin_required
def book_edit(book_id):
    book = db.get_book_by_id(book_id)
    if not book:
        flash("Libro no encontrado.", "danger")
        return redirect(url_for("catalog"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        isbn = request.form.get("isbn", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        total_copies = request.form.get("total_copies", "").strip()
        pub_year = request.form.get("publication_year", "").strip()

        if not title or not author or not isbn or not category:
            flash("Por favor completa los campos obligatorios.", "danger")
        else:
            try:
                total_copies_int = int(total_copies)
                if total_copies_int < 1:
                    raise ValueError()
            except ValueError:
                flash("El total de copias debe ser al menos 1.", "danger")
                return render_template("book_form.html", action="edit", book=book)

            pub_year_val = int(pub_year) if pub_year and pub_year.isdigit() else None

            success, error = db.update_book(
                book_id=book_id,
                title=title,
                author=author,
                isbn=isbn,
                category=category,
                description=description,
                total_copies=total_copies_int,
                publication_year=pub_year_val,
            )

            if not success:
                flash(error, "danger")
                return render_template("book_form.html", action="edit", book=book)

            flash(f"Libro '{title}' actualizado exitosamente.", "success")
            return redirect(url_for("book_detail", book_id=book_id))

    return render_template("book_form.html", action="edit", book=book)


@app.route("/books/<int:book_id>/delete", methods=["POST"])
@admin_required
def book_delete(book_id):
    book = db.get_book_by_id(book_id)
    if not book:
        flash("Libro no encontrado.", "danger")
        return redirect(url_for("catalog"))

    success, error = db.delete_book(book_id)
    if not success:
        flash(error, "danger")
        return redirect(url_for("book_detail", book_id=book_id))

    flash(f"El libro '{book['title']}' ha sido eliminado del catálogo.", "success")
    return redirect(url_for("catalog"))


# ==========================================
# Gestión de Préstamos
# ==========================================
@app.route("/loans")
@login_required
def loans_list():
    """Visualización de préstamos. Administrador ve todos, Lector ve sus préstamos."""
    db.update_overdue_loans()
    status_filter = request.args.get("status", "todos")

    if g.user["role"] == "admin":
        loans = db.get_all_loans(status=status_filter)
        return render_template("loans.html", loans=loans, status_filter=status_filter, is_admin=True)
    else:
        loans = db.get_all_loans(status=status_filter, user_id=g.user["id"])
        return render_template("loans.html", loans=loans, status_filter=status_filter, is_admin=False)


@app.route("/my-loans")
@login_required
def my_loans():
    """Acceso directo para que un lector revise sus préstamos."""
    db.update_overdue_loans()
    status_filter = request.args.get("status", "todos")
    loans = db.get_all_loans(status=status_filter, user_id=g.user["id"])
    return render_template("loans.html", loans=loans, status_filter=status_filter, is_admin=False)


@app.route("/loans/new", methods=["GET", "POST"])
@admin_required
def loan_create():
    """Registro manual de un préstamo por parte del administrador."""
    if request.method == "POST":
        user_id = request.form.get("user_id")
        book_id = request.form.get("book_id")
        days = request.form.get("days", "14")
        notes = request.form.get("notes", "").strip()

        try:
            user_id = int(user_id)
            book_id = int(book_id)
            days = int(days)
        except (ValueError, TypeError):
            flash("Datos del formulario inválidos.", "danger")
            return redirect(url_for("loan_create"))

        _loan_id, error = db.create_loan(user_id=user_id, book_id=book_id, days=days, notes=notes)
        if error:
            flash(error, "danger")
        else:
            flash("Préstamo registrado exitosamente.", "success")
            return redirect(url_for("loans_list"))

    # Datos para los selects del formulario
    conn = db.get_db()
    users = conn.execute("SELECT id, full_name, email, username FROM users WHERE role = 'lector' ORDER BY full_name").fetchall()
    books = conn.execute("SELECT id, title, author, available_copies FROM books WHERE available_copies > 0 ORDER BY title").fetchall()
    conn.close()

    preselected_book_id = request.args.get("book_id", type=int)

    return render_template(
        "loan_form.html",
        users=users,
        books=books,
        preselected_book_id=preselected_book_id,
    )


@app.route("/loans/request/<int:book_id>", methods=["POST"])
@login_required
def loan_request(book_id):
    """Acción del lector para solicitar el préstamo de un libro."""
    days = int(request.form.get("days", 14))
    notes = request.form.get("notes", "").strip()

    _loan_id, error = db.create_loan(user_id=g.user["id"], book_id=book_id, days=days, notes=notes)
    if error:
        flash(error, "danger")
    else:
        book = db.get_book_by_id(book_id)
        title = book["title"] if book else "el libro"
        flash(f"¡Préstamo de '{title}' registrado con éxito! Tienes {days} días para su lectura.", "success")
        return redirect(url_for("my_loans"))

    return redirect(url_for("book_detail", book_id=book_id))


@app.route("/loans/<int:loan_id>/return", methods=["POST"])
@login_required
def loan_return(loan_id):
    """Registra la devolución de un libro prestado."""
    loan = db.get_loan_by_id(loan_id)
    if not loan:
        flash("Préstamo no encontrado.", "danger")
        return redirect(url_for("loans_list"))

    # Permitir si es admin O si es el mismo usuario lector que lo tiene prestado
    if g.user["role"] != "admin" and g.user["id"] != loan["user_id"]:
        abort(403)

    success, error = db.return_loan(loan_id)
    if not success:
        flash(error, "danger")
    else:
        flash(f"Libro '{loan['book_title']}' devuelto con éxito. Ejemplar reintegrado al inventario.", "success")

    if g.user["role"] == "admin":
        return redirect(url_for("loans_list"))
    return redirect(url_for("my_loans"))


# ==========================================
# Gestión de Usuarios (Admin)
# ==========================================
@app.route("/users", methods=["GET", "POST"])
@admin_required
def users_list():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "lector")

        if not username or not full_name or not email or not password:
            flash("Todos los campos son obligatorios para crear un usuario.", "danger")
        elif role not in ("admin", "lector"):
            flash("Rol no válido.", "danger")
        else:
            _user_id, error = db.create_user(
                username=username,
                password=password,
                full_name=full_name,
                email=email,
                role=role,
            )
            if error:
                flash(error, "danger")
            else:
                flash(f"Usuario '{username}' ({role}) creado exitosamente.", "success")
                return redirect(url_for("users_list"))

    users = db.get_all_users()
    return render_template("users.html", users=users)


# ==========================================
# Inicialización y Ejecución
# ==========================================
def setup_application():
    """Inicializa la base de datos y los datos de prueba."""
    db.init_db()
    db.seed_db()
    db.update_overdue_loans()


if __name__ == "__main__":
    setup_application()
    print("Iniciando servidor de Biblioteca en http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1", port=5000)

