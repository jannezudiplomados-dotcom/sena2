from flask import Blueprint, render_template
from routes.auth import login_required
from models import obtener_estadisticas

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    stats = obtener_estadisticas()
    return render_template('dashboard.html', stats=stats)
