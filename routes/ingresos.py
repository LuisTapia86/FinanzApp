# -*- coding: utf-8 -*-
# routes/ingresos.py - Rutas de ingresos y ingresos recurrentes
from flask import request, redirect, flash
from routes import ingresos_bp
from database import get_db_connection
from utils import validar_fecha, validar_monto, validar_dia_mes, calcular_fecha_inicio_inteligente, validar_texto
from config import Config

@ingresos_bp.route('/agregar_ingreso', methods=['POST'])
def agregar_ingreso():
    """Agregar nuevo ingreso"""
    try:
        # Obtener datos del formulario
        fecha = request.form.get('fecha', '').strip()
        concepto = request.form.get('concepto', '').strip()
        monto_str = request.form.get('monto', '0')
        categoria_id = request.form.get('categoria_id', None)

        # Validar datos
        valido_fecha, fecha, error_fecha = validar_fecha(fecha, "Fecha", requerido=True)
        if not valido_fecha:
            flash(f'Error: {error_fecha}', 'error')
            return redirect('/')

        valido_concepto, concepto, error_concepto = validar_texto(concepto, "Concepto", min_length=1, max_length=200)
        if not valido_concepto:
            flash(f'Error: {error_concepto}', 'error')
            return redirect('/')

        valido_monto, monto, error_monto = validar_monto(monto_str, "Monto", minimo=0.01)
        if not valido_monto:
            flash(f'Error: {error_monto}', 'error')
            return redirect('/')

        # Insertar en la base de datos
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('INSERT INTO ingresos (fecha, concepto, monto, categoria_id) VALUES (?, ?, ?, ?)',
                  (fecha, concepto, monto, categoria_id if categoria_id else None))
        conn.commit()
        conn.close()

        flash(f'Ingreso agregado exitosamente: {concepto} - ${monto:.2f}', 'success')
        print(f"[INGRESO] {concepto} - ${monto:.2f}")

    except Exception as e:
        flash(f'Error al agregar ingreso: {str(e)}', 'error')
        print(f"[ERROR] Error al agregar ingreso: {str(e)}")

    return redirect('/')


@ingresos_bp.route('/borrar_ingreso/<int:id>')
def borrar_ingreso(id):
    """Borrar un ingreso específico"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM ingresos WHERE id=?', (id,))
        conn.commit()
        conn.close()

        flash(f'Ingreso eliminado exitosamente', 'success')
        print(f"[DELETE] Ingreso {id} eliminado")

    except Exception as e:
        flash(f'Error al eliminar ingreso: {str(e)}', 'error')
        print(f"[ERROR] Error al eliminar ingreso: {str(e)}")

    return redirect('/')


@ingresos_bp.route('/agregar_ingreso_recurrente', methods=['POST'])
def agregar_ingreso_recurrente():
    """Agregar ingreso recurrente con diferentes frecuencias"""
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        monto_str = request.form.get('monto', '0')
        dia_pago_str = request.form.get('dia_pago', '1')
        fecha_inicio = request.form.get('fecha_inicio', '').strip()
        fecha_fin = request.form.get('fecha_fin', '').strip()
        frecuencia = request.form.get('frecuencia', 'mensual')
        mes_especifico_str = request.form.get('mes_especifico', '')

        # Validar nombre
        valido_nombre, nombre, error_nombre = validar_texto(nombre, "Nombre", min_length=1, max_length=200)
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

        # Validar/calcular fecha de inicio
        if not fecha_inicio or fecha_inicio == '':
            # Calcular inteligentemente
            fecha_inicio = calcular_fecha_inicio_inteligente(dia_pago)
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

        # Validar mes específico para frecuencia anual
        mes_especifico = None
        if frecuencia == 'anual' and mes_especifico_str:
            try:
                mes_especifico = int(mes_especifico_str)
                if mes_especifico < 1 or mes_especifico > 12:
                    flash('Error: El mes debe estar entre 1 y 12', 'error')
                    return redirect('/')
            except:
                flash('Error: Mes especifico invalido', 'error')
                return redirect('/')

        # Insertar en la base de datos
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''INSERT INTO ingresos_recurrentes
                     (nombre, monto, dia_pago, fecha_inicio, fecha_fin, frecuencia, mes_especifico)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (nombre, monto, dia_pago, fecha_inicio, fecha_fin, frecuencia, mes_especifico))
        conn.commit()
        conn.close()

        # Mensaje personalizado según frecuencia
        frecuencia_texto = {
            'semanal': 'cada semana',
            'quincenal': 'cada quincena',
            'mensual': 'cada mes',
            'bimestral': 'cada 2 meses',
            'trimestral': 'cada 3 meses',
            'semestral': 'cada 6 meses',
            'anual': 'cada año'
        }.get(frecuencia, 'periodicamente')

        flash(f'Ingreso recurrente agregado: {nombre} - ${monto:.2f} {frecuencia_texto}', 'success')
        print(f"[RECURRENTE] Ingreso agregado: {nombre} - ${monto:.2f} {frecuencia_texto} (desde {fecha_inicio} hasta {fecha_fin})")

    except Exception as e:
        flash(f'Error al agregar ingreso recurrente: {str(e)}', 'error')
        print(f"[ERROR] Error al agregar ingreso recurrente: {str(e)}")

    return redirect('/')


@ingresos_bp.route('/desactivar_ingreso_recurrente/<int:id>')
def desactivar_ingreso_recurrente(id):
    """Desactivar un ingreso recurrente"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('UPDATE ingresos_recurrentes SET activo=0 WHERE id=?', (id,))
        conn.commit()
        conn.close()

        flash('Ingreso recurrente desactivado', 'success')
        print(f"[DESACTIVAR] Ingreso recurrente {id} desactivado")

    except Exception as e:
        flash(f'Error al desactivar ingreso recurrente: {str(e)}', 'error')
        print(f"[ERROR] Error al desactivar ingreso recurrente: {str(e)}")

    return redirect('/')


@ingresos_bp.route('/borrar_ingreso_recurrente/<int:id>')
def borrar_ingreso_recurrente(id):
    """Borrar completamente un ingreso recurrente"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM ingresos_recurrentes WHERE id=?', (id,))
        conn.commit()
        conn.close()

        flash('Ingreso recurrente eliminado', 'success')
        print(f"[DELETE] Ingreso recurrente {id} eliminado")

    except Exception as e:
        flash(f'Error al eliminar ingreso recurrente: {str(e)}', 'error')
        print(f"[ERROR] Error al eliminar ingreso recurrente: {str(e)}")

    return redirect('/')
