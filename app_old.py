# app.py - FinanzApp con Simulador y Proyecciones
from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

def init_db():
    """Inicializar base de datos"""
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    
    # Tabla de ingresos
    c.execute('''CREATE TABLE IF NOT EXISTS ingresos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  fecha TEXT,
                  concepto TEXT,
                  monto REAL)''')
    
    # Tabla de gastos
    c.execute('''CREATE TABLE IF NOT EXISTS gastos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  fecha TEXT,
                  tipo TEXT,
                  nombre TEXT,
                  monto REAL)''')
    
    # Tabla de créditos programados (pagos fijos mensuales)
    c.execute('''CREATE TABLE IF NOT EXISTS creditos_programados
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  nombre TEXT,
                  monto_mensual REAL,
                  dia_pago INTEGER,
                  fecha_inicio TEXT,
                  fecha_fin TEXT,
                  fecha_corte INTEGER,
                  fecha_limite_pago INTEGER,
                  fecha_apartado INTEGER,
                  dias_alerta INTEGER DEFAULT 3,
                  notas TEXT,
                  activo INTEGER DEFAULT 1)''')
    
    # Tabla de compras MSI
    c.execute('''CREATE TABLE IF NOT EXISTS compras_msi
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  producto TEXT,
                  precio_total REAL,
                  meses INTEGER,
                  mensualidad REAL,
                  fecha_primera_mensualidad TEXT,
                  meses_restantes INTEGER,
                  dia_pago INTEGER,
                  dias_alerta INTEGER DEFAULT 3,
                  activo INTEGER DEFAULT 1)''')
    
    # Tabla de configuración
    c.execute('''CREATE TABLE IF NOT EXISTS configuracion
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  clave TEXT UNIQUE,
                  valor TEXT)''')
    
    # Tabla de ingresos recurrentes
    c.execute('''CREATE TABLE IF NOT EXISTS ingresos_recurrentes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  nombre TEXT,
                  monto REAL,
                  dia_pago INTEGER,
                  fecha_inicio TEXT,
                  fecha_fin TEXT,
                  activo INTEGER DEFAULT 1)''')
    
    # Insertar balance inicial por defecto si no existe
    c.execute("INSERT OR IGNORE INTO configuracion (clave, valor) VALUES ('balance_inicial', '0')")
    c.execute("INSERT OR IGNORE INTO configuracion (clave, valor) VALUES ('primera_vez', '1')")
    
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada")

def parse_fecha(fecha_str):
    """Parsear fecha en múltiples formatos posibles"""
    if not fecha_str or fecha_str == '2099-12-31':
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

