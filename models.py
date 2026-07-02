import mysql.connector
from mysql.connector import pooling, Error
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_CONFIG


class Database:
    """Clase para manejar la conexion a MySQL con pool de conexiones."""

    _pool = None

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            try:
                cls._pool = pooling.MySQLConnectionPool(**DB_CONFIG)
            except Error as e:
                print(f"Error al crear el pool de conexiones: {e}")
                raise
        return cls._pool

    @classmethod
    def get_connection(cls):
        return cls.get_pool().get_connection()

    @classmethod
    def execute_query(cls, query, params=None, fetch_one=False, fetch_all=False, commit=False):
        """Ejecuta una consulta SQL con manejo automatico de conexion."""
        conn = None
        cursor = None
        try:
            conn = cls.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())

            result = None
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()

            if commit:
                conn.commit()
                result = cursor.lastrowid

            return result
        except Error as e:
            if conn and commit:
                conn.rollback()
            # No exponer detalles internos al usuario; registrarlos en el log del servidor.
            print(f"Error en consulta SQL: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


# ============================================
# FUNCIONES PARA ADMIN (con hashing seguro y roles)
# ============================================

def verificar_admin(username, password):
    """Verifica credenciales del administrador usando hash seguro (Werkzeug).
    Devuelve el admin (sin el hash) solo si esta activo y la clave es correcta."""
    admin = Database.execute_query(
        "SELECT * FROM admin WHERE username = %s", (username,), fetch_one=True
    )
    if not admin:
        return None
    if not admin.get('activo', 1):
        return None
    if not check_password_hash(admin['password'], password):
        return None
    admin.pop('password', None)  # nunca devolver el hash
    return admin


def crear_admin(username, password, nombre_completo, rol='admin'):
    """Crea un administrador con contrasena hasheada."""
    password_hash = generate_password_hash(password)
    query = """
        INSERT INTO admin (username, password, nombre_completo, rol, activo)
        VALUES (%s, %s, %s, %s, 1)
    """
    return Database.execute_query(query, (username, password_hash, nombre_completo, rol), commit=True)


def actualizar_password_admin(admin_id, nuevo_password):
    password_hash = generate_password_hash(nuevo_password)
    return Database.execute_query(
        "UPDATE admin SET password = %s WHERE id = %s",
        (password_hash, admin_id), commit=True
    )


def obtener_admins():
    return Database.execute_query(
        "SELECT id, username, nombre_completo, rol, activo, fecha_creacion FROM admin ORDER BY username",
        fetch_all=True
    )


def set_admin_activo(admin_id, activo):
    return Database.execute_query(
        "UPDATE admin SET activo = %s WHERE id = %s",
        (1 if activo else 0, admin_id), commit=True
    )


# ============================================
# CONTROL DE INTENTOS DE LOGIN (bloqueo temporal)
# ============================================

def registrar_intento_login(username, ip, exito):
    query = """
        INSERT INTO intentos_login (username, ip, exito)
        VALUES (%s, %s, %s)
    """
    return Database.execute_query(query, (username, ip, 1 if exito else 0), commit=True)


def contar_intentos_fallidos(username, ip, minutos):
    """Cuenta intentos fallidos recientes por usuario o IP dentro de una ventana de tiempo."""
    query = """
        SELECT COUNT(*) AS total
        FROM intentos_login
        WHERE exito = 0
          AND (username = %s OR ip = %s)
          AND fecha >= (NOW() - INTERVAL %s MINUTE)
    """
    row = Database.execute_query(query, (username, ip, minutos), fetch_one=True)
    return row['total'] if row else 0


def limpiar_intentos(username, ip):
    """Limpia los intentos tras un login exitoso."""
    return Database.execute_query(
        "DELETE FROM intentos_login WHERE username = %s OR ip = %s",
        (username, ip), commit=True
    )


# ============================================
# AUDITORIA (log_actividades)
# ============================================

def registrar_actividad(admin_username, accion, entidad=None, entidad_id=None, detalle=None, ip=None):
    query = """
        INSERT INTO log_actividades (admin_username, accion, entidad, entidad_id, detalle, ip)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        return Database.execute_query(
            query, (admin_username, accion, entidad, entidad_id, detalle, ip), commit=True
        )
    except Exception as e:
        # La auditoria no debe romper la operacion principal.
        print(f"No se pudo registrar la actividad: {e}")
        return None


def obtener_actividades(limite=200):
    return Database.execute_query(
        "SELECT * FROM log_actividades ORDER BY fecha DESC LIMIT %s",
        (limite,), fetch_all=True
    )


# ============================================
# FUNCIONES PARA PROGRAMAS DE FORMACION
# ============================================

def obtener_programas():
    return Database.execute_query(
        "SELECT * FROM programas_formacion ORDER BY nombre_programa", fetch_all=True
    )


def obtener_programa(id):
    return Database.execute_query(
        "SELECT * FROM programas_formacion WHERE id = %s", (id,), fetch_one=True
    )


def crear_programa(nombre_programa, descripcion):
    query = "INSERT INTO programas_formacion (nombre_programa, descripcion) VALUES (%s, %s)"
    return Database.execute_query(query, (nombre_programa, descripcion), commit=True)


def actualizar_programa(id, nombre_programa, descripcion):
    query = "UPDATE programas_formacion SET nombre_programa = %s, descripcion = %s WHERE id = %s"
    return Database.execute_query(query, (nombre_programa, descripcion, id), commit=True)


def eliminar_programa(id):
    return Database.execute_query(
        "DELETE FROM programas_formacion WHERE id = %s", (id,), commit=True
    )


# ============================================
# FUNCIONES PARA FICHAS
# ============================================

def obtener_fichas():
    query = """
        SELECT f.*, p.nombre_programa,
               COUNT(u.id) AS total_aprendices
        FROM fichas f
        LEFT JOIN programas_formacion p ON f.programa_id = p.id
        LEFT JOIN usuarios u ON u.ficha_id = f.id
        GROUP BY f.id, p.nombre_programa
        ORDER BY f.numero_ficha
    """
    return Database.execute_query(query, fetch_all=True)


def obtener_ficha(id):
    query = """
        SELECT f.*, p.nombre_programa
        FROM fichas f
        LEFT JOIN programas_formacion p ON f.programa_id = p.id
        WHERE f.id = %s
    """
    return Database.execute_query(query, (id,), fetch_one=True)


def obtener_fichas_por_programa(programa_id):
    query = "SELECT * FROM fichas WHERE programa_id = %s ORDER BY numero_ficha"
    return Database.execute_query(query, (programa_id,), fetch_all=True)


def crear_ficha(numero_ficha, programa_id, fecha_inicio, fecha_fin, estado):
    query = """
        INSERT INTO fichas (numero_ficha, programa_id, fecha_inicio, fecha_fin, estado)
        VALUES (%s, %s, %s, %s, %s)
    """
    return Database.execute_query(
        query, (numero_ficha, programa_id, fecha_inicio, fecha_fin, estado), commit=True
    )


def actualizar_ficha(id, numero_ficha, programa_id, fecha_inicio, fecha_fin, estado):
    query = """
        UPDATE fichas SET numero_ficha = %s, programa_id = %s,
               fecha_inicio = %s, fecha_fin = %s, estado = %s
        WHERE id = %s
    """
    return Database.execute_query(
        query, (numero_ficha, programa_id, fecha_inicio, fecha_fin, estado, id), commit=True
    )


def eliminar_ficha(id):
    return Database.execute_query("DELETE FROM fichas WHERE id = %s", (id,), commit=True)


# ============================================
# FUNCIONES PARA USUARIOS (APRENDICES) - con paginacion
# ============================================

_SELECT_USUARIO = """
    SELECT u.*, f.numero_ficha, p.nombre_programa
    FROM usuarios u
    LEFT JOIN fichas f ON u.ficha_id = f.id
    LEFT JOIN programas_formacion p ON u.programa_id = p.id
"""


def obtener_usuarios():
    return Database.execute_query(
        _SELECT_USUARIO + " ORDER BY u.fecha_registro DESC", fetch_all=True
    )


def contar_usuarios(buscar=None):
    if buscar:
        like = f"%{buscar}%"
        row = Database.execute_query(
            """SELECT COUNT(*) AS total FROM usuarios
               WHERE nombre LIKE %s OR apellidos LIKE %s OR identificacion LIKE %s""",
            (like, like, like), fetch_one=True
        )
    else:
        row = Database.execute_query("SELECT COUNT(*) AS total FROM usuarios", fetch_one=True)
    return row['total'] if row else 0


def obtener_usuarios_paginado(page=1, per_page=10, buscar=None):
    """Devuelve una pagina de aprendices. Usa LIMIT/OFFSET con parametros seguros."""
    page = max(int(page), 1)
    per_page = max(int(per_page), 1)
    offset = (page - 1) * per_page

    if buscar:
        like = f"%{buscar}%"
        query = _SELECT_USUARIO + """
            WHERE u.nombre LIKE %s OR u.apellidos LIKE %s OR u.identificacion LIKE %s
            ORDER BY u.fecha_registro DESC
            LIMIT %s OFFSET %s
        """
        params = (like, like, like, per_page, offset)
    else:
        query = _SELECT_USUARIO + " ORDER BY u.fecha_registro DESC LIMIT %s OFFSET %s"
        params = (per_page, offset)

    return Database.execute_query(query, params, fetch_all=True)


def obtener_usuario(id):
    return Database.execute_query(_SELECT_USUARIO + " WHERE u.id = %s", (id,), fetch_one=True)


def obtener_usuarios_por_ficha(ficha_id):
    query = _SELECT_USUARIO + " WHERE u.ficha_id = %s ORDER BY u.apellidos, u.nombre"
    return Database.execute_query(query, (ficha_id,), fetch_all=True)


def obtener_usuarios_por_programa(programa_id):
    query = _SELECT_USUARIO + " WHERE u.programa_id = %s ORDER BY u.apellidos, u.nombre"
    return Database.execute_query(query, (programa_id,), fetch_all=True)


def crear_usuario(tipo_documento, identificacion, nombre, apellidos, telefono,
                  correo_institucional, correo_personal, direccion_residencia,
                  ficha_id, programa_id, firma_imagen):
    query = """
        INSERT INTO usuarios
        (tipo_documento, identificacion, nombre, apellidos, telefono,
         correo_institucional, correo_personal, direccion_residencia,
         ficha_id, programa_id, firma_imagen)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    return Database.execute_query(query, (
        tipo_documento, identificacion, nombre, apellidos, telefono,
        correo_institucional, correo_personal, direccion_residencia,
        ficha_id, programa_id, firma_imagen
    ), commit=True)


def actualizar_usuario(id, tipo_documento, identificacion, nombre, apellidos, telefono,
                       correo_institucional, correo_personal, direccion_residencia,
                       ficha_id, programa_id, firma_imagen=None):
    if firma_imagen is not None:
        query = """
            UPDATE usuarios SET
                tipo_documento = %s, identificacion = %s, nombre = %s, apellidos = %s,
                telefono = %s, correo_institucional = %s, correo_personal = %s,
                direccion_residencia = %s, ficha_id = %s, programa_id = %s, firma_imagen = %s
            WHERE id = %s
        """
        params = (tipo_documento, identificacion, nombre, apellidos, telefono,
                  correo_institucional, correo_personal, direccion_residencia,
                  ficha_id, programa_id, firma_imagen, id)
    else:
        query = """
            UPDATE usuarios SET
                tipo_documento = %s, identificacion = %s, nombre = %s, apellidos = %s,
                telefono = %s, correo_institucional = %s, correo_personal = %s,
                direccion_residencia = %s, ficha_id = %s, programa_id = %s
            WHERE id = %s
        """
        params = (tipo_documento, identificacion, nombre, apellidos, telefono,
                  correo_institucional, correo_personal, direccion_residencia,
                  ficha_id, programa_id, id)

    return Database.execute_query(query, params, commit=True)


def eliminar_usuario(id):
    return Database.execute_query("DELETE FROM usuarios WHERE id = %s", (id,), commit=True)


# ============================================
# FUNCIONES PARA PLANTILLAS
# ============================================

def obtener_plantillas():
    return Database.execute_query("SELECT * FROM plantillas ORDER BY fecha_subida DESC", fetch_all=True)


def obtener_plantilla(id):
    return Database.execute_query("SELECT * FROM plantillas WHERE id = %s", (id,), fetch_one=True)


def crear_plantilla(nombre, archivo, descripcion):
    query = "INSERT INTO plantillas (nombre, archivo, descripcion) VALUES (%s, %s, %s)"
    return Database.execute_query(query, (nombre, archivo, descripcion), commit=True)


def eliminar_plantilla(id):
    return Database.execute_query("DELETE FROM plantillas WHERE id = %s", (id,), commit=True)


# ============================================
# FUNCIONES DE ESTADISTICAS
# ============================================

def obtener_estadisticas():
    stats = {}
    stats['total_usuarios'] = Database.execute_query(
        "SELECT COUNT(*) as total FROM usuarios", fetch_one=True
    )['total']
    stats['total_fichas'] = Database.execute_query(
        "SELECT COUNT(*) as total FROM fichas", fetch_one=True
    )['total']
    stats['total_programas'] = Database.execute_query(
        "SELECT COUNT(*) as total FROM programas_formacion", fetch_one=True
    )['total']
    stats['fichas_activas'] = Database.execute_query(
        "SELECT COUNT(*) as total FROM fichas WHERE estado = 'Activa'", fetch_one=True
    )['total']
    stats['ultimos_usuarios'] = Database.execute_query(
        _SELECT_USUARIO + " ORDER BY u.fecha_registro DESC LIMIT 5", fetch_all=True
    )
    return stats
