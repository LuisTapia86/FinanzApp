# config.py - Configuración de la aplicación
import os

class Config:
    """Configuración central de la aplicación"""

    # Base de datos
    DATABASE_NAME = 'finanzas.db'
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True

    # Autenticación
    SKIP_LOGIN = True  # Cambiar a False en producción para activar login
    DEFAULT_USER_ID = 1  # Usuario por defecto cuando SKIP_LOGIN = True

    # Límites de proyección
    PROYECCION_MESES_DEFAULT = 6

    # Fecha indefinida por defecto
    FECHA_INDEFINIDA = '2099-12-31'

    # Umbrales del semáforo financiero (basado en porcentaje del balance actual)
    # NOTA: Los umbrales ahora se calculan dinámicamente en proyeccion.py
    # Verde: Saldo >= 30% del balance actual
    # Amarillo: Saldo entre 5% y 29% del balance actual
    # Rojo: Saldo < 5% del balance actual
    UMBRAL_VERDE = 5000   # (Deprecado - se mantiene para compatibilidad)
    UMBRAL_AMARILLO = 1000  # (Deprecado - se mantiene para compatibilidad)