def obtener_proximas_alertas(dias_adelante=15):
    """Obtener próximas alertas de pagos"""
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    
    # Obtener créditos activos con alertas
    c.execute('''SELECT id, nombre, monto_mensual, fecha_limite_pago, dias_alerta, notas 
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
        dias_alerta = cred[4] or 3
        
        # Calcular próxima fecha de pago (este mes o siguiente)
        for mes_offset in range(3):  # Revisar próximos 3 meses
            fecha_pago = hoy + relativedelta(months=mes_offset)
            try:
                fecha_pago = datetime(fecha_pago.year, fecha_pago.month, dia_limite)
            except ValueError:
                # Si el día no existe en ese mes (ej: 31 en febrero), usar último día
                fecha_pago = datetime(fecha_pago.year, fecha_pago.month, 1) + relativedelta(months=1, days=-1)
            
            fecha_alerta = fecha_pago - timedelta(days=dias_alerta)
            dias_para_pago = (fecha_pago - hoy).days
            
            if 0 <= dias_para_pago <= dias_adelante:
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
        dias_alerta = msi[4] or 3
        
        for mes_offset in range(3):
            fecha_pago = hoy + relativedelta(months=mes_offset)
            try:
                fecha_pago = datetime(fecha_pago.year, fecha_pago.month, dia_pago)
            except ValueError:
                fecha_pago = datetime(fecha_pago.year, fecha_pago.month, 1) + relativedelta(months=1, days=-1)
            
            dias_para_pago = (fecha_pago - hoy).days
            
            if 0 <= dias_para_pago <= dias_adelante:
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

def calcular_proyeccion_meses(meses_adelante=6):
    """Calcular proyección de saldo para los próximos X meses"""
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    
    # Obtener balance inicial
    try:
        c.execute("SELECT valor FROM configuracion WHERE clave='balance_inicial'")
        result = c.fetchone()
        saldo_actual = float(result[0]) if result else 0.0
    except:
        saldo_actual = 0.0
    
    # Obtener ingresos y gastos ya registrados
    c.execute('SELECT SUM(monto) FROM ingresos')
    total_ingresos = c.fetchone()[0] or 0
    
    c.execute('SELECT SUM(monto) FROM gastos')
    total_gastos = c.fetchone()[0] or 0
    
    # Aplicar ingresos y gastos históricos al saldo
    saldo_actual = saldo_actual + total_ingresos - total_gastos
    
    # Obtener créditos programados activos con fechas
    c.execute('SELECT nombre, monto_mensual, dia_pago, fecha_inicio, fecha_fin FROM creditos_programados WHERE activo=1')
    creditos = c.fetchall()
    
    # Obtener compras MSI activas
    c.execute('SELECT producto, mensualidad, meses_restantes, fecha_primera_mensualidad FROM compras_msi WHERE activo=1 AND meses_restantes > 0')
    msis = c.fetchall()
    
    # Obtener ingresos recurrentes activos con fechas
    c.execute('SELECT nombre, monto, dia_pago, fecha_inicio, fecha_fin FROM ingresos_recurrentes WHERE activo=1')
    ingresos_rec = c.fetchall()
    
    conn.close()
    
    # Proyectar próximos meses
    proyeccion = []
    fecha_actual = datetime.now()
    
    for i in range(meses_adelante):
        mes_futuro = fecha_actual + relativedelta(months=i)
        mes_nombre = mes_futuro.strftime('%B %Y')
        
        # Para comparación, usar solo año-mes (ignorar día)
        mes_futuro_comparacion = datetime(mes_futuro.year, mes_futuro.month, 1)
        
        # Calcular INGRESOS del mes (solo si están activos en ese mes)
        ingresos_mes = 0
        for ing in ingresos_rec:
            fecha_inicio = parse_fecha(ing[3])
            fecha_inicio_mes = datetime(fecha_inicio.year, fecha_inicio.month, 1)
            
            fecha_fin = parse_fecha(ing[4])
            fecha_fin_mes = datetime(fecha_fin.year, fecha_fin.month, 1)
            
            # Solo aplicar si el mes está dentro del rango
            if fecha_inicio_mes <= mes_futuro_comparacion <= fecha_fin_mes:
                ingresos_mes += ing[1]
        
        # Calcular GASTOS del mes (solo créditos activos en ese mes)
        pago_creditos = 0
        for cred in creditos:
            fecha_inicio = parse_fecha(cred[3])
            fecha_inicio_mes = datetime(fecha_inicio.year, fecha_inicio.month, 1)
            
            fecha_fin = parse_fecha(cred[4])
            fecha_fin_mes = datetime(fecha_fin.year, fecha_fin.month, 1)
            
            # Solo aplicar si el mes está dentro del rango
            if fecha_inicio_mes <= mes_futuro_comparacion <= fecha_fin_mes:
                pago_creditos += cred[1]
        
        # Calcular pagos MSI (solo los que ya empezaron)
        pago_msis = 0
        for msi in msis:
            fecha_primera = parse_fecha(msi[3])
            fecha_primera_mes = datetime(fecha_primera.year, fecha_primera.month, 1)
            
            # Verificar si este mes ya debe pagar
            meses_desde_inicio = (mes_futuro_comparacion.year - fecha_primera_mes.year) * 12 + (mes_futuro_comparacion.month - fecha_primera_mes.month)
            
            if meses_desde_inicio >= 0 and meses_desde_inicio < msi[2]:
                pago_msis += msi[1]
        
        pago_total_mes = pago_creditos + pago_msis
        
        # Actualizar saldo: + ingresos - gastos
        saldo_actual = saldo_actual + ingresos_mes - pago_total_mes
        
        # Determinar estado (semáforo)
        if saldo_actual > 10000:
            estado = "verde"
        elif saldo_actual > 0:
            estado = "amarillo"
        else:
            estado = "rojo"
        
        proyeccion.append({
            'mes': mes_nombre,
            'ingresos_mes': ingresos_mes,
            'pago_total': pago_total_mes,
            'saldo_estimado': saldo_actual,
            'estado': estado
        })
    
    return proyeccion

@app.route('/')
def home():
    """Página principal con dashboard"""
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    
    # Obtener configuración (con valores por defecto si no existen)
    try:
        c.execute("SELECT valor FROM configuracion WHERE clave='balance_inicial'")
        result = c.fetchone()
        balance_inicial = float(result[0]) if result else 0.0
    except:
        balance_inicial = 0.0
    
    try:
        c.execute("SELECT valor FROM configuracion WHERE clave='primera_vez'")
        result = c.fetchone()
        primera_vez = int(result[0]) if result else 1
    except:
        primera_vez = 1
    
    # Datos actuales
    c.execute('SELECT * FROM ingresos ORDER BY fecha DESC LIMIT 10')
    ingresos = c.fetchall()
    
    c.execute('SELECT * FROM gastos ORDER BY fecha DESC LIMIT 10')
    gastos = c.fetchall()
    
    c.execute('SELECT SUM(monto) FROM ingresos')
    total_ingresos = c.fetchone()[0] or 0
    
    c.execute('SELECT SUM(monto) FROM gastos')
    total_gastos = c.fetchone()[0] or 0
    
    # Créditos y MSI
    c.execute('SELECT * FROM creditos_programados WHERE activo=1')
    creditos = c.fetchall()
    
    c.execute('SELECT * FROM compras_msi WHERE activo=1')
    msis = c.fetchall()
    
    # Ingresos recurrentes
    c.execute('SELECT * FROM ingresos_recurrentes WHERE activo=1')
    ingresos_recurrentes = c.fetchall()
    
    # Balance real = Balance inicial + Ingresos - Gastos
    balance = balance_inicial + total_ingresos - total_gastos
    
    conn.close()
    
    # Calcular proyección
    proyeccion = calcular_proyeccion_meses(6)
    
    # Obtener próximas alertas
    alertas = obtener_proximas_alertas(15)
    
    return render_template('index.html', 
                         ingresos=ingresos, 
                         gastos=gastos,
                         creditos=creditos,
                         msis=msis,
                         ingresos_recurrentes=ingresos_recurrentes,
                         balance_inicial=balance_inicial,
                         total_ingresos=total_ingresos,
                         total_gastos=total_gastos,
                         balance=balance,
                         primera_vez=primera_vez,
                         proyeccion=proyeccion,
                         alertas=alertas)

@app.route('/agregar_ingreso', methods=['POST'])
def agregar_ingreso():
    """Agregar nuevo ingreso"""
    fecha = request.form.get('fecha', '')
    concepto = request.form.get('concepto', '')
    monto = float(request.form.get('monto', 0))
    
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    c.execute('INSERT INTO ingresos (fecha, concepto, monto) VALUES (?, ?, ?)',
              (fecha, concepto, monto))
    conn.commit()
    conn.close()
    
    return redirect('/')

@app.route('/agregar_gasto', methods=['POST'])
def agregar_gasto():
    """Agregar nuevo gasto (o compra MSI si está marcado)"""
    fecha = request.form.get('fecha', '')
    tipo = request.form.get('tipo', 'efectivo')
    nombre = request.form.get('nombre', '')
    monto = float(request.form.get('monto', 0))
    es_msi = request.form.get('es_msi', '0')  # '1' si está marcado, None/'' si no

    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()

    # Si es compra MSI, guardar en tabla compras_msi
    if es_msi == '1':
        meses = int(request.form.get('meses_msi', 3))
        fecha_primera = request.form.get('fecha_primera_msi', fecha)  # Si no hay fecha MSI, usar fecha del gasto

        # Si fecha_primera está vacía, usar la fecha del gasto
        if not fecha_primera:
            fecha_primera = fecha

        mensualidad = monto / meses

        # Insertar en compras_msi
        c.execute('''INSERT INTO compras_msi
                     (producto, precio_total, meses, mensualidad, fecha_primera_mensualidad, meses_restantes)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (nombre, monto, meses, mensualidad, fecha_primera, meses))

        print(f"💳 Compra MSI agregada: {nombre} - ${monto} en {meses} meses (${mensualidad:.2f}/mes)")
    else:
        # Gasto normal
        c.execute('INSERT INTO gastos (fecha, tipo, nombre, monto) VALUES (?, ?, ?, ?)',
                  (fecha, tipo, nombre, monto))

        print(f"💸 Gasto agregado: {nombre} - ${monto}")

    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/borrar_ingreso/<int:id>')
