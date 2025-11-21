# routes/api.py - API endpoints para AJAX
from flask import jsonify
from datetime import datetime
from database import get_db_connection
from . import api_bp

@api_bp.route('/api/movimientos_mes_actual', methods=['GET'])
def movimientos_mes_actual():
    """Obtener movimientos del mes actual"""
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # Obtener el primer y último día del mes actual
        hoy = datetime.now()
        primer_dia_mes = datetime(hoy.year, hoy.month, 1).strftime('%Y-%m-%d')

        # Obtener balance inicial configurado
        c.execute('SELECT balance_inicial FROM configuracion WHERE id=1')
        balance_inicial_app = c.fetchone()['balance_inicial']

        # Calcular saldo al inicio del mes (balance inicial + movimientos hasta fin del mes anterior)
        # Ingresos hasta fin del mes anterior
        c.execute('''SELECT COALESCE(SUM(monto), 0) as total
                     FROM ingresos
                     WHERE fecha < ?''', (primer_dia_mes,))
        ingresos_previos = c.fetchone()['total']

        # Gastos hasta fin del mes anterior
        c.execute('''SELECT COALESCE(SUM(monto), 0) as total
                     FROM gastos
                     WHERE fecha < ?''', (primer_dia_mes,))
        gastos_previos = c.fetchone()['total']

        saldo_inicio_mes = balance_inicial_app + ingresos_previos - gastos_previos

        # Obtener ingresos del mes actual
        c.execute('''SELECT COALESCE(SUM(monto), 0) as total
                     FROM ingresos
                     WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')''')
        ingresos_mes = c.fetchone()['total']

        # Obtener gastos del mes actual
        c.execute('''SELECT COALESCE(SUM(monto), 0) as total
                     FROM gastos
                     WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')''')
        gastos_mes = c.fetchone()['total']

        # Saldo actual
        saldo_actual = saldo_inicio_mes + ingresos_mes - gastos_mes

        conn.close()

        return jsonify({
            'saldo_inicio_mes': saldo_inicio_mes,
            'ingresos_mes': ingresos_mes,
            'gastos_mes': gastos_mes,
            'saldo_actual': saldo_actual
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
