# utils/helpers.py - Funciones auxiliares
from datetime import datetime
from dateutil.relativedelta import relativedelta
from config import Config

def parse_fecha(fecha_str):
    """
    Parsear fecha en múltiples formatos posibles

    Args:
        fecha_str: String con la fecha

    Returns:
        datetime: Objeto datetime parseado
    """
    if not fecha_str or fecha_str == Config.FECHA_INDEFINIDA:
        return datetime(2099, 12, 31)

    # Intentar formato YYYY-MM-DD
    try:
        return datetime.strptime(fecha_str, '%Y-%m-%d')
    except:
        pass

    # Intentar formato DD/MM/YYYY
    try:
        return datetime.strptime(fecha_str, '%d/%m/%Y')
    except:
        pass

    # Intentar formato MM/DD/YYYY
    try:
        return datetime.strptime(fecha_str, '%m/%d/%Y')
    except:
        pass

    # Si nada funciona, retornar fecha lejana
    return datetime(2099, 12, 31)


def calcular_fecha_inicio_inteligente(dia_pago, fecha_limite_pago=None):
    """
    Calcula la fecha de inicio inteligentemente basándose en el día de pago

    Args:
        dia_pago: Día del mes en que se recibe el pago/cobro
        fecha_limite_pago: Día límite de pago (para créditos), opcional

    Returns:
        str: Fecha de inicio en formato YYYY-MM-DD
    """
    hoy = datetime.now()
    dia_referencia = fecha_limite_pago if fecha_limite_pago is not None else dia_pago

    # Si el día de referencia de este mes ya pasó, empezar el siguiente mes
    if hoy.day > dia_referencia:
        # Empezar el mes siguiente
        fecha_calculada = hoy + relativedelta(months=1)
        try:
            return datetime(fecha_calculada.year, fecha_calculada.month, dia_referencia).strftime('%Y-%m-%d')
        except ValueError:
            # Si el día no existe en ese mes, usar el último día del mes
            ultimo_dia = (datetime(fecha_calculada.year, fecha_calculada.month, 1) + relativedelta(months=1, days=-1)).day
            return datetime(fecha_calculada.year, fecha_calculada.month, ultimo_dia).strftime('%Y-%m-%d')
    else:
        # Empezar este mes
        try:
            return datetime(hoy.year, hoy.month, dia_referencia).strftime('%Y-%m-%d')
        except ValueError:
            # Si el día no existe en este mes, usar el último día del mes
            ultimo_dia = (datetime(hoy.year, hoy.month, 1) + relativedelta(months=1, days=-1)).day
            return datetime(hoy.year, hoy.month, ultimo_dia).strftime('%Y-%m-%d')


def formatear_moneda(monto):
    """
    Formatea un monto como moneda

    Args:
        monto: Número a formatear

    Returns:
        str: Monto formateado como $X,XXX.XX
    """
    try:
        return f"${monto:,.2f}"
    except:
        return "$0.00"


def calcular_estado_semaforo(saldo):
    """
    Determina el estado del semáforo financiero

    Args:
        saldo: Saldo actual

    Returns:
        str: 'verde', 'amarillo' o 'rojo'
    """
    if saldo > Config.UMBRAL_VERDE:
        return "verde"
    elif saldo > Config.UMBRAL_AMARILLO:
        return "amarillo"
    else:
        return "rojo"
