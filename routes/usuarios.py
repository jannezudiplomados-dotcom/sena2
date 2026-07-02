import os
import base64
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from routes.auth import login_required
from models import (obtener_usuario, crear_usuario, actualizar_usuario, eliminar_usuario,
                    obtener_fichas, obtener_programas, registrar_actividad,
                    obtener_usuarios_paginado, contar_usuarios)
from config import FIRMAS_FOLDER, PER_PAGE

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

EXTENSIONES_FIRMA = {'png', 'jpg', 'jpeg'}


def _guardar_firma(identificacion, firma_archivo, firma_data):
    """Guarda la firma (archivo subido o dibujo base64) de forma segura.
    Devuelve el nombre de archivo guardado o cadena vacia."""
    ident_seguro = secure_filename(str(identificacion)) or 'aprendiz'
    ts = datetime.now().strftime('%Y%m%d%H%M%S')

    if firma_archivo and firma_archivo.filename:
        filename = secure_filename(firma_archivo.filename)
        ext = os.path.splitext(filename)[1].lower().lstrip('.')
        if ext not in EXTENSIONES_FIRMA:
            raise ValueError('Formato de firma no permitido (use PNG o JPG).')
        nombre_archivo = f"firma_{ident_seguro}_{ts}.{ext}"
        ruta = os.path.join(FIRMAS_FOLDER, nombre_archivo)
        firma_archivo.save(ruta)
        return nombre_archivo

    if firma_data and ',' in firma_data:
        firma_base64 = firma_data.split(',', 1)[1]
    contenido = base64.b64decode(firma_base64)
    # Validar que realmente sea una imagen (PNG o JPEG) por su firma de bytes
    _png = bytes.fromhex('89504e470d0a1a0a')
    _jpg = bytes.fromhex('ffd8ff')
    if not (contenido.startswith(_png) or contenido.startswith(_jpg)):
        raise ValueError('La firma dibujada no es una imagen valida.')
    nombre_archivo = f"firma_{ident_seguro}_{ts}.png"
    ruta = os.path.join(FIRMAS_FOLDER, nombre_archivo)
    with open(ruta, 'wb') as f:
        f.write(contenido)
    return nombre_archivo

    return ''


def _eliminar_firma_antigua(nombre_firma):
    if not nombre_firma:
        return
    ruta = os.path.join(FIRMAS_FOLDER, secure_filename(nombre_firma))
    if os.path.exists(ruta):
        try:
            os.remove(ruta)
        except OSError:
            pass


