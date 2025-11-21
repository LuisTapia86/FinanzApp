# utils/validators.py - Validadores de datos
from datetime import datetime
from flask import flash

def validar_fecha(fecha_str, campo_nombre="Fecha", requerido=True):
    """
    Valida que una fecha sea válida

    Args:
        fecha_str: String con la fecha
        campo_nombre: Nombre del campo para mensajes de error
        requerido: Si el campo es requerido

    Returns:
        tuple: (es_valido, fecha_str_validada, mensaje_error)
    """
    if not fecha_str or fecha_str.strip() == '':
        if requerido:
            return False, None, f"{campo_nombre} es requerido"
        return True, '', None

    # Intentar parsear la fecha
    try:
        datetime.strptime(fecha_str, '%Y-%m-%d')
        return True, fecha_str, None
    except ValueError:
        return False, None, f"{campo_nombre} tiene un formato inválido (debe ser YYYY-MM-DD)"


def validar_monto(monto_str, campo_nombre="Monto", minimo=0, requerido=True):
    """
    Valida que un monto sea válido

    Args:
        monto_str: String o número con el monto
        campo_nombre: Nombre del campo para mensajes de error
        minimo: Valor mínimo permitido
        requerido: Si el campo es requerido

    Returns:
        tuple: (es_valido, monto_float, mensaje_error)
    """
    if monto_str is None or str(monto_str).strip() == '':
        if requerido:
            return False, None, f"{campo_nombre} es requerido"
        return True, 0.0, None

    try:
        monto = float(monto_str)
        if minimo is not None and monto < minimo:
            return False, None, f"{campo_nombre} debe ser mayor o igual a {minimo}"
        return True, monto, None
    except (ValueError, TypeError):
        return False, None, f"{campo_nombre} debe ser un número válido"


def validar_dia_mes(dia, campo_nombre="Día del mes", requerido=True):
    """
    Valida que un día del mes sea válido (1-31)

    Args:
        dia: Número del día
        campo_nombre: Nombre del campo para mensajes de error
        requerido: Si el campo es requerido

    Returns:
        tuple: (es_valido, dia_int, mensaje_error)
    """
    if dia is None or str(dia).strip() == '':
        if requerido:
            return False, None, f"{campo_nombre} es requerido"
        return True, 1, None

    try:
        dia_int = int(dia)
        if dia_int < 1 or dia_int > 31:
            return False, None, f"{campo_nombre} debe estar entre 1 y 31"
        return True, dia_int, None
    except (ValueError, TypeError):
        return False, None, f"{campo_nombre} debe ser un número entero"


def validar_texto(texto, campo_nombre="Campo", min_length=1, max_length=200, requerido=True):
    """
    Valida que un texto sea válido

    Args:
        texto: String con el texto
        campo_nombre: Nombre del campo para mensajes de error
        min_length: Longitud mínima
        max_length: Longitud máxima
        requerido: Si el campo es requerido

    Returns:
        tuple: (es_valido, texto_validado, mensaje_error)
    """
    if not texto or texto.strip() == '':
        if requerido:
            return False, None, f"{campo_nombre} es requerido"
        return True, '', None

    texto = texto.strip()

    if len(texto) < min_length:
        return False, None, f"{campo_nombre} debe tener al menos {min_length} caracteres"

    if len(texto) > max_length:
        return False, None, f"{campo_nombre} no puede tener más de {max_length} caracteres"

    return True, texto, None
