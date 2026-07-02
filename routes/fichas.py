from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from routes.auth import login_required
from models import (obtener_fichas, obtener_ficha, crear_ficha,
                    actualizar_ficha, eliminar_ficha,
                    obtener_programas, obtener_fichas_por_programa, registrar_actividad)

fichas_bp = Blueprint('fichas', __name__, url_prefix='/fichas')


@fichas_bp.route('/')
@login_required
def listar():
    fichas = obtener_fichas()
    return render_template('fichas/listar.html', fichas=fichas)


@fichas_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    programas = obtener_programas()

    if request.method == 'POST':
        numero_ficha = request.form.get('numero_ficha', '').strip()
        programa_id = request.form.get('programa_id', '')
        fecha_inicio = request.form.get('fecha_inicio', '') or None
        fecha_fin = request.form.get('fecha_fin', '') or None
        estado = request.form.get('estado', 'Activa').strip()

        if not numero_ficha:
            flash('El numero de ficha es obligatorio.', 'danger')
            return render_template('fichas/crear.html', programas=programas)

        programa_id = int(programa_id) if programa_id else None

        try:
            nuevo_id = crear_ficha(numero_ficha, programa_id, fecha_inicio, fecha_fin, estado)
            registrar_actividad(session.get('admin'), 'crear', 'ficha', nuevo_id, numero_ficha, request.remote_addr)
            flash('Ficha creada exitosamente.', 'success')
            return redirect(url_for('fichas.listar'))
        except Exception:
            flash('Ocurrio un error al crear la ficha.', 'danger')

    return render_template('fichas/crear.html', programas=programas)


@fichas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    ficha = obtener_ficha(id)
    if not ficha:
        flash('Ficha no encontrada.', 'danger')
        return redirect(url_for('fichas.listar'))

    programas = obtener_programas()

    if request.method == 'POST':
        numero_ficha = request.form.get('numero_ficha', '').strip()
        programa_id = request.form.get('programa_id', '')
        fecha_inicio = request.form.get('fecha_inicio', '') or None
        fecha_fin = request.form.get('fecha_fin', '') or None
        estado = request.form.get('estado', 'Activa').strip()

        if not numero_ficha:
            flash('El numero de ficha es obligatorio.', 'danger')
            return render_template('fichas/editar.html', ficha=ficha, programas=programas)

        programa_id = int(programa_id) if programa_id else None

        try:
            actualizar_ficha(id, numero_ficha, programa_id, fecha_inicio, fecha_fin, estado)
            registrar_actividad(session.get('admin'), 'editar', 'ficha', id, numero_ficha, request.remote_addr)
            flash('Ficha actualizada exitosamente.', 'success')
            return redirect(url_for('fichas.listar'))
        except Exception:
            flash('Ocurrio un error al actualizar la ficha.', 'danger')

    return render_template('fichas/editar.html', ficha=ficha, programas=programas)


@fichas_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    try:
        eliminar_ficha(id)
        registrar_actividad(session.get('admin'), 'eliminar', 'ficha', id, None, request.remote_addr)
        flash('Ficha eliminada exitosamente.', 'success')
    except Exception:
        flash('No se pudo eliminar (puede tener aprendices asociados).', 'danger')

    return redirect(url_for('fichas.listar'))


@fichas_bp.route('/api/por_programa/<int:programa_id>')
@login_required
def api_fichas_por_programa(programa_id):
    """API para obtener fichas de un programa (filtro dinamico)."""
    fichas = obtener_fichas_por_programa(programa_id)
    return jsonify([{'id': f['id'], 'numero_ficha': f['numero_ficha']} for f in fichas])
