# routes/api.py - API endpoints for AJAX
from flask import jsonify
from datetime import datetime
from database import get_db_connection
from . import api_bp

@api_bp.route('/api/movimientos_mes_actual', methods=['GET'])
def movimientos_mes_actual():
    """Get current month movements"""
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # Get first and last day of current month
        hoy = datetime.now()
        primer_dia_mes = datetime(hoy.year, hoy.month, 1).strftime('%Y-%m-%d')

        # Get configured initial balance
        c.execute('SELECT balance_inicial FROM configuracion WHERE id=1')
        balance_inicial_app = c.fetchone()['balance_inicial']

        # Calculate balance at start of month (initial balance + movements until end of previous month)
        # Income until end of previous month
        c.execute('''SELECT COALESCE(SUM(monto), 0) as total
                     FROM ingresos
                     WHERE fecha < ?''', (primer_dia_mes,))
        ingresos_previos = c.fetchone()['total']

        # Expenses until end of previous month
        c.execute('''SELECT COALESCE(SUM(monto), 0) as total
                     FROM gastos
                     WHERE fecha < ?''', (primer_dia_mes,))
        gastos_previos = c.fetchone()['total']

        saldo_inicio_mes = balance_inicial_app + ingresos_previos - gastos_previos

        # Get current month income
        c.execute('''SELECT COALESCE(SUM(monto), 0) as total
                     FROM ingresos
                     WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')''')
        ingresos_mes = c.fetchone()['total']

        # Get current month expenses
        c.execute('''SELECT COALESCE(SUM(monto), 0) as total
                     FROM gastos
                     WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')''')
        gastos_mes = c.fetchone()['total']

        # Current balance
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
