# services/simulador.py - Lógica del simulador de compras
from database import get_db_connection
from datetime import datetime
from dateutil.relativedelta import relativedelta

def simular_compra(precio, meses):
    """
    Simular impacto de una compra MSI en la proyección

    Args:
        precio: Precio total de la compra
        meses: Meses sin intereses

    Returns:
        dict: Resultado de la simulación con proyección mes a mes
    """
    conn = get_db_connection()
    c = conn.cursor()

    # Obtener balance inicial
    c.execute("SELECT balance_inicial FROM configuracion WHERE id=1")
    result = c.fetchone()
    balance_inicial = float(result[0]) if result else 0.0

    # Obtener totales de ingresos y gastos
    c.execute('SELECT SUM(monto) as total FROM ingresos')
    total_ingresos_row = c.fetchone()
    total_ingresos = total_ingresos_row['total'] if total_ingresos_row['total'] else 0.0

    c.execute('SELECT SUM(monto) as total FROM gastos')
    total_gastos_row = c.fetchone()
    total_gastos = total_gastos_row['total'] if total_gastos_row['total'] else 0.0

    # Calcular saldo actual
    saldo_actual = balance_inicial + total_ingresos - total_gastos

    # Obtener ingresos recurrentes
    c.execute('SELECT * FROM ingresos_recurrentes WHERE activo=1')
    ingresos_rec = c.fetchall()

    # Obtener créditos programados
    c.execute('SELECT * FROM creditos_programados WHERE activo=1')
    creditos = c.fetchall()

    # Obtener MSI activos
    c.execute('SELECT * FROM compras_msi WHERE activo=1')
    msis = c.fetchall()

    conn.close()

    # Calcular mensualidad
    mensualidad = precio / meses

    # Proyectar mes a mes (hasta el número de meses o 12, lo que sea mayor)
    meses_proyectar = max(meses, 12)
    proyeccion = []

    fecha_actual = datetime.now()
    saldo_sin_compra = saldo_actual
    saldo_con_compra = saldo_actual

    for i in range(meses_proyectar):
        mes_fecha = fecha_actual + relativedelta(months=i)
        mes_nombre = mes_fecha.strftime('%Y-%m')

        # Calcular ingresos del mes
        ingresos_mes = 0.0
        for ing in ingresos_rec:
            # Verificar si está activo en este mes
            fecha_inicio = datetime.strptime(ing['fecha_inicio'], '%Y-%m-%d')
            if ing['fecha_fin'] and ing['fecha_fin'] != '2099-12-31':
                fecha_fin = datetime.strptime(ing['fecha_fin'], '%Y-%m-%d')
                if mes_fecha < fecha_inicio or mes_fecha > fecha_fin:
                    continue
            elif mes_fecha < fecha_inicio:
                continue

            ingresos_mes += ing['monto']

        # Calcular gastos del mes (créditos)
        gastos_mes = 0.0
        for credito in creditos:
            fecha_inicio = datetime.strptime(credito['fecha_inicio'], '%Y-%m-%d')
            if credito['fecha_fin'] and credito['fecha_fin'] != '2099-12-31':
                fecha_fin = datetime.strptime(credito['fecha_fin'], '%Y-%m-%d')
                if mes_fecha < fecha_inicio or mes_fecha > fecha_fin:
                    continue
            elif mes_fecha < fecha_inicio:
                continue

            gastos_mes += credito['monto_mensual']

        # Calcular MSI existentes
        for msi in msis:
            if msi['meses_restantes'] > 0:
                fecha_primera = datetime.strptime(msi['fecha_primera_mensualidad'], '%Y-%m-%d')
                meses_transcurridos = (mes_fecha.year - fecha_primera.year) * 12 + (mes_fecha.month - fecha_primera.month)

                if 0 <= meses_transcurridos < msi['meses']:
                    gastos_mes += msi['mensualidad']

        # Calcular saldo SIN la nueva compra
        saldo_sin_compra = saldo_sin_compra + ingresos_mes - gastos_mes

        # Calcular saldo CON la nueva compra (restar mensualidad solo durante los meses MSI)
        if i < meses:
            saldo_con_compra = saldo_con_compra + ingresos_mes - gastos_mes - mensualidad
        else:
            saldo_con_compra = saldo_con_compra + ingresos_mes - gastos_mes

        # Determinar estados
        if saldo_sin_compra > 10000:
            estado_sin = "verde"
        elif saldo_sin_compra > 0:
            estado_sin = "amarillo"
        else:
            estado_sin = "rojo"

        if saldo_con_compra > 10000:
            estado_con = "verde"
        elif saldo_con_compra > 0:
            estado_con = "amarillo"
        else:
            estado_con = "rojo"

        proyeccion.append({
            'mes': mes_nombre,
            'numero_mes': i + 1,
            'ingresos': ingresos_mes,
            'gastos': gastos_mes,
            'mensualidad_msi': mensualidad if i < meses else 0,
            'saldo_sin_compra': round(saldo_sin_compra, 2),
            'saldo_con_compra': round(saldo_con_compra, 2),
            'diferencia': round(saldo_sin_compra - saldo_con_compra, 2),
            'estado_sin': estado_sin,
            'estado_con': estado_con
        })

    # Determinar veredicto
    veredicto = "SI"
    problema_en_mes = None
    mes_critico = None
    saldo_minimo = min(proyeccion, key=lambda x: x['saldo_con_compra'])

    for mes in proyeccion:
        if mes['estado_con'] == "rojo":
            if mes['numero_mes'] <= 3:
                veredicto = "NO"
                problema_en_mes = mes['numero_mes']
                mes_critico = mes['mes']
                break
            else:
                veredicto = "CUIDADO"
                problema_en_mes = mes['numero_mes']
                mes_critico = mes['mes']
                break

    return {
        'precio': precio,
        'meses': meses,
        'mensualidad': round(mensualidad, 2),
        'saldo_inicial': round(saldo_actual, 2),
        'proyeccion': proyeccion,
        'veredicto': veredicto,
        'problema_mes': problema_en_mes,
        'mes_critico': mes_critico,
        'saldo_minimo': round(saldo_minimo['saldo_con_compra'], 2),
        'saldo_final': round(proyeccion[-1]['saldo_con_compra'], 2)
    }
