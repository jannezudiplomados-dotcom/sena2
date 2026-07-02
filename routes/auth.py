from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from models import (verificar_admin, registrar_intento_login,
                    contar_intentos_fallidos, limpiar_intentos, registrar_actividad)
from config import MAX_LOGIN_ATTEMPTS, LOCKOUT_MINUTES

auth_bp = Blueprint('auth', __name__)


def _client_ip():
    """Obtiene la IP real del cliente (considerando proxy inverso)."""
    fwd = request.headers.get('X-Forwarded-For', '')
    if fwd:
        return fwd.split(',')[0].strip()
    return request.remote_addr or 'desconocida'


def login_required(f):
    """Decorador para proteger rutas que requieren autenticacion."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            flash('Debe iniciar sesion para acceder.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Decorador para exigir uno o varios roles (por ejemplo 'superadmin')."""
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'admin' not in session:
                flash('Debe iniciar sesion para acceder.', 'warning')
                return redirect(url_for('auth.login'))
            if session.get('admin_rol') not in roles:
                flash('No tiene permisos para realizar esta accion.', 'danger')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper


@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'admin' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        ip = _client_ip()

        if not username or not password:
            flash('Por favor complete todos los campos.', 'danger')
            return render_template('login.html')

        # Bloqueo por intentos fallidos recientes
        fallidos = contar_intentos_fallidos(username, ip, LOCKOUT_MINUTES)
        if fallidos >= MAX_LOGIN_ATTEMPTS:
            flash(
                f'Demasiados intentos fallidos. Intente de nuevo en {LOCKOUT_MINUTES} minutos.',
                'danger'
            )
            return render_template('login.html')

        admin = verificar_admin(username, password)

        if admin:
            registrar_intento_login(username, ip, exito=True)
            limpiar_intentos(username, ip)

            session.clear()
            session['admin'] = admin['username']
            session['admin_nombre'] = admin.get('nombre_completo', admin['username'])
            session['admin_rol'] = admin.get('rol', 'admin')
            session.permanent = False

            registrar_actividad(admin['username'], 'login', 'admin', admin.get('id'),
                                'Inicio de sesion', ip)
            flash(f'Bienvenido, {session["admin_nombre"]}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            registrar_intento_login(username, ip, exito=False)
            restantes = max(MAX_LOGIN_ATTEMPTS - (fallidos + 1), 0)
            if restantes > 0:
                flash(f'Usuario o contrasena incorrectos. Intentos restantes: {restantes}.', 'danger')
            else:
                flash('Usuario o contrasena incorrectos. Cuenta bloqueada temporalmente.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    admin = session.get('admin')
    registrar_actividad(admin, 'logout', 'admin', None, 'Cierre de sesion', _client_ip())
    session.clear()
    flash('Sesion cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))