@usuarios_bp.route('/')
@login_required
def listar():
    page = request.args.get('page', 1, type=int)
    buscar = request.args.get('q', '', type=str).strip() or None
    usuarios = obtener_usuarios_paginado(page=page, per_page=PER_PAGE, buscar=buscar)
    total = contar_usuarios(buscar=buscar)
    total_paginas = max((total + PER_PAGE - 1) // PER_PAGE, 1)
    return render_template('usuarios/listar.html', usuarios=usuarios,
                           page=page, total_paginas=total_paginas,
                           total=total, buscar=buscar or '')


@usuarios_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    fichas = obtener_fichas()
    programas = obtener_programas()

    if request.method == 'POST':
        tipo_documento = request.form.get('tipo_documento', 'CC').strip()
        identificacion = request.form.get('identificacion', '').strip()
        nombre = request.form.get('nombre', '').strip()
        apellidos = request.form.get('apellidos', '').strip()
        telefono = request.form.get('telefono', '').strip()
        correo_institucional = request.form.get('correo_institucional', '').strip()
        correo_personal = request.form.get('correo_personal', '').strip()
        direccion_residencia = request.form.get('direccion_residencia', '').strip()
        ficha_id = request.form.get('ficha_id', '')
        programa_id = request.form.get('programa_id', '')
        firma_data = request.form.get('firma', '')

        if not identificacion or not nombre or not apellidos:
            flash('Los campos Identificacion, Nombre y Apellidos son obligatorios.', 'danger')
            return render_template('usuarios/crear.html', fichas=fichas, programas=programas)

        try:
            nombre_archivo = _guardar_firma(identificacion, request.files.get('firma_archivo'), firma_data)
        except ValueError as e:
            flash(str(e), 'warning')
            nombre_archivo = ''

        ficha_id = int(ficha_id) if ficha_id else None
        programa_id = int(programa_id) if programa_id else None

        try:
            nuevo_id = crear_usuario(tipo_documento, identificacion, nombre, apellidos, telefono,
                                     correo_institucional, correo_personal, direccion_residencia,
                                     ficha_id, programa_id, nombre_archivo)
            registrar_actividad(session.get('admin'), 'crear', 'usuario', nuevo_id,
                                f"{nombre} {apellidos} ({identificacion})", request.remote_addr)
            flash('Aprendiz registrado exitosamente.', 'success')
            return redirect(url_for('usuarios.listar'))
        except Exception:
            flash('Ocurrio un error al registrar el aprendiz.', 'danger')

    return render_template('usuarios/crear.html', fichas=fichas, programas=programas)


@usuarios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    usuario = obtener_usuario(id)
    if not usuario:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('usuarios.listar'))

    fichas = obtener_fichas()
    programas = obtener_programas()

    if request.method == 'POST':
        tipo_documento = request.form.get('tipo_documento', 'CC').strip()
        identificacion = request.form.get('identificacion', '').strip()
        nombre = request.form.get('nombre', '').strip()
        apellidos = request.form.get('apellidos', '').strip()
        telefono = request.form.get('telefono', '').strip()
        correo_institucional = request.form.get('correo_institucional', '').strip()
        correo_personal = request.form.get('correo_personal', '').strip()
        direccion_residencia = request.form.get('direccion_residencia', '').strip()
        ficha_id = request.form.get('ficha_id', '')
        programa_id = request.form.get('programa_id', '')
        firma_data = request.form.get('firma', '')

        if not identificacion or not nombre or not apellidos:
            flash('Los campos Identificacion, Nombre y Apellidos son obligatorios.', 'danger')
            return render_template('usuarios/editar.html', usuario=usuario, fichas=fichas, programas=programas)

        ficha_id = int(ficha_id) if ficha_id else None
        programa_id = int(programa_id) if programa_id else None

        try:
            nombre_archivo = _guardar_firma(identificacion, request.files.get('firma_archivo'), firma_data)
            nombre_archivo = nombre_archivo or None
        except ValueError as e:
            flash(str(e), 'warning')
            nombre_archivo = None

        # Si hay firma nueva, borrar la anterior para no dejar huerfanos
        if nombre_archivo and usuario.get('firma_imagen'):
            _eliminar_firma_antigua(usuario['firma_imagen'])

        try:
            actualizar_usuario(id, tipo_documento, identificacion, nombre, apellidos, telefono,
                               correo_institucional, correo_personal, direccion_residencia,
                               ficha_id, programa_id, nombre_archivo)
            registrar_actividad(session.get('admin'), 'editar', 'usuario', id,
                                f"{nombre} {apellidos} ({identificacion})", request.remote_addr)
            flash('Aprendiz actualizado exitosamente.', 'success')
            return redirect(url_for('usuarios.listar'))
        except Exception:
            flash('Ocurrio un error al actualizar el aprendiz.', 'danger')

    return render_template('usuarios/editar.html', usuario=usuario, fichas=fichas, programas=programas)


@usuarios_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    try:
        usuario = obtener_usuario(id)
        if usuario and usuario.get('firma_imagen'):
            _eliminar_firma_antigua(usuario['firma_imagen'])

        eliminar_usuario(id)
        registrar_actividad(session.get('admin'), 'eliminar', 'usuario', id, None, request.remote_addr)
        flash('Aprendiz eliminado exitosamente.', 'success')
    except Exception:
        flash('Ocurrio un error al eliminar el aprendiz.', 'danger')

    return redirect(url_for('usuarios.listar'))
