# routes/__init__.py
from flask import Blueprint

# Crear blueprints para cada módulo
ingresos_bp = Blueprint('ingresos', __name__)
gastos_bp = Blueprint('gastos', __name__)
creditos_bp = Blueprint('creditos', __name__)
msi_bp = Blueprint('msi', __name__)
dashboard_bp = Blueprint('dashboard', __name__)
config_bp = Blueprint('configuracion', __name__)
reportes_bp = Blueprint('reportes', __name__)
prestamos_bp = Blueprint('prestamos', __name__)
tarjetas_bp = Blueprint('tarjetas', __name__)
api_bp = Blueprint('api', __name__)

# Importar las rutas (esto debe ir después de crear los blueprints)
from . import ingresos, gastos, creditos, msi, dashboard, configuracion, reportes, prestamos, tarjetas, api

__all__ = ['ingresos_bp', 'gastos_bp', 'creditos_bp', 'msi_bp', 'dashboard_bp', 'config_bp', 'reportes_bp', 'prestamos_bp', 'tarjetas_bp', 'api_bp']
