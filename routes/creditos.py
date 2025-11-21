# -*- coding: utf-8 -*-
# routes/creditos.py - Rutas de créditos programados
from flask import request, redirect, flash
from routes import creditos_bp
from database import get_db_connection
from utils import validar_fecha, validar_monto, validar_dia_mes, validar_texto, calcular_fecha_inicio_inteligente
from config import Config

@creditos_bp.route('/agregar_credito', methods=['POST'])
def agregar_credito():
    """Agregar crédito programado"""
    try:
        nombre = request.form.get('nombre', '').strip()
        monto_str = request.form.get('monto', '0')
        dia_pago_str = request.form.get('dia_pago', '1')
        fecha_inicio = request.form.get('fecha_inicio', '').strip()
        fecha_fin = request.form.get('fecha_fin', '').strip()

        # Campos opcionales
        fecha_corte = int(request.form.get('fecha_corte', 0))
        fecha_limite_pago = int(request.form.get('fecha_limite_pago', 0))
        fecha_apartado = int(request.form.get('fecha_apartado', 0))
        dias_alerta = int(request.form.get('dias_alerta', 3))
        notas = request.form.get('notas', '')

        # Validar nombre
        valido_nombre, nombre, error_nombre = validar_texto(nombre, "Nombre")
        if not valido_nombre:
            flash(f'Error: {error_nombre}', 'error')
            return redirect('/')

        # Validar monto
        valido_monto, monto, error_monto = validar_monto(monto_str, "Monto", minimo=0.01)
        if not valido_monto:
            flash(f'Error: {error_monto}', 'error')
            return redirect('/')

        # Validar día de pago
        valido_dia, dia_pago, error_dia = validar_dia_mes(dia_pago_str, "Día de pago")
        if not valido_dia:
            flash(f'Error: {error_dia}', 'error')
            return redirect('/')

        # Si fecha_limite_pago no está configurado, usar dia_pago
        if fecha_limite_pago == 0:
            fecha_limite_pago = dia_pago

        if fecha_apartado == 0:
            fecha_apartado = dia_pago

        # Validar/calcular fecha de inicio
        if not fecha_inicio or fecha_inicio == '':
            fecha_inicio = calcular_fecha_inicio_inteligente(dia_pago, fecha_limite_pago)
        else:
            valido_fecha_inicio, fecha_inicio, error_fecha_inicio = validar_fecha(fecha_inicio, "Fecha de inicio")
            if not valido_fecha_inicio:
                flash(f'Error: {error_fecha_inicio}', 'error')
                return redirect('/')

        # Validar fecha fin (opcional)
        if not fecha_fin or fecha_fin == '':
            fecha_fin = Config.FECHA_INDEFINIDA
        else:
            valido_fecha_fin, fecha_fin, error_fecha_fin = validar_fecha(fecha_fin, "Fecha fin", requerido=False)
            if not valido_fecha_fin:
                flash(f'Error: {error_fecha_fin}', 'error')
                return redirect('/')

        # Insertar en BD
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''INSERT INTO creditos_programados
                    (nombre, monto_mensual, dia_pago, fecha_inicio, fecha_fin,
                     fecha_corte, fecha_limite_pago, fecha_apartado, dias_alerta, notas)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (nombre, monto, dia_pago, fecha_inicio, fecha_fin,
                  fecha_corte, fecha_limite_pago, fecha_apartado, dias_alerta, notas))
        conn.commit()
        conn.close()

        flash(f'Crédito agregado: {nombre} - ${monto:.2f}/mes', 'success')
        print(f"[CREDITO] {nombre} - ${monto:.2f}/mes (dia {dia_pago})")

    except Exception as e:
        flash(f'Error al agregar crédito: {str(e)}', 'error')
        print(f"[ERROR] Error al agregar credito: {str(e)}")

    return redirect('/')


@creditos_bp.route('/desactivar_credito/<int:id>')
def desactivar_credito(id):
    """Desactivar (soft delete) un crédito"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('UPDATE creditos_programados SET activo=0 WHERE id=?', (id,))
        conn.commit()
        conn.close()

        flash('Crédito desactivado', 'success')
        print(f"[DESACTIVAR] Credito {id} desactivado")

    except Exception as e:
        flash(f'Error al desactivar crédito: {str(e)}', 'error')
        print(f"[ERROR] Error al desactivar credito: {str(e)}")

    return redirect('/')


@creditos_bp.route('/borrar_credito/<int:id>')
def borrar_credito(id):
    """Borrar completamente un crédito"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM creditos_programados WHERE id=?', (id,))
        conn.commit()
        conn.close()

        flash('Crédito eliminado', 'success')
        print(f"[DELETE] Credito {id} eliminado")

    except Exception as e:
        flash(f'Error al eliminar crédito: {str(e)}', 'error')
        print(f"[ERROR] Error al eliminar credito: {str(e)}")

    return redirect('/')
