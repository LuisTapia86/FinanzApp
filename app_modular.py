# app_modular.py - Aplicación Flask modular con manejo de errores robusto
from flask import Flask, render_template, flash, get_flashed_messages
import sys
import os

# Agregar el directorio actual al path de Python
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from database import init_db, get_db_connection
from utils import parse_fecha, calcular_estado_semaforo
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Importar blueprints
from routes import ingresos_bp

app = Flask(__name__)
app.config.from_object(Config)

# Registrar blueprints
app.register_blueprint(ingresos_bp)

# Configurar mensaje flash secreto
app.secret_key = Config.SECRET_KEY


@app.errorhandler(404)
def not_found(e):
    """Manejar errores 404"""
    flash('Página no encontrada', 'error')
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """Manejar errores 500"""
    flash(f'Error interno del servidor: {str(e)}', 'error')
    print(f"❌ Error 500: {str(e)}")
    return render_template('index.html'), 500


@app.errorhandler(Exception)
def handle_exception(e):
    """Manejar todas las excepciones no capturadas"""
    flash(f'Error inesperado: {str(e)}', 'error')
    print(f"❌ Excepción no capturada: {str(e)}")
    import traceback
    traceback.print_exc()
    return render_template('index.html'), 500


def obtener_proximas_alertas(dias_adelante=15):
    """Obtener próximas alertas de pagos"""
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # Obtener créditos activos con alertas
        c.execute('''SELECT id, nombre, monto_mensual, fecha_limite_pago, dias_alerta, notas
                     FROM creditos_programados WHERE activo=1''')
        creditos = c.fetchall()

        # Obtener MSI activos
        c.execute('''SELECT id, producto, mensualidad, dia_pago, dias_alerta
                     FROM compras_msi WHERE activo=1 AND meses_restantes > 0''')
        msis = c.fetchall()

        conn.close()

        alertas = []
        hoy = datetime.now()

        # Procesar créditos
        for cred in creditos:
            dia_limite = cred['fecha_limite_pago'] if cred['fecha_limite_pago'] else cred['dia_pago']
            dias_alerta = cred['dias_alerta'] or 3

            # Calcular próxima fecha de pago (este mes o siguiente)
            for mes_offset in range(3):  # Revisar próximos 3 meses
                fecha_pago = hoy + relativedelta(months=mes_offset)
                try:
                    fecha_pago = datetime(fecha_pago.year, fecha_pago.month, dia_limite)
                except ValueError:
                    # Si el día no existe en ese mes (ej: 31 en febrero), usar último día
                    fecha_pago = datetime(fecha_pago.year, fecha_pago.month, 1) + relativedelta(months=1, days=-1)

                dias_para_pago = (fecha_pago - hoy).days

                if 0 <= dias_para_pago <= dias_adelante:
                    urgencia = "urgente" if dias_para_pago <= 2 else "proximo" if dias_para_pago <= 5 else "programado"

                    alertas.append({
                        'tipo': 'credito',
                        'nombre': cred['nombre'],
                        'monto': cred['monto_mensual'],
                        'fecha_pago': fecha_pago,
                        'dias_restantes': dias_para_pago,
                        'urgencia': urgencia,
                        'notas': cred['notas'] or ''
                    })
                    break

        # Procesar MSI
        for msi in msis:
            dia_pago = msi['dia_pago'] if msi['dia_pago'] else 15
            dias_alerta = msi['dias_alerta'] or 3

            for mes_offset in range(3):
                fecha_pago = hoy + relativedelta(months=mes_offset)
                try:
                    fecha_pago = datetime(fecha_pago.year, fecha_pago.month, dia_pago)
                except ValueError:
                    fecha_pago = datetime(fecha_pago.year, fecha_pago.month, 1) + relativedelta(months=1, days=-1)

                dias_para_pago = (fecha_pago - hoy).days

                if 0 <= dias_para_pago <= dias_adelante:
                    urgencia = "urgente" if dias_para_pago <= 2 else "proximo" if dias_para_pago <= 5 else "programado"

                    alertas.append({
                        'tipo': 'msi',
                        'nombre': msi['producto'],
                        'monto': msi['mensualidad'],
                        'fecha_pago': fecha_pago,
                        'dias_restantes': dias_para_pago,
                        'urgencia': urgencia,
                        'notas': ''
                    })
                    break

        # Ordenar por fecha más próxima
        alertas.sort(key=lambda x: x['dias_restantes'])

        return alertas

    except Exception as e:
        print(f"❌ Error al obtener alertas: {str(e)}")
        return []


