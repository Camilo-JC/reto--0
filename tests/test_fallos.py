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
