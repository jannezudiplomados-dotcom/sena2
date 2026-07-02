from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from models import (obtener_programas, obtener_programa, crear_programa,
                    actualizar_programa, eliminar_programa, registrar_actividad)

programas_bp = Blueprint('programas', __name__, url_prefix='/programas')


@programas_bp.route('/')
@login_required
def listar():
    programas = obtener_programas()
    return render_template('programas/listar.html', programas=programas)


@programas_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    if request.method == 'POST':
        nombre = request.form.get('nombre_programa', '').strip()
        descripcion = request.form.get('descripcion', '').strip()

        if not nombre:
            flash('El nombre del programa es obligatorio.', 'danger')
            return render_template('programas/crear.html')

        try:
            nuevo_id = crear_programa(nombre, descripcion)
            registrar_actividad(session_user(), 'crear', 'programa', nuevo_id, nombre, request.remote_addr)
            flash('Programa de formacion creado exitosamente.', 'success')
            return redirect(url_for('programas.listar'))
        except Exception:
            flash('Ocurrio un error al crear el programa.', 'danger')

    return render_template('programas/crear.html')


@programas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    programa = obtener_programa(id)
    if not programa:
        flash('Programa no encontrado.', 'danger')
        return redirect(url_for('programas.listar'))

    if request.method == 'POST':
        nombre = request.form.get('nombre_programa', '').strip()
        descripcion = request.form.get('descripcion', '').strip()

        if not nombre:
            flash('El nombre del programa es obligatorio.', 'danger')
            return render_template('programas/editar.html', programa=programa)

        try:
            actualizar_programa(id, nombre, descripcion)
            registrar_actividad(session_user(), 'editar', 'programa', id, nombre, request.remote_addr)
            flash('Programa actualizado exitosamente.', 'success')
            return redirect(url_for('programas.listar'))
        except Exception:
            flash('Ocurrio un error al actualizar el programa.', 'danger')

    return render_template('programas/editar.html', programa=programa)


@programas_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    try:
        eliminar_programa(id)
        registrar_actividad(session_user(), 'eliminar', 'programa', id, None, request.remote_addr)
        flash('Programa eliminado exitosamente.', 'success')
    except Exception:
        flash('No se pudo eliminar (puede tener fichas asociadas).', 'danger')

    return redirect(url_for('programas.listar'))


def session_user():
    from flask import session
    return session.get('admin')
