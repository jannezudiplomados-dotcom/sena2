# Mejoras aplicadas al proyecto

Este paquete contiene la version **corregida** del backend del Sistema de Gestion de Fichas SENA.
A continuacion, el detalle de los cambios frente a la version original.

## Nota importante sobre alcance
- Se incluyen todos los archivos **Python** (backend), `database.sql`, configuracion y documentacion.
- **No** se incluyen las plantillas HTML (`templates/`) ni los `static/` originales, porque contenian
  datos personales de aprendices (firmas y documentos). Debes copiar tu carpeta `templates/`
  en este proyecto y aplicar el pequeno cambio de los botones de eliminar (ver mas abajo).

---

## 1. Seguridad (critico)

### 1.1 Credenciales y SECRET_KEY fuera del codigo
- `config.py` ahora lee todo de variables de entorno / `.env` (con `python-dotenv`).
- `SECRET_KEY` es **obligatoria**; si falta, la app no arranca (evita usar una clave por defecto conocida).
- Se agrego `.env.example` y `.gitignore`.

### 1.2 Modo debug controlado
- `app.run(debug=True, host='0.0.0.0')` se reemplazo por control via entorno (`FLASK_DEBUG`, `HOST`, `PORT`).
- Cookies de sesion endurecidas: `HttpOnly`, `SameSite=Lax`, y `Secure` opcional para HTTPS.

### 1.3 Hash de contrasenas seguro
- Se elimino `SHA2(password, 256)` (rapido y sin sal).
- Ahora se usa `werkzeug.security.generate_password_hash` / `check_password_hash`.
- Se elimino el admin por defecto `admin/admin123`. Se crea con `python crear_admin.py`.

### 1.4 Borrados por POST + CSRF
- Las rutas `eliminar` de usuarios, fichas, programas y plantillas ahora son `methods=['POST']`.
- Requieren token CSRF (ya activo con Flask-WTF). Ver el snippet de plantilla mas abajo.

### 1.5 Conversion a PDF sin inyeccion de codigo
- Se elimino la ejecucion de `subprocess.run(['python', '-c', script])` con rutas interpoladas.
- DOCX -> PDF usa `docx2pdf` (Word en Windows) y luego LibreOffice; XLSX -> PDF usa LibreOffice.
- Ambos con fallback a reportlab. Los nombres de archivo se sanean con `secure_filename`.

### 1.6 Manejo de errores
- Se dejo de mostrar `str(e)` al usuario (evita filtrar detalles internos). Se registra en el log del servidor.

---

## 2. Funcionalidades documentadas que faltaban

### 2.1 Auditoria (`log_actividades`)
- Nueva tabla `log_actividades` y funcion `registrar_actividad(...)`.
- Se registra login, logout, crear/editar/eliminar y generacion de documentos, con IP y timestamp.

### 2.2 Multi-admin con roles + estado activo
- Tabla `admin` con columnas `rol` ('superadmin'/'admin') y `activo`.
- Decorador `role_required(...)` en `routes/auth.py`.

### 2.3 Bloqueo por intentos de login
- Nueva tabla `intentos_login` + `MAX_LOGIN_ATTEMPTS` y `LOCKOUT_MINUTES`.
- Tras N fallos por usuario/IP se bloquea temporalmente.

### 2.4 Paginacion (PER_PAGE)
- `obtener_usuarios_paginado(page, per_page, buscar)` y `contar_usuarios(buscar)`.
- La ruta `usuarios.listar` acepta `?page=` y `?q=` (busqueda).

---

## 3. Calidad / bugs menores
- `current_year` ahora es dinamico (`datetime.now().year`).
- Las firmas dibujadas se guardan con timestamp (ya no se sobrescriben) y se validan como imagen real.
- Al actualizar/eliminar un aprendiz se borra su firma anterior (evita archivos huerfanos).
- `obtener_fichas()` usa `GROUP BY` en vez de subconsulta por fila (evita N+1).
- `firma_imagen` pasa de `TEXT` a `VARCHAR(255)` (guarda un nombre de archivo).
- Se agrego `UNIQUE` en `usuarios.identificacion`.

---

## 4. Cambio necesario en tus plantillas (deletes por POST)

Donde antes tenias un enlace de eliminar:

```html
<a href=" url_for('usuarios.eliminar', id=u.id) ">Eliminar</a>
```

Cambialo por un formulario POST con token CSRF:

```html
<form action=" url_for('usuarios.eliminar', id=u.id) " method="post"
      onsubmit="return confirm('Seguro que desea eliminar?');" style="display:inline">
  <input type="hidden" name="csrf_token" value=" csrf_token() ">
  <button type="submit" class="btn btn-danger btn-sm">Eliminar</button>
</form>
```

Aplica lo mismo para `fichas.eliminar`, `programas.eliminar` y `documentos.eliminar_plantilla`.
Asegurate de que TODOS los formularios `POST` incluyan ` csrf_token() `.

---

## 5. Puesta en marcha

```bash
pip install -r requirements.txt
cp .env.example .env        # y edita los valores (SECRET_KEY, DB_PASSWORD, etc.)
mysql -u root -p < database.sql
python crear_admin.py       # crea tu primer administrador de forma segura
python app.py
```
