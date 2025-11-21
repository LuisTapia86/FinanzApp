# -*- coding: utf-8 -*-
# routes/dashboard.py - Rutas del dashboard analítico
from flask import render_template
from routes import dashboard_bp
from database import get_db_connection
from services import calcular_proyeccion_quincenal

@dashboard_bp.route('/dashboard')
def dashboard():
    """Dashboard analítico con gráficas y métricas"""
    try:
        conn = get_db_connection()
        c = conn.cursor()

        # ========== BALANCE ACTUAL ==========
        c.execute('SELECT balance_inicial FROM configuracion WHERE id = 1')
        balance_inicial_row = c.fetchone()
        balance_inicial = balance_inicial_row['balance_inicial'] if balance_inicial_row else 0.0

        c.execute('SELECT SUM(monto) as total FROM ingresos')
        total_ingresos_row = c.fetchone()
        total_ingresos = total_ingresos_row['total'] if total_ingresos_row['total'] else 0.0

        c.execute('SELECT SUM(monto) as total FROM gastos')
        total_gastos_row = c.fetchone()
        total_gastos = total_gastos_row['total'] if total_gastos_row['total'] else 0.0

        balance_actual = balance_inicial + total_ingresos - total_gastos

        # ========== COMPROMISOS MENSUALES ==========
        # Préstamos (antes créditos_programados)
        c.execute('SELECT SUM(monto_mensual) as total FROM prestamos WHERE activo=1')
        total_prestamos_row = c.fetchone()
        total_prestamos = total_prestamos_row['total'] if total_prestamos_row['total'] else 0.0

        # MSI de tarjetas
        c.execute('SELECT SUM(mensualidad_msi) as total FROM gastos_tdc WHERE activo=1 AND tipo="msi"')
        total_msi_row = c.fetchone()
        total_msi = total_msi_row['total'] if total_msi_row['total'] else 0.0

        compromisos_mensuales = total_prestamos + total_msi

        # ========== INGRESOS RECURRENTES ==========
        c.execute('SELECT SUM(monto) as total FROM ingresos_recurrentes WHERE activo=1')
        ingresos_recurrentes_row = c.fetchone()
        ingresos_recurrentes = ingresos_recurrentes_row['total'] if ingresos_recurrentes_row['total'] else 0.0

        # ========== PROYECCIÓN QUINCENAL (24 quincenas = 12 meses) ==========
        proyeccion = calcular_proyeccion_quincenal(quincenas_adelante=24, fecha_pago_1=10, fecha_pago_2=25)
        if proyeccion and len(proyeccion) > 0:
            peor_quincena = min(proyeccion, key=lambda x: x['saldo_estimado'])
            saldo_minimo_proyectado = peor_quincena['saldo_estimado']
        else:
            saldo_minimo_proyectado = balance_actual

        # ========== GRÁFICA 1: INGRESOS VS GASTOS (Últimos 6 meses) ==========
        c.execute('''SELECT strftime('%Y-%m', fecha) as mes, SUM(monto) as total
                     FROM ingresos
                     GROUP BY mes
                     ORDER BY mes DESC
                     LIMIT 6''')
        ingresos_data = [dict(row) for row in c.fetchall()]

        c.execute('''SELECT strftime('%Y-%m', fecha) as mes, SUM(monto) as total
                     FROM gastos
                     GROUP BY mes
                     ORDER BY mes DESC
                     LIMIT 6''')
        gastos_data = [dict(row) for row in c.fetchall()]

        # ========== GRÁFICA 2: DISTRIBUCIÓN DE GASTOS POR TIPO ==========
        c.execute('''SELECT tipo, SUM(monto) as total
                     FROM gastos
                     GROUP BY tipo''')
        gastos_por_tipo = [dict(row) for row in c.fetchall()]

        # ========== GRÁFICA 3: PROYECCIÓN SEMÁFORO ==========
        # Ya tenemos 'proyeccion' calculado arriba

        # ========== GRÁFICA 4: TOP 5 GASTOS MAYORES ==========
        c.execute('''SELECT nombre, monto, fecha
                     FROM gastos
                     ORDER BY monto DESC
                     LIMIT 5''')
        top_gastos = [dict(row) for row in c.fetchall()]

        # ========== TABLA 1: PRÉSTAMOS ACTIVOS ==========
        c.execute('''SELECT nombre, monto_mensual, dia_pago, fecha_inicio, fecha_fin
                     FROM prestamos
                     WHERE activo=1
                     ORDER BY dia_pago''')
        creditos_activos = [dict(row) for row in c.fetchall()]

        # ========== TABLA 2: MSI ACTIVOS ==========
        c.execute('''SELECT
                        gt.concepto as producto,
                        gt.monto as precio_total,
                        gt.meses_msi as meses,
                        gt.mensualidad_msi as mensualidad,
                        gt.meses_restantes
                     FROM gastos_tdc gt
                     WHERE gt.activo=1 AND gt.tipo="msi"
                     ORDER BY gt.meses_restantes DESC''')
        compras_msi_activas = [dict(row) for row in c.fetchall()]

        # ========== TABLA 3: INGRESOS RECURRENTES ==========
        c.execute('''SELECT nombre, monto, dia_pago, fecha_inicio, fecha_fin
                     FROM ingresos_recurrentes
                     WHERE activo=1
                     ORDER BY dia_pago''')
        ingresos_rec_lista = [dict(row) for row in c.fetchall()]

        # ========== TABLA 4: ÚLTIMAS TRANSACCIONES ==========
        c.execute('''SELECT fecha, concepto as nombre, monto, 'Ingreso' as tipo
                     FROM ingresos
                     UNION ALL
                     SELECT fecha, nombre, monto, 'Gasto' as tipo
                     FROM gastos
                     ORDER BY fecha DESC
                     LIMIT 10''')
        ultimas_transacciones = [dict(row) for row in c.fetchall()]

        conn.close()

        # Renderizar template con todos los datos
        return render_template('dashboard.html',
                             balance_actual=balance_actual,
                             balance_inicial=balance_inicial,
                             total_ingresos=total_ingresos,
                             total_gastos=total_gastos,
                             compromisos_mensuales=compromisos_mensuales,
                             ingresos_recurrentes=ingresos_recurrentes,
                             saldo_minimo_proyectado=saldo_minimo_proyectado,
                             ingresos_por_mes=ingresos_data,
                             gastos_por_mes=gastos_data,
                             ingresos_data=ingresos_data,
                             gastos_data=gastos_data,
                             gastos_por_tipo=gastos_por_tipo,
                             proyeccion=proyeccion,
                             top_gastos=top_gastos,
                             creditos_activos=creditos_activos,
                             compras_msi_activas=compras_msi_activas,
                             msis_activos=compras_msi_activas,
                             ingresos_rec_lista=ingresos_rec_lista,
                             ultimas_transacciones=ultimas_transacciones)

    except Exception as e:
        print(f"[ERROR] Error al cargar dashboard: {str(e)}")
        return f"Error al cargar dashboard: {str(e)}", 500
