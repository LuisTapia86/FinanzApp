# -*- coding: utf-8 -*-
# routes/msi.py - Rutas de compras MSI (Meses Sin Intereses)
from flask import request, redirect, flash, jsonify
from routes import msi_bp
from database import get_db_connection
from utils import validar_monto, validar_texto
from datetime import datetime

@msi_bp.route('/agregar_compra_msi', methods=['POST'])
def agregar_compra_msi():
    """Agregar compra en MSI confirmada"""
    try:
        producto = request.form.get('producto', '').strip()
        precio_str = request.form.get('precio', '0')
        meses = int(request.form.get('meses', 3))
        fecha_primera = request.form.get('fecha_primera', '').strip()

        # Validar producto
        valido_producto, producto, error_producto = validar_texto(producto, "Producto")
        if not valido_producto:
            flash(f'Error: {error_producto}', 'error')
            return redirect('/')

        # Validar precio
        valido_precio, precio, error_precio = validar_monto(precio_str, "Precio", minimo=0.01)
        if not valido_precio:
            flash(f'Error: {error_precio}', 'error')
            return redirect('/')

        # Si fecha_primera está vacía, usar fecha actual
        if not fecha_primera or fecha_primera == '':
            fecha_primera = datetime.now().strftime('%Y-%m-%d')

        mensualidad = precio / meses

        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''INSERT INTO compras_msi
                    (producto, precio_total, meses, mensualidad, fecha_primera_mensualidad, meses_restantes)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (producto, precio, meses, mensualidad, fecha_primera, meses))
        conn.commit()
        conn.close()

        flash(f'Compra MSI agregada: {producto} - {meses} meses de ${mensualidad:.2f}', 'success')
        print(f"[OK] Compra MSI agregada: {producto} - ${precio:.2f} en {meses} meses")

    except Exception as e:
        flash(f'Error al agregar compra MSI: {str(e)}', 'error')
        print(f"[ERROR] Error al agregar compra MSI: {str(e)}")

    return redirect('/')


@msi_bp.route('/simular_compra', methods=['POST'])
def simular_compra():
    """Simular una compra MSI y ver su impacto"""
    try:
        from services import simular_compra as simular_compra_servicio

        precio = float(request.json.get('precio', 0))
        meses = int(request.json.get('meses', 3))
        producto = request.json.get('producto', 'Sin nombre').strip()

        # Simular la compra
        resultado = simular_compra_servicio(precio, meses)

        # Guardar en historial
        conn = get_db_connection()
        c = conn.cursor()

        c.execute('''INSERT INTO simulaciones_historial
                    (fecha_simulacion, producto, precio_total, meses, mensualidad,
                     veredicto, saldo_inicial, saldo_final_proyectado, mes_critico, saldo_minimo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                  producto,
                  precio,
                  meses,
                  resultado['mensualidad'],
                  resultado['veredicto'],
                  resultado['saldo_inicial'],
                  resultado['saldo_final'],
                  resultado['mes_critico'],
                  resultado['saldo_minimo']))

        conn.commit()
        conn.close()

        print(f"[OK] Simulacion guardada: {producto} - ${precio:.2f} en {meses} MSI - Veredicto: {resultado['veredicto']}")

        return jsonify(resultado)

    except Exception as e:
        print(f"[ERROR] Error en simulador: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'veredicto': 'ERROR',
            'problema_mes': None
        }), 500


@msi_bp.route('/pago_anticipado_msi/<int:id>', methods=['POST'])
def pago_anticipado_msi(id):
    """Registrar pago anticipado de MSI (reducir meses restantes)"""
    try:
        meses_pagados = int(request.form.get('meses_pagados', 1))

        conn = get_db_connection()
        c = conn.cursor()

        # Obtener meses restantes actuales
        c.execute('SELECT meses_restantes FROM compras_msi WHERE id=?', (id,))
        result = c.fetchone()

        if not result:
            flash('Compra MSI no encontrada', 'error')
            return redirect('/')

        meses_restantes = result[0]
        nuevos_meses = max(0, meses_restantes - meses_pagados)

        # Actualizar
        c.execute('UPDATE compras_msi SET meses_restantes=? WHERE id=?', (nuevos_meses, id))

        # Si llega a 0, desactivar
        if nuevos_meses == 0:
            c.execute('UPDATE compras_msi SET activo=0 WHERE id=?', (id,))

        conn.commit()
        conn.close()

        flash(f'Pago anticipado registrado: {meses_pagados} meses', 'success')
        print(f"[OK] Pago anticipado registrado: {meses_pagados} meses")

    except Exception as e:
        flash(f'Error al registrar pago anticipado: {str(e)}', 'error')
        print(f"[ERROR] Error al registrar pago anticipado: {str(e)}")

    return redirect('/')


@msi_bp.route('/desactivar_msi/<int:id>')
def desactivar_msi(id):
    """Desactivar una compra MSI"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('UPDATE compras_msi SET activo=0 WHERE id=?', (id,))
        conn.commit()
        conn.close()

        flash('Compra MSI desactivada', 'success')
        print(f"[OK] Compra MSI {id} desactivada")

    except Exception as e:
        flash(f'Error al desactivar compra MSI: {str(e)}', 'error')
        print(f"[ERROR] Error al desactivar compra MSI: {str(e)}")

    return redirect('/')


@msi_bp.route('/borrar_msi/<int:id>')
def borrar_msi(id):
    """Borrar completamente una compra MSI"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM compras_msi WHERE id=?', (id,))
        conn.commit()
        conn.close()

        flash('Compra MSI eliminada', 'success')
        print(f"[OK] Compra MSI {id} eliminada")

    except Exception as e:
        flash(f'Error al eliminar compra MSI: {str(e)}', 'error')
        print(f"[ERROR] Error al eliminar compra MSI: {str(e)}")

    return redirect('/')