def calcular_proyeccion_meses(meses_adelante=6):
    """Calcular proyección de saldo para los próximos X meses"""
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # Obtener balance inicial
        try:
            c.execute("SELECT valor FROM configuracion WHERE clave='balance_inicial'")
            result = c.fetchone()
            saldo_actual = float(result['valor']) if result else 0.0
        except:
            saldo_actual = 0.0

        # Obtener ingresos y gastos ya registrados
        c.execute('SELECT SUM(monto) FROM ingresos')
        total_ingresos = c.fetchone()[0] or 0

        c.execute('SELECT SUM(monto) FROM gastos')
        total_gastos = c.fetchone()[0] or 0

        # Aplicar ingresos y gastos históricos al saldo
        saldo_actual = saldo_actual + total_ingresos - total_gastos

        # Obtener créditos programados activos con fechas
        c.execute('SELECT nombre, monto_mensual, dia_pago, fecha_inicio, fecha_fin FROM creditos_programados WHERE activo=1')
        creditos = c.fetchall()

        # Obtener compras MSI activas
        c.execute('SELECT producto, mensualidad, meses_restantes, fecha_primera_mensualidad FROM compras_msi WHERE activo=1 AND meses_restantes > 0')
        msis = c.fetchall()

        # Obtener ingresos recurrentes activos con fechas
        c.execute('SELECT nombre, monto, dia_pago, fecha_inicio, fecha_fin FROM ingresos_recurrentes WHERE activo=1')
        ingresos_rec = c.fetchall()

        conn.close()

        # Proyectar próximos meses
        proyeccion = []
        fecha_actual = datetime.now()

        for i in range(meses_adelante):
            mes_futuro = fecha_actual + relativedelta(months=i)
            mes_nombre = mes_futuro.strftime('%B %Y')

            # Para comparación, usar solo año-mes (ignorar día)
            mes_futuro_comparacion = datetime(mes_futuro.year, mes_futuro.month, 1)

            # Calcular INGRESOS del mes (solo si están activos en ese mes)
            ingresos_mes = 0
            for ing in ingresos_rec:
                fecha_inicio = parse_fecha(ing['fecha_inicio'])
                fecha_inicio_mes = datetime(fecha_inicio.year, fecha_inicio.month, 1)

                fecha_fin = parse_fecha(ing['fecha_fin'])
                fecha_fin_mes = datetime(fecha_fin.year, fecha_fin.month, 1)

                # Solo aplicar si el mes está dentro del rango
                if fecha_inicio_mes <= mes_futuro_comparacion <= fecha_fin_mes:
                    ingresos_mes += ing['monto']

            # Calcular GASTOS del mes (solo créditos activos en ese mes)
            pago_creditos = 0
            for cred in creditos:
                fecha_inicio = parse_fecha(cred['fecha_inicio'])
                fecha_inicio_mes = datetime(fecha_inicio.year, fecha_inicio.month, 1)

                fecha_fin = parse_fecha(cred['fecha_fin'])
                fecha_fin_mes = datetime(fecha_fin.year, fecha_fin.month, 1)

                # Solo aplicar si el mes está dentro del rango
                if fecha_inicio_mes <= mes_futuro_comparacion <= fecha_fin_mes:
                    pago_creditos += cred['monto_mensual']

            # Calcular pagos MSI (solo los que ya empezaron)
            pago_msis = 0
            for msi in msis:
                fecha_primera = parse_fecha(msi['fecha_primera_mensualidad'])
                fecha_primera_mes = datetime(fecha_primera.year, fecha_primera.month, 1)

                # Verificar si este mes ya debe pagar
                meses_desde_inicio = (mes_futuro_comparacion.year - fecha_primera_mes.year) * 12 + (mes_futuro_comparacion.month - fecha_primera_mes.month)

                if meses_desde_inicio >= 0 and meses_desde_inicio < msi['meses_restantes']:
                    pago_msis += msi['mensualidad']

            pago_total_mes = pago_creditos + pago_msis

            # Actualizar saldo: + ingresos - gastos
            saldo_actual = saldo_actual + ingresos_mes - pago_total_mes

            # Determinar estado (semáforo)
            estado = calcular_estado_semaforo(saldo_actual)

            proyeccion.append({
                'mes': mes_nombre,
                'ingresos_mes': ingresos_mes,
                'pago_total': pago_total_mes,
                'saldo_estimado': saldo_actual,
                'estado': estado
            })

        return proyeccion

    except Exception as e:
        print(f"❌ Error al calcular proyección: {str(e)}")
        return []


