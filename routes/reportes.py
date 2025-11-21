# -*- coding: utf-8 -*-
# routes/reportes.py - Rutas de reportes y estadísticas
from flask import jsonify
from routes import reportes_bp
from database import get_db_connection
from datetime import datetime, timedelta

@reportes_bp.route('/api/reportes/gastos_por_categoria')
def gastos_por_categoria():
    """Obtener gastos agrupados por categoría"""
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # Obtener gastos con categorías
        c.execute('''
            SELECT
                c.nombre as categoria,
                c.color as color,
                SUM(g.monto) as total,
                COUNT(g.id) as cantidad
            FROM gastos g
            LEFT JOIN categorias c ON g.categoria_id = c.id
            GROUP BY c.id, c.nombre, c.color
            ORDER BY total DESC
        ''')

        datos = c.fetchall()
        conn.close()

        # Convertir a diccionario
        resultado = []
        for row in datos:
            resultado.append({
                'categoria': row['categoria'] if row['categoria'] else 'Sin categoría',
                'color': row['color'] if row['color'] else '#6c757d',
                'total': float(row['total']),
                'cantidad': row['cantidad']
            })

        return jsonify(resultado)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reportes_bp.route('/api/reportes/ingresos_por_categoria')
def ingresos_por_categoria():
    """Obtener ingresos agrupados por categoría"""
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # Obtener ingresos con categorías
        c.execute('''
            SELECT
                c.nombre as categoria,
                c.color as color,
                SUM(i.monto) as total,
                COUNT(i.id) as cantidad
            FROM ingresos i
            LEFT JOIN categorias c ON i.categoria_id = c.id
            GROUP BY c.id, c.nombre, c.color
            ORDER BY total DESC
        ''')

        datos = c.fetchall()
        conn.close()

        # Convertir a diccionario
        resultado = []
        for row in datos:
            resultado.append({
                'categoria': row['categoria'] if row['categoria'] else 'Sin categoría',
                'color': row['color'] if row['color'] else '#6c757d',
                'total': float(row['total']),
                'cantidad': row['cantidad']
            })

        return jsonify(resultado)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reportes_bp.route('/api/reportes/tendencia_mensual')
def tendencia_mensual():
    """Obtener tendencia mensual de ingresos y gastos (últimos 12 meses)"""
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # Calcular fecha de inicio (12 meses atrás)
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=365)

        # Obtener ingresos por mes
        c.execute('''
            SELECT
                strftime('%Y-%m', fecha) as mes,
                SUM(monto) as total
            FROM ingresos
            WHERE fecha >= ?
            GROUP BY mes
            ORDER BY mes
        ''', (fecha_inicio.strftime('%Y-%m-%d'),))

        ingresos_mes = {row['mes']: float(row['total']) for row in c.fetchall()}

        # Obtener gastos por mes
        c.execute('''
            SELECT
                strftime('%Y-%m', fecha) as mes,
                SUM(monto) as total
            FROM gastos
            WHERE fecha >= ?
            GROUP BY mes
            ORDER BY mes
        ''', (fecha_inicio.strftime('%Y-%m-%d'),))

        gastos_mes = {row['mes']: float(row['total']) for row in c.fetchall()}

        conn.close()

        # Generar lista de todos los meses
        meses = []
        mes_actual = fecha_inicio
        while mes_actual <= fecha_fin:
            mes_str = mes_actual.strftime('%Y-%m')
            meses.append({
                'mes': mes_str,
                'mes_nombre': mes_actual.strftime('%b %Y'),
                'ingresos': ingresos_mes.get(mes_str, 0),
                'gastos': gastos_mes.get(mes_str, 0),
                'balance': ingresos_mes.get(mes_str, 0) - gastos_mes.get(mes_str, 0)
            })

            # Siguiente mes
            if mes_actual.month == 12:
                mes_actual = mes_actual.replace(year=mes_actual.year + 1, month=1)
            else:
                mes_actual = mes_actual.replace(month=mes_actual.month + 1)

        return jsonify(meses)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reportes_bp.route('/api/reportes/resumen')
def resumen():
    """Obtener resumen general de finanzas"""
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # Total ingresos
        c.execute('SELECT SUM(monto) as total FROM ingresos')
        total_ingresos = c.fetchone()['total'] or 0

        # Total gastos
        c.execute('SELECT SUM(monto) as total FROM gastos')
        total_gastos = c.fetchone()['total'] or 0

        # Balance inicial
        c.execute('SELECT balance_inicial FROM configuracion WHERE id=1')
        balance_inicial = c.fetchone()['balance_inicial'] or 0

        # Créditos activos
        c.execute('SELECT COUNT(*) as total FROM creditos_programados WHERE activo=1')
        creditos_activos = c.fetchone()['total']

        # MSI activos
        c.execute('SELECT COUNT(*) as total FROM compras_msi WHERE activo=1')
        msi_activos = c.fetchone()['total']

        # Promedio mensual de gastos (últimos 6 meses)
        fecha_limite = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        c.execute('''
            SELECT AVG(total_mes) as promedio
            FROM (
                SELECT SUM(monto) as total_mes
                FROM gastos
                WHERE fecha >= ?
                GROUP BY strftime('%Y-%m', fecha)
            )
        ''', (fecha_limite,))
        promedio_gastos = c.fetchone()['promedio'] or 0

        conn.close()

        return jsonify({
            'total_ingresos': float(total_ingresos),
            'total_gastos': float(total_gastos),
            'balance_actual': float(balance_inicial + total_ingresos - total_gastos),
            'creditos_activos': creditos_activos,
            'msi_activos': msi_activos,
            'promedio_gastos_mensual': float(promedio_gastos)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
