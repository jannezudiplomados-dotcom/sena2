import os
from dotenv import load_dotenv

# Carga variables desde el archivo .env (si existe)
load_dotenv()

# ============================================
# CONFIGURACION DEL SISTEMA (basada en variables de entorno)
# ============================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ---- Base de datos ----
# NUNCA quemes credenciales en el codigo. Se leen del entorno / .env
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'sena_app'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'gestion_fichas'),
    'charset': 'utf8mb4',
    'autocommit': False,
    'pool_name': 'sena_pool',
    'pool_size': int(os.environ.get('DB_POOL_SIZE', '5')),
    'pool_reset_session': True,
}

# ---- Flask ----
# SECRET_KEY obligatoria y SIN valor por defecto (si falta, la app no arranca)
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError(
        'SECRET_KEY no esta definida. Copia .env.example a .env y define un valor seguro '
        "(por ejemplo: python -c \"import secrets; print(secrets.token_hex(32))\")."
    )

# ---- Seguridad de inicio de sesion ----
MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', '5'))
LOCKOUT_MINUTES = int(os.environ.get('LOCKOUT_MINUTES', '15'))

# ---- Paginacion ----
PER_PAGE = int(os.environ.get('PER_PAGE', '10'))

# ---- Carpetas de Upload ----
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
FIRMAS_FOLDER = os.path.join(BASE_DIR, 'static', 'firmas')
PLANTILLAS_FOLDER = os.path.join(UPLOAD_FOLDER, 'plantillas')
GENERADOS_FOLDER = os.path.join(UPLOAD_FOLDER, 'generados')

# ---- Extensiones permitidas ----
ALLOWED_EXTENSIONS = {'docx', 'xlsx', 'xls'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max

# Crear carpetas si no existen
for folder in [UPLOAD_FOLDER, FIRMAS_FOLDER, PLANTILLAS_FOLDER, GENERADOS_FOLDER]:
    os.makedirs(folder, exist_ok=True)
