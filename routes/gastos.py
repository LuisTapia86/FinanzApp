# -*- coding: utf-8 -*-
# routes/gastos.py - Rutas de gastos
from flask import request, redirect, flash
from routes import gastos_bp
from database import get_db_connection
from utils import validar_fecha, validar_monto, validar_texto
from datetime import datetime

@gastos_bp.route('/agregar_gasto', methods=['POST'])
def agregar_gasto():
    """Agregar nuevo gasto (efectivo, tarjeta, o compra MSI)"""
    from config import Config

    try:
        fecha = request.form.get('fecha', '').strip()
        tipo = request.form.get('tipo', 'efectivo')
        nombre = request.form.get('nombre', '').strip()
        monto_str = request.form.get('monto', '0')
        es_msi = request.form.get('es_msi', '0')  # '1' si está marcado
        categoria_id = request.form.get('categoria_id', None)
        tarjeta_id = request.form.get('tarjeta_id', None)

        # Obtener usuario_id
        usuario_id = Config.DEFAULT_USER_ID if Config.SKIP_LOGIN else 1

        # Validar datos
        valido_fecha, fecha, error_fecha = validar_fecha(fecha, "Fecha", requerido=True)
        if not valido_fecha:
            flash(f'Error: {error_fecha}', 'error')
            return redirect('/')

        valido_nombre, nombre, error_nombre = validar_texto(nombre, "Nombre", min_length=1, max_length=200)
        if not valido_nombre:
            flash(f'Error: {error_nombre}', 'error')
            return redirect('/')

        valido_monto, monto, error_monto = validar_monto(monto_str, "Monto", minimo=0.01)
        if not valido_monto:
            flash(f'Error: {error_monto}', 'error')
            return redirect('/')

        conn = get_db_connection()
        c = conn.cursor()

        # Si es compra MSI
        if es_msi == '1':
            meses = int(request.form.get('meses', 3))
            fecha_primera = request.form.get('fecha_primera_msi', fecha)

            if not fecha_primera or fecha_primera.strip() == '':
                fecha_primera = datetime.now().strftime('%Y-%m-%d')

            mensualidad = monto / meses

            c.execute('''INSERT INTO compras_msi
                        (producto, precio_total, meses, mensualidad, fecha_primera_mensualidad, meses_restantes, usuario_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (nombre, monto, meses, mensualidad, fecha_primera, meses, usuario_id))
            conn.commit()
            conn.close()

            flash(f'Compra MSI agregada: {nombre} - {meses} meses de ${mensualidad:.2f}', 'success')
            print(f"[MSI] Compra agregada: {nombre} - ${monto:.2f} en {meses} meses")

        # Si es gasto con tarjeta (sin MSI)
        elif tipo == 'tarjeta' and tarjeta_id:
            c.execute('''INSERT INTO gastos_tdc
                        (tarjeta_id, fecha, concepto, monto, categoria_id, usuario_id)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (tarjeta_id, fecha, nombre, monto, categoria_id if categoria_id else None, usuario_id))
            conn.commit()
            conn.close()

            flash(f'Gasto con tarjeta agregado: {nombre} - ${monto:.2f}', 'success')
            print(f"[TDC] Gasto agregado: {nombre} - ${monto:.2f} (Tarjeta ID: {tarjeta_id})")

        # Gasto en efectivo/transferencia
        else:
            c.execute('INSERT INTO gastos (fecha, tipo, nombre, monto, categoria_id, usuario_id) VALUES (?, ?, ?, ?, ?, ?)',
                     (fecha, tipo, nombre, monto, categoria_id if categoria_id else None, usuario_id))
            conn.commit()
            conn.close()

            flash(f'Gasto agregado: {nombre} - ${monto:.2f}', 'success')
            print(f"[GASTO] {nombre} - ${monto:.2f} ({tipo})")

    except Exception as e:
        flash(f'Error al agregar gasto: {str(e)}', 'error')
        print(f"[ERROR] Error al agregar gasto: {str(e)}")
        import traceback
        traceback.print_exc()

    return redirect('/')


@gastos_bp.route('/borrar_gasto/<int:id>')
def borrar_gasto(id):
    """Borrar un gasto específico"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM gastos WHERE id=?', (id,))
        conn.commit()
        conn.close()

        flash('Gasto eliminado exitosamente', 'success')
        print(f"[DELETE] Gasto {id} eliminado")

    except Exception as e:
        flash(f'Error al eliminar gasto: {str(e)}', 'error')
        print(f"[ERROR] Error al eliminar gasto: {str(e)}")

    return redirect('/')


@gastos_bp.route('/borrar_gasto_tdc/<int:id>')
def borrar_gasto_tdc(id):
    """Borrar un gasto de tarjeta de crédito"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM gastos_tdc WHERE id=?', (id,))
        conn.commit()
        conn.close()

        flash('Gasto de tarjeta eliminado exitosamente', 'success')
        print(f"[DELETE] Gasto TDC {id} eliminado")

    except Exception as e:
        flash(f'Error al eliminar gasto de tarjeta: {str(e)}', 'error')
        print(f"[ERROR] Error al eliminar gasto TDC: {str(e)}")

    return redirect('/')
