# -*- coding: utf-8 -*-
# routes/prestamos.py - Rutas para gestión de Préstamos
from flask import request, redirect, url_for
from database import get_db_connection
from . import prestamos_bp

@prestamos_bp.route('/agregar_prestamo', methods=['POST'])
def agregar_prestamo():
    """Agregar nuevo préstamo"""
    try:
        nombre = request.form['nombre']
        monto_mensual = float(request.form['monto_mensual'])
        dia_pago = int(request.form['dia_pago'])
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        dias_alerta = int(request.form.get('dias_alerta', 10))

        conn = get_db_connection()
        c = conn.cursor()

        c.execute('''INSERT INTO prestamos
                     (nombre, monto_mensual, dia_pago, fecha_inicio, fecha_fin, dias_alerta)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (nombre, monto_mensual, dia_pago, fecha_inicio, fecha_fin, dias_alerta))

        conn.commit()
        conn.close()

        print(f"[PRESTAMO] Agregado: {nombre} - ${monto_mensual:.2f}/mes (Día {dia_pago})")
        return redirect(url_for('home'))

    except Exception as e:
        print(f"[ERROR] Error al agregar préstamo: {e}")
        return redirect(url_for('home'))


@prestamos_bp.route('/desactivar_prestamo/<int:id>')
def desactivar_prestamo(id):
    """Desactivar préstamo"""
    try:
        conn = get_db_connection()
        c = conn.cursor()

        c.execute('UPDATE prestamos SET activo=0 WHERE id=?', (id,))

        conn.commit()
        conn.close()

        print(f"[DESACTIVAR] Préstamo ID {id}")
        return redirect(url_for('home'))

    except Exception as e:
        print(f"[ERROR] Error al desactivar préstamo: {e}")
        return redirect(url_for('home'))


@prestamos_bp.route('/borrar_prestamo/<int:id>')
def borrar_prestamo(id):
    """Eliminar préstamo"""
    try:
        conn = get_db_connection()
        c = conn.cursor()

        c.execute('DELETE FROM prestamos WHERE id=?', (id,))

        conn.commit()
        conn.close()

        print(f"[DELETE] Préstamo ID {id}")
        return redirect(url_for('home'))

    except Exception as e:
        print(f"[ERROR] Error al borrar préstamo: {e}")
        return redirect(url_for('home'))