def borrar_ingreso(id):
    """Borrar un ingreso específico"""
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    c.execute('DELETE FROM ingresos WHERE id=?', (id,))
    conn.commit()
    conn.close()
    
    print(f"🗑️ Ingreso {id} eliminado")
    return redirect('/')

@app.route('/borrar_gasto/<int:id>')
def borrar_gasto(id):
    """Borrar un gasto específico"""
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    c.execute('DELETE FROM gastos WHERE id=?', (id,))
    conn.commit()
    conn.close()
    
    print(f"🗑️ Gasto {id} eliminado")
    return redirect('/')

@app.route('/agregar_credito', methods=['POST'])
def agregar_credito():
    """Agregar crédito programado"""
    nombre = request.form.get('nombre', '')
    monto = float(request.form.get('monto', 0))
    dia_pago = int(request.form.get('dia_pago', 1))
    fecha_inicio = request.form.get('fecha_inicio', '')
    fecha_fin = request.form.get('fecha_fin', '2099-12-31')

    # Nuevos campos opcionales
    fecha_corte = int(request.form.get('fecha_corte', 0))
    fecha_limite_pago = int(request.form.get('fecha_limite_pago', dia_pago))
    fecha_apartado = int(request.form.get('fecha_apartado', dia_pago))
    dias_alerta = int(request.form.get('dias_alerta', 3))
    notas = request.form.get('notas', '')

    # Si fecha_inicio está vacía, calcular inteligentemente
    if not fecha_inicio or fecha_inicio.strip() == '':
        hoy = datetime.now()

        # Si el día límite de pago de este mes ya pasó, empezar el siguiente mes
        if hoy.day > fecha_limite_pago:
            # Empezar el mes siguiente
            fecha_inicio_calculada = hoy + relativedelta(months=1)
            try:
                fecha_inicio = datetime(fecha_inicio_calculada.year, fecha_inicio_calculada.month, fecha_limite_pago).strftime('%Y-%m-%d')
            except ValueError:
                ultimo_dia = (datetime(fecha_inicio_calculada.year, fecha_inicio_calculada.month, 1) + relativedelta(months=1, days=-1)).day
                fecha_inicio = datetime(fecha_inicio_calculada.year, fecha_inicio_calculada.month, ultimo_dia).strftime('%Y-%m-%d')
        else:
            # Empezar este mes
            try:
                fecha_inicio = datetime(hoy.year, hoy.month, fecha_limite_pago).strftime('%Y-%m-%d')
            except ValueError:
                ultimo_dia = (datetime(hoy.year, hoy.month, 1) + relativedelta(months=1, days=-1)).day
                fecha_inicio = datetime(hoy.year, hoy.month, ultimo_dia).strftime('%Y-%m-%d')

    # Si fecha_fin está vacía, usar fecha indefinida
    if not fecha_fin or fecha_fin.strip() == '':
        fecha_fin = '2099-12-31'
    
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    c.execute('''INSERT INTO creditos_programados 
                 (nombre, monto_mensual, dia_pago, fecha_inicio, fecha_fin, 
                  fecha_corte, fecha_limite_pago, fecha_apartado, dias_alerta, notas) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (nombre, monto, dia_pago, fecha_inicio, fecha_fin,
               fecha_corte, fecha_limite_pago, fecha_apartado, dias_alerta, notas))
    conn.commit()
    conn.close()
    
    return redirect('/')

@app.route('/simular_compra', methods=['POST'])
def simular_compra():
    """Simular compra en MSI y ver impacto"""
    data = request.json
    precio = float(data['precio'])
    meses = int(data['meses'])
    
    mensualidad = precio / meses
    
    # Calcular proyección actual
    proyeccion_actual = calcular_proyeccion_meses(meses)
    
    # Simular con la nueva compra
    proyeccion_con_compra = []
    for i, mes in enumerate(proyeccion_actual):
        nuevo_saldo = mes['saldo_estimado'] - (mensualidad * (i + 1))
        
        if nuevo_saldo > 10000:
            estado = "verde"
        elif nuevo_saldo > 0:
            estado = "amarillo"
        else:
            estado = "rojo"
        
        proyeccion_con_compra.append({
            'mes': mes['mes'],
            'saldo_sin_compra': mes['saldo_estimado'],
            'saldo_con_compra': nuevo_saldo,
            'estado': estado,
            'diferencia': mensualidad
        })
    
    # Determinar veredicto
    problema_en_mes = None
    for i, p in enumerate(proyeccion_con_compra):
        if p['estado'] == 'rojo':
            problema_en_mes = i
            break
    
    if problema_en_mes is not None and problema_en_mes < 3:
        veredicto = "NO"
    elif problema_en_mes is not None:
        veredicto = "CUIDADO"
    else:
        veredicto = "SI"
    
    return jsonify({
        'mensualidad': mensualidad,
        'proyeccion': proyeccion_con_compra,
        'veredicto': veredicto,
        'problema_mes': problema_en_mes
    })

@app.route('/agregar_compra_msi', methods=['POST'])
def agregar_compra_msi():
    """Agregar compra en MSI confirmada"""
    producto = request.form.get('producto', '')
    precio = float(request.form.get('precio', 0))
    meses = int(request.form.get('meses', 3))
    fecha_primera = request.form.get('fecha_primera', '')

    # Si fecha_primera está vacía, usar fecha actual
    if not fecha_primera or fecha_primera.strip() == '':
        fecha_primera = datetime.now().strftime('%Y-%m-%d')

    mensualidad = precio / meses
    
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    c.execute('INSERT INTO compras_msi (producto, precio_total, meses, mensualidad, fecha_primera_mensualidad, meses_restantes) VALUES (?, ?, ?, ?, ?, ?)',
              (producto, precio, meses, mensualidad, fecha_primera, meses))
    conn.commit()
    conn.close()
    
    return redirect('/')

@app.route('/desactivar_credito/<int:id>')
def desactivar_credito(id):
    """Desactivar un crédito (cuando se paga anticipadamente)"""
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    c.execute('UPDATE creditos_programados SET activo=0 WHERE id=?', (id,))
    conn.commit()
    conn.close()
    
    print(f"✅ Crédito {id} desactivado")
    return redirect('/')

@app.route('/borrar_credito/<int:id>')
def borrar_credito(id):
    """Borrar completamente un crédito"""
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    c.execute('DELETE FROM creditos_programados WHERE id=?', (id,))
    conn.commit()
    conn.close()
    
    print(f"🗑️ Crédito {id} eliminado")
    return redirect('/')

@app.route('/desactivar_msi/<int:id>')
def desactivar_msi(id):
    """Desactivar compra MSI (cuando se liquida anticipadamente)"""
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    c.execute('UPDATE compras_msi SET activo=0 WHERE id=?', (id,))
    conn.commit()
    conn.close()
    
    print(f"✅ Compra MSI {id} desactivada")
    return redirect('/')

@app.route('/borrar_msi/<int:id>')
def borrar_msi(id):
    """Borrar completamente una compra MSI"""
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    c.execute('DELETE FROM compras_msi WHERE id=?', (id,))
    conn.commit()
    conn.close()
    
    print(f"🗑️ Compra MSI {id} eliminada")
    return redirect('/')

@app.route('/pago_anticipado_msi/<int:id>', methods=['POST'])
def pago_anticipado_msi(id):
    """Registrar pago anticipado de MSI (reducir meses restantes)"""
    meses_pagados = int(request.form.get('meses_pagados', 1))
    
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    
    # Obtener meses restantes actuales
    c.execute('SELECT meses_restantes FROM compras_msi WHERE id=?', (id,))
    meses_actuales = c.fetchone()[0]
    
    nuevos_meses = max(0, meses_actuales - meses_pagados)
    
    if nuevos_meses == 0:
        # Si ya no quedan meses, desactivar
        c.execute('UPDATE compras_msi SET meses_restantes=0, activo=0 WHERE id=?', (id,))
    else:
        c.execute('UPDATE compras_msi SET meses_restantes=? WHERE id=?', (nuevos_meses, id))
    
    conn.commit()
    conn.close()
    
    print(f"💰 Pago anticipado registrado: {meses_pagados} meses")
    return redirect('/')

@app.route('/configurar_balance_inicial', methods=['POST'])
def configurar_balance_inicial():
    """Configurar balance inicial"""
    balance = float(request.form.get('balance', 0))
    
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    
    c.execute("UPDATE configuracion SET valor=? WHERE clave='balance_inicial'", (str(balance),))
    c.execute("UPDATE configuracion SET valor='0' WHERE clave='primera_vez'")
    
    conn.commit()
    conn.close()
    
    print(f"💰 Balance inicial configurado: ${balance}")
    return redirect('/')

@app.route('/editar_balance_inicial', methods=['POST'])
def editar_balance_inicial():
    """Editar balance inicial"""
    balance = float(request.form.get('balance', 0))
    
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    c.execute("UPDATE configuracion SET valor=? WHERE clave='balance_inicial'", (str(balance),))
    conn.commit()
    conn.close()
    
    print(f"✏️ Balance inicial actualizado: ${balance}")
    return redirect('/')

@app.route('/agregar_ingreso_recurrente', methods=['POST'])
def agregar_ingreso_recurrente():
    """Agregar ingreso recurrente (quincenal/mensual)"""
    nombre = request.form.get('nombre', '')
    monto = float(request.form.get('monto', 0))
    dia_pago = int(request.form.get('dia_pago', 1))
    fecha_inicio = request.form.get('fecha_inicio', '')
    fecha_fin = request.form.get('fecha_fin', '')

    # Validar que fecha_inicio no esté vacía
    if not fecha_inicio or fecha_inicio.strip() == '':
        # Si está vacía, calcular inteligentemente basándose en el día de pago
        hoy = datetime.now()

        # Si el día de pago de este mes ya pasó, empezar el siguiente mes
        if hoy.day > dia_pago:
            # Empezar el mes siguiente
            fecha_inicio_calculada = hoy + relativedelta(months=1)
            # Ajustar al día de pago, manejando días inválidos (ej: 31 en febrero)
            try:
                fecha_inicio = datetime(fecha_inicio_calculada.year, fecha_inicio_calculada.month, dia_pago).strftime('%Y-%m-%d')
            except ValueError:
                # Si el día no existe en ese mes, usar el último día del mes
                ultimo_dia = (datetime(fecha_inicio_calculada.year, fecha_inicio_calculada.month, 1) + relativedelta(months=1, days=-1)).day
                fecha_inicio = datetime(fecha_inicio_calculada.year, fecha_inicio_calculada.month, ultimo_dia).strftime('%Y-%m-%d')
        else:
            # Empezar este mes
            try:
                fecha_inicio = datetime(hoy.year, hoy.month, dia_pago).strftime('%Y-%m-%d')
            except ValueError:
                # Si el día no existe en este mes, usar el último día del mes
                ultimo_dia = (datetime(hoy.year, hoy.month, 1) + relativedelta(months=1, days=-1)).day
                fecha_inicio = datetime(hoy.year, hoy.month, ultimo_dia).strftime('%Y-%m-%d')

    # Si fecha_fin está vacía, usar fecha indefinida (hasta el fin de los tiempos)
    if not fecha_fin or fecha_fin.strip() == '':
        fecha_fin = '2099-12-31'

    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    c.execute('INSERT INTO ingresos_recurrentes (nombre, monto, dia_pago, fecha_inicio, fecha_fin) VALUES (?, ?, ?, ?, ?)',
              (nombre, monto, dia_pago, fecha_inicio, fecha_fin))
    conn.commit()
    conn.close()

    print(f"💰 Ingreso recurrente agregado: {nombre} - ${monto} cada día {dia_pago} (desde {fecha_inicio} hasta {fecha_fin})")
    return redirect('/')

@app.route('/desactivar_ingreso_recurrente/<int:id>')
def desactivar_ingreso_recurrente(id):
    """Desactivar un ingreso recurrente"""
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    c.execute('UPDATE ingresos_recurrentes SET activo=0 WHERE id=?', (id,))
    conn.commit()
    conn.close()
    
    print(f"⏸️ Ingreso recurrente {id} desactivado")
    return redirect('/')

@app.route('/borrar_ingreso_recurrente/<int:id>')
def borrar_ingreso_recurrente(id):
    """Borrar completamente un ingreso recurrente"""
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()
    c.execute('DELETE FROM ingresos_recurrentes WHERE id=?', (id,))
    conn.commit()
    conn.close()

    print(f"🗑️ Ingreso recurrente {id} eliminado")
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    """Dashboard con análisis y gráficas interactivas"""
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()

    # Obtener balance inicial
    try:
        c.execute("SELECT valor FROM configuracion WHERE clave='balance_inicial'")
        result = c.fetchone()
        balance_inicial = float(result[0]) if result else 0.0
    except:
        balance_inicial = 0.0

    # Totales generales
    c.execute('SELECT SUM(monto) FROM ingresos')
    total_ingresos = c.fetchone()[0] or 0

    c.execute('SELECT SUM(monto) FROM gastos')
    total_gastos = c.fetchone()[0] or 0

    balance_actual = balance_inicial + total_ingresos - total_gastos

    # Ingresos por mes (últimos 6 meses)
    c.execute('''SELECT strftime('%Y-%m', fecha) as mes, SUM(monto)
                 FROM ingresos
                 GROUP BY mes
                 ORDER BY mes DESC
                 LIMIT 6''')
    ingresos_por_mes = c.fetchall()

    # Gastos por mes (últimos 6 meses)
    c.execute('''SELECT strftime('%Y-%m', fecha) as mes, SUM(monto)
                 FROM gastos
                 GROUP BY mes
                 ORDER BY mes DESC
                 LIMIT 6''')
    gastos_por_mes = c.fetchall()

    # Gastos por tipo
    c.execute('''SELECT tipo, SUM(monto)
                 FROM gastos
                 GROUP BY tipo
                 ORDER BY SUM(monto) DESC''')
    gastos_por_tipo = c.fetchall()

    # Top 5 gastos
    c.execute('''SELECT nombre, monto, fecha
                 FROM gastos
                 ORDER BY monto DESC
                 LIMIT 5''')
    top_gastos = c.fetchall()

    # Ingresos recurrentes activos
    c.execute('SELECT nombre, monto FROM ingresos_recurrentes WHERE activo=1')
    ingresos_recurrentes = c.fetchall()

    # Créditos activos
    c.execute('SELECT nombre, monto_mensual FROM creditos_programados WHERE activo=1')
    creditos_activos = c.fetchall()

    # MSI activos
    c.execute('''SELECT producto, mensualidad, meses_restantes
                 FROM compras_msi
                 WHERE activo=1 AND meses_restantes > 0''')
    msis_activos = c.fetchall()

    # Calcular proyección
    proyeccion = calcular_proyeccion_meses(6)

    conn.close()

    return render_template('dashboard.html',
                         balance_inicial=balance_inicial,
                         total_ingresos=total_ingresos,
                         total_gastos=total_gastos,
                         balance_actual=balance_actual,
                         ingresos_por_mes=ingresos_por_mes,
                         gastos_por_mes=gastos_por_mes,
                         gastos_por_tipo=gastos_por_tipo,
                         top_gastos=top_gastos,
                         ingresos_recurrentes=ingresos_recurrentes,
                         creditos_activos=creditos_activos,
                         msis_activos=msis_activos,
                         proyeccion=proyeccion)

if __name__ == '__main__':
    init_db()
    print("🚀 Iniciando FinanzApp Mejorada...")
    print("📍 Abre tu navegador en: http://127.0.0.1:5000")
    app.run(debug=True)