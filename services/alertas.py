# services/alertas.py - Lógica de alertas de pagos
import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from config import Config

def obtener_proximas_alertas(dias_adelante=15):
    """
    Obtener próximas alertas de pagos

    Args:
        dias_adelante: Días hacia adelante para buscar alertas

    Returns:
        list: Lista de diccionarios con alertas
    """
    conn = sqlite3.connect(Config.DATABASE_PATH)
    c = conn.cursor()

    # Obtener créditos activos con alertas
    c.execute('''SELECT id, nombre, monto_mensual, fecha_limite_pago, dias_alerta, notas, fecha_inicio, fecha_fin
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
        dia_limite = cred[3]
        dias_alerta = cred[4] or 10
        fecha_inicio_str = cred[6]
        fecha_fin_str = cred[7]

        # Verificar si el crédito ya inició
        if fecha_inicio_str:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
            if hoy < fecha_inicio:
                # El crédito aún no ha iniciado, no mostrar alertas
                continue

        # Verificar si el crédito ya terminó
        if fecha_fin_str:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
            if hoy > fecha_fin:
                # El crédito ya terminó, no mostrar alertas
                continue

        # Calcular próxima fecha de pago (este mes o siguiente)
        for mes_offset in range(3):  # Revisar próximos 3 meses
            fecha_pago = hoy + relativedelta(months=mes_offset)
            try:
                fecha_pago = datetime(fecha_pago.year, fecha_pago.month, dia_limite)
            except ValueError:
                # Si el día no existe en ese mes (ej: 31 en febrero), usar último día
                fecha_pago = datetime(fecha_pago.year, fecha_pago.month, 1) + relativedelta(months=1, days=-1)

            dias_para_pago = (fecha_pago - hoy).days

            # Usar dias_alerta del crédito específico en lugar de dias_adelante global
            if 0 <= dias_para_pago <= dias_alerta:
                urgencia = "urgente" if dias_para_pago <= 2 else "proximo" if dias_para_pago <= 5 else "programado"

                alertas.append({
                    'tipo': 'credito',
                    'nombre': cred[1],
                    'monto': cred[2],
                    'fecha_pago': fecha_pago,
                    'dias_restantes': dias_para_pago,
                    'urgencia': urgencia,
                    'notas': cred[5] or ''
                })
                break

    # Procesar MSI
    for msi in msis:
        dia_pago = msi[3] if msi[3] else 15
        dias_alerta = msi[4] or 10

        for mes_offset in range(3):
            fecha_pago = hoy + relativedelta(months=mes_offset)
            try:
                fecha_pago = datetime(fecha_pago.year, fecha_pago.month, dia_pago)
            except ValueError:
                fecha_pago = datetime(fecha_pago.year, fecha_pago.month, 1) + relativedelta(months=1, days=-1)

            dias_para_pago = (fecha_pago - hoy).days

            # Usar dias_alerta del MSI específico en lugar de dias_adelante global
            if 0 <= dias_para_pago <= dias_alerta:
                urgencia = "urgente" if dias_para_pago <= 2 else "proximo" if dias_para_pago <= 5 else "programado"

                alertas.append({
                    'tipo': 'msi',
                    'nombre': msi[1],
                    'monto': msi[2],
                    'fecha_pago': fecha_pago,
                    'dias_restantes': dias_para_pago,
                    'urgencia': urgencia,
                    'notas': ''
                })
                break

    # Ordenar por fecha más próxima
    alertas.sort(key=lambda x: x['dias_restantes'])

    return alertas
