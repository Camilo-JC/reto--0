import random

import database as db
from app import app, setup_application

setup_application()


def test_control_acceso_devolver_prestamo_ajeno_retorna_403():
    cliente = app.test_client()
    rand = random.randint(1000, 9999)

    # Registrar dos lectores ficticios
    u_a, _ = db.create_user(f"lector_a_{rand}", "pass123", f"Lector A {rand}", f"a_{rand}@test.com", "lector")
    _u_b, _ = db.create_user(f"lector_b_{rand}", "pass123", f"Lector B {rand}", f"b_{rand}@test.com", "lector")

    # Registrar libro con ejemplares y prestarlo al Usuario A
    b_id, _ = db.create_book(
        f"Libro Test {rand}", "Autor Test", f"978-999-{rand}", "Ficción", "Desc", 5
    )
    loan_id, _ = db.create_loan(user_id=u_a, book_id=b_id, days=14)

    # Iniciar sesión como Usuario B
    cliente.post("/login", data={"username": f"lector_b_{rand}", "password": "pass123"})

    # Usuario B intenta devolver el préstamo de Usuario A
    respuesta = cliente.post(f"/loans/{loan_id}/return")

    # Debe denegar con 403 Forbidden
    assert respuesta.status_code == 403

def test_validacion_entradas_registro_rechaza_texto_excesivo():
    """
    Comprueba que el formulario de registro rechace un nombre de usuario con longitud
    excesiva (> 50 caracteres) y no cree el registro en la base de datos.
    """
    cliente = app.test_client()
    rand = random.randint(1000, 9999)
    conn = db.get_db()
    total_antes = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()["count"]
    conn.close()

    # Intento de registro con nombre de usuario excesivo (> 500 caracteres)
    username_excesivo = f"user_{rand}_" + ("a" * 500)
    respuesta = cliente.post(
        "/register",
        data={
          "username": username_excesivo,
          "full_name": f"Usuario Test {rand}",
          "email": f"user_{rand}@correo.com",
          "password": "password123",
          "confirm_password": "password123",
      },
      follow_redirects=True,
  )

    conn = db.get_db()
    total_despues = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()["count"]
    conn.close()

    # No debe crear registros si la entrada es inválida
    assert total_despues == total_antes
    assert b"no debe superar" in respuesta.data

def test_manejo_errores_libro_inexistente_retorna_404():
    """
    Comprueba que al solicitar un libro inexistente (/books/99999), la aplicación
    responda con código HTTP 404 Not Found y no exponga trazas de error (Traceback).
    """
    cliente = app.test_client()
    respuesta = cliente.get("/books/99999")

    assert respuesta.status_code == 404
    assert b"Traceback" not in respuesta.data