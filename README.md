# 📚 BiblioTech - Sistema de Gestión de Libros y Préstamos

Una aplicación web completa desarrollada en **Python (Flask)** con base de datos **SQLite3** y diseño moderno y responsivo con **Bootstrap 5**.

Permite gestionar el catálogo completo de una biblioteca, controlar el inventario de copias físicas y administrar préstamos con control de acceso basado en roles (**Administrador** y **Lector**).

---

## 🚀 Inicio Rápido

### 1. Requisitos Previos
Tener instalado Python 3.10 o superior.

### 2. Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar la Aplicación
```bash
python run.py
```
Abre tu navegador en: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 👥 Cuentas de Acceso de Prueba

El sistema inicializa automáticamente la base de datos con usuarios y catálogo de muestra:

| Rol | Usuario | Contraseña | Permisos |
|---|---|---|---|
| **Administrador** | `admin` | `admin123` | Control total del inventario, CRUD de libros, gestión de préstamos, usuarios y métricas. |
| **Lector** | `lector` | `lector123` | Explorar catálogo, solicitar préstamos de libros, consultar fecha límite y devolver. |
| **Lector 2** | `carlos` | `carlos123` | Cuenta secundaria de lector con préstamos previos. |

> 💡 *En la pantalla de inicio de sesión dispones de botones de un clic para autocompletar estas credenciales al instante.*

---

## ✨ Características Principales

### 🛡️ Funcionalidades del Administrador
- **Dashboard Estadístico:**
  - Métricas en tiempo real: Total de títulos, inventario total vs copias disponibles, préstamos activos y préstamos vencidos.
  - Tabla de actividad reciente con accesos rápidos para devoluciones.
- **Gestión de Libros (CRUD):**
  - Registro de nuevos libros con título, autor, ISBN único, categoría, año de publicación, total de ejemplares y sinopsis.
  - Edición de información y ajuste seguro de inventario (impide reducir copias por debajo de las que están prestadas).
  - Eliminación segura con protección ante libros con préstamos activos.
- **Control Global de Préstamos:**
  - Registro manual de préstamos asignando cualquier libro disponible a cualquier lector registrado.
  - Filtrado por estado: *Todos*, *Activos*, *Vencidos* y *Devueltos*.
  - Detección y marcado automático de préstamos fuera de fecha (*Vencidos*).
  - Devolución en un clic con reincorporación inmediata del ejemplar al stock disponible.
- **Gestión de Usuarios:**
  - Visualización del directorio de lectores y administradores.
  - Contador de préstamos activos por lector.
  - Creación de nuevos usuarios con rol personalizable.

### 📖 Funcionalidades del Lector
- **Catálogo Interactivo:**
  - Búsqueda en tiempo real por título, autor o código ISBN.
  - Filtro por categoría o género literario.
  - Interruptor para mostrar únicamente ejemplares con disponibilidad inmediata.
  - Barra visual de porcentaje de disponibilidad por libro.
- **Solicitud de Préstamos:**
  - Selección de plazo de lectura (7, 14, 21 o 30 días).
  - Control de restricciones: no se permite pedir un libro agotado ni solicitar dos veces el mismo título simultáneamente.
- **Panel "Mis Préstamos":**
  - Vista detallada de los libros en posesión del lector.
  - Alerta de fecha límite y estado del préstamo.
  - Opción para devolver el libro directamente desde la plataforma.
- **Registro y Perfil:**
  - Auto-registro público para nuevos lectores.
  - Gestión de perfil y actualización de contraseña.

---

## 🗄️ Modelo de Datos (SQLite)

- **`users`**: `id`, `username`, `password_hash`, `full_name`, `email`, `role ('admin' | 'lector')`, `created_at`.
- **`books`**: `id`, `title`, `author`, `isbn` (único), `category`, `description`, `total_copies`, `available_copies`, `publication_year`, `created_at`.
- **`loans`**: `id`, `user_id`, `book_id`, `loan_date`, `due_date`, `return_date`, `status ('activo' | 'devuelto' | 'vencido')`, `notes`, `created_at`.

---

## 🧪 Pruebas Automatizadas

Se incluye una suite de pruebas unitarias y de integración que cubre autenticación, control de permisos, operaciones de catálogo y flujo de préstamos:

```bash
python -m unittest test_app.py -v
```

---

## 📁 Estructura del Proyecto

```text
reto-0/
│
├── app.py              # Controlador principal Flask (rutas, auth y lógica)
├── database.py         # Conexión SQLite, esquemas, consultas y datos iniciales
├── run.py              # Script de arranque del servidor
├── test_app.py         # Suite de pruebas unitarias
├── requirements.txt    # Dependencias del proyecto
├── README.md           # Documentación
│
├── static/
│   └── css/
│       └── style.css   # Estilos personalizados y paleta visual
│
└── templates/          # Plantillas Jinja2 / Bootstrap 5
    ├── base.html       # Layout maestro con navbar y notificaciones
    ├── login.html      # Inicio de sesión con botones de acceso rápido
    ├── register.html   # Registro de lectores
    ├── dashboard.html  # Panel administrativo con métricas
    ├── catalog.html    # Catálogo con búsqueda y filtros
    ├── book_detail.html# Detalle de libro, historial y solicitud
    ├── book_form.html  # Formulario de alta y edición de libros
    ├── loans.html      # Lista de préstamos con filtros de estado
    ├── loan_form.html  # Formulario para asignar préstamos
    ├── users.html      # Administración de usuarios
    └── profile.html    # Perfil y cambio de contraseña
```