@app.route('/')
def home():
    """Página principal con dashboard"""
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # Obtener configuración (con valores por defecto si no existen)
        try:
            c.execute("SELECT valor FROM configuracion WHERE clave='balance_inicial'")
            result = c.fetchone()
            balance_inicial = float(result['valor']) if result else 0.0
        except:
            balance_inicial = 0.0

        try:
            c.execute("SELECT valor FROM configuracion WHERE clave='primera_vez'")
            result = c.fetchone()
            primera_vez = int(result['valor']) if result else 1
        except:
            primera_vez = 1

        # Datos actuales
        c.execute('SELECT * FROM ingresos ORDER BY fecha DESC LIMIT 10')
        ingresos = c.fetchall()

        c.execute('SELECT * FROM gastos ORDER BY fecha DESC LIMIT 10')
        gastos = c.fetchall()

        c.execute('SELECT SUM(monto) FROM ingresos')
        total_ingresos = c.fetchone()[0] or 0

        c.execute('SELECT SUM(monto) FROM gastos')
        total_gastos = c.fetchone()[0] or 0

        # Créditos y MSI
        c.execute('SELECT * FROM creditos_programados WHERE activo=1')
        creditos = c.fetchall()

        c.execute('SELECT * FROM compras_msi WHERE activo=1')
        msis = c.fetchall()

        # Ingresos recurrentes
        c.execute('SELECT * FROM ingresos_recurrentes WHERE activo=1')
        ingresos_recurrentes = c.fetchall()

        # Balance real = Balance inicial + Ingresos - Gastos
        balance = balance_inicial + total_ingresos - total_gastos

        conn.close()

        # Calcular proyección
        proyeccion = calcular_proyeccion_meses(Config.PROYECCION_MESES_DEFAULT)

        # Obtener próximas alertas
        alertas = obtener_proximas_alertas(15)

        return render_template('index.html',
                             ingresos=ingresos,
                             gastos=gastos,
                             creditos=creditos,
                             msis=msis,
                             ingresos_recurrentes=ingresos_recurrentes,
                             balance_inicial=balance_inicial,
                             total_ingresos=total_ingresos,
                             total_gastos=total_gastos,
                             balance=balance,
                             primera_vez=primera_vez,
                             proyeccion=proyeccion,
                             alertas=alertas)

    except Exception as e:
        flash(f'Error al cargar el dashboard: {str(e)}', 'error')
        print(f"❌ Error en home(): {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('index.html',
                             ingresos=[],
                             gastos=[],
                             creditos=[],
                             msis=[],
                             ingresos_recurrentes=[],
                             balance_inicial=0,
                             total_ingresos=0,
                             total_gastos=0,
                             balance=0,
                             primera_vez=0,
                             proyeccion=[],
                             alertas=[])


if __name__ == '__main__':
    init_db()
    print("[INICIO] Iniciando FinanzApp Modular...")
    print("[INFO] Abre tu navegador en: http://127.0.0.1:5000")
    app.run(debug=Config.DEBUG)
