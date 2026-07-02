import os
from datetime import datetime
from flask import Flask, render_template, session
from flask_wtf.csrf import CSRFProtect
from config import SECRET_KEY, MAX_CONTENT_LENGTH

# ============================================
# INICIALIZACION DE LA APLICACION
# ============================================

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Endurecer las cookies de sesion
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    # Activa SESSION_COOKIE_SECURE=1 en produccion (HTTPS)
    SESSION_COOKIE_SECURE=os.environ.get('SESSION_COOKIE_SECURE', '0') == '1',
)

# Proteccion CSRF (global)
csrf = CSRFProtect(app)

# ============================================
# REGISTRO DE BLUEPRINTS
# ============================================

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.usuarios import usuarios_bp
from routes.programas import programas_bp
from routes.fichas import fichas_bp
from routes.documentos import documentos_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(programas_bp)
app.register_blueprint(fichas_bp)
app.register_blueprint(documentos_bp)

# ============================================
# CONTEXT PROCESSOR - Variables globales para templates
# ============================================

@app.context_processor
def inject_globals():
    return {
        'app_name': 'Gestion de Fichas SENA',
        'current_year': datetime.now().year,
        'admin_nombre': session.get('admin_nombre', 'Admin'),
        'admin_rol': session.get('admin_rol', 'admin'),
    }

# ============================================
# MANEJO DE ERRORES
# ============================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

@app.errorhandler(413)
def file_too_large(e):
    return render_template('errors/413.html'), 413

# ============================================
# EJECUTAR
# ============================================

if __name__ == '__main__':
    from config import UPLOAD_FOLDER, FIRMAS_FOLDER, PLANTILLAS_FOLDER, GENERADOS_FOLDER
    for folder in [FIRMAS_FOLDER, PLANTILLAS_FOLDER, GENERADOS_FOLDER]:
        os.makedirs(folder, exist_ok=True)

    # El modo debug se controla por entorno. NUNCA uses debug=True en produccion.
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', '5000'))

    print('=' * 50)
    print(' SISTEMA DE GESTION DE FICHAS SENA')
    print(f' http://{host}:{port}')
    print(' (En produccion usa un servidor WSGI como waitress o gunicorn)')
    print('=' * 50)

    app.run(debug=debug, host=host, port=port)
