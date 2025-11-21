# -*- coding: utf-8 -*-
"""
AUDITORÍA COMPLETA DEL SISTEMA
Verificar que todas las relaciones y cálculos estén correctos
"""
import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=" * 80)
print("AUDITORÍA COMPLETA DE FINANZAPP")
print("=" * 80)

# 1. VERIFICAR ESQUEMA DE TABLAS Y RELACIONES
print("\n1. ESQUEMA DE TABLAS Y RELACIONES")
print("-" * 80)

print("\n--- compras_msi ---")
c.execute('PRAGMA table_info(compras_msi)')
cols_msi = c.fetchall()
tiene_tarjeta_id = False
for col in cols_msi:
    print(f"  {col['name']:30s} {col['type']:10s}")
    if col['name'] == 'tarjeta_id':
        tiene_tarjeta_id = True

if tiene_tarjeta_id:
    print("  [OK] Tiene tarjeta_id para vincular con tarjetas_credito")
else:
    print("  [ERROR] NO tiene tarjeta_id")

print("\n--- gastos_tdc ---")
c.execute('PRAGMA table_info(gastos_tdc)')
cols_tdc = c.fetchall()
tiene_tarjeta_id_tdc = False
for col in cols_tdc:
    print(f"  {col['name']:30s} {col['type']:10s}")
    if col['name'] == 'tarjeta_id':
        tiene_tarjeta_id_tdc = True

if tiene_tarjeta_id_tdc:
    print("  [OK] Tiene tarjeta_id para vincular con tarjetas_credito")
else:
    print("  [X] ERROR: NO tiene tarjeta_id")

print("\n--- tarjetas_credito ---")
c.execute('PRAGMA table_info(tarjetas_credito)')
cols_tarjetas = c.fetchall()
for col in cols_tarjetas:
    print(f"  {col['name']:30s} {col['type']:10s}")

print("\n--- prestamos ---")
c.execute('PRAGMA table_info(prestamos)')
cols_prestamos = c.fetchall()
for col in cols_prestamos:
    print(f"  {col['name']:30s} {col['type']:10s}")

# 2. VERIFICAR INTEGRIDAD DE DATOS
print("\n\n2. INTEGRIDAD DE DATOS")
print("-" * 80)

# MSI sin tarjeta
c.execute('SELECT COUNT(*) FROM compras_msi WHERE activo=1 AND tarjeta_id IS NULL')
msi_sin_tarjeta = c.fetchone()[0]
if msi_sin_tarjeta > 0:
    print(f"  [X] HAY {msi_sin_tarjeta} MSI ACTIVOS SIN TARJETA ASIGNADA")
    c.execute('SELECT id, producto, mensualidad FROM compras_msi WHERE activo=1 AND tarjeta_id IS NULL')
    for row in c.fetchall():
        print(f"    - ID {row['id']}: {row['producto']} ${row['mensualidad']:.2f}/mes")
else:
    print(f"  [OK] Todos los MSI activos tienen tarjeta asignada")

# Gastos TDC sin tarjeta
c.execute('SELECT COUNT(*) FROM gastos_tdc WHERE activo=1 AND tarjeta_id IS NULL')
gastos_sin_tarjeta = c.fetchone()[0]
if gastos_sin_tarjeta > 0:
    print(f"  [X] HAY {gastos_sin_tarjeta} GASTOS TDC ACTIVOS SIN TARJETA")
else:
    print(f"  [OK] Todos los gastos TDC tienen tarjeta asignada")

# 3. VERIFICAR CÁLCULOS
print("\n\n3. VERIFICACIÓN DE CÁLCULOS")
print("-" * 80)

# Calcular totales por tarjeta
c.execute('''SELECT
                tc.id,
                tc.nombre,
                tc.fecha_pago_estimada,
                COALESCE(SUM(gt.monto), 0) as total_gastos,
                COALESCE((SELECT SUM(cm.mensualidad)
                          FROM compras_msi cm
                          WHERE cm.tarjeta_id = tc.id AND cm.activo = 1), 0) as total_msi
             FROM tarjetas_credito tc
             LEFT JOIN gastos_tdc gt ON tc.id = gt.tarjeta_id AND gt.activo = 1
             WHERE tc.activo = 1
             GROUP BY tc.id
             ORDER BY tc.fecha_pago_estimada''')

print("\nTARJETAS (Gastos + MSI):")
total_tarjetas = 0
for t in c.fetchall():
    total = t['total_gastos'] + t['total_msi']
    total_tarjetas += total
    print(f"  {t['nombre']:20s} día {t['fecha_pago_estimada']:>2} | Gastos: ${t['total_gastos']:>8.2f} + MSI: ${t['total_msi']:>8.2f} = ${total:>10.2f}")

# Préstamos
c.execute('SELECT nombre, monto_mensual, dia_pago FROM prestamos WHERE activo=1 ORDER BY dia_pago')
print("\nPRÉSTAMOS:")
total_prestamos = 0
for p in c.fetchall():
    total_prestamos += p['monto_mensual']
    print(f"  {p['nombre']:20s} día {p['dia_pago']:>2} | ${p['monto_mensual']:>10.2f}")

print(f"\n  TOTAL MENSUAL: ${total_tarjetas + total_prestamos:>10.2f}")

# 4. VERIFICAR FUNCIONES DE PROYECCIÓN
print("\n\n4. VERIFICACIÓN DE FUNCIONES")
print("-" * 80)

# Revisar imports y exports
print("\nFunciones exportadas desde services/__init__.py:")
try:
    from services import calcular_proyeccion_meses, calcular_proyeccion_quincenal, calcular_quincenas_a_proyectar
    print("  [OK] calcular_proyeccion_meses")
    print("  [OK] calcular_proyeccion_quincenal")
    print("  [OK] calcular_quincenas_a_proyectar")
except ImportError as e:
    print(f"  [X] ERROR al importar: {e}")

# 5. VERIFICAR RUTAS DE REGISTRO
print("\n\n5. RUTAS DE REGISTRO")
print("-" * 80)

print("\nRevisando routes/msi.py:")
with open('routes/msi.py', 'r', encoding='utf-8') as f:
    contenido_msi = f.read()
    if 'tarjeta_id' in contenido_msi:
        print("  [OK] Menciona tarjeta_id")
        # Verificar si INSERT incluye tarjeta_id
        if 'INSERT INTO compras_msi' in contenido_msi:
            lineas_insert = [l for l in contenido_msi.split('\n') if 'INSERT INTO compras_msi' in l or 'VALUES' in l]
            if any('tarjeta_id' in l for l in lineas_insert):
                print("  [OK] INSERT incluye tarjeta_id")
            else:
                print("  [X] ERROR: INSERT NO incluye tarjeta_id")
    else:
        print("  [X] ERROR: NO menciona tarjeta_id")

print("\n\n6. RESUMEN")
print("=" * 80)

problemas = []

if msi_sin_tarjeta > 0:
    problemas.append(f"- {msi_sin_tarjeta} MSI sin tarjeta asignada")

if gastos_sin_tarjeta > 0:
    problemas.append(f"- {gastos_sin_tarjeta} Gastos TDC sin tarjeta")

# Verificar si la ruta de MSI incluye tarjeta_id en INSERT
if 'INSERT INTO compras_msi' in contenido_msi:
    if not any('tarjeta_id' in l for l in [l for l in contenido_msi.split('\n') if 'INSERT INTO compras_msi' in l or 'VALUES' in l]):
        problemas.append("- Ruta /agregar_compra_msi NO guarda tarjeta_id")

if problemas:
    print("\n[X] SE ENCONTRARON PROBLEMAS:")
    for p in problemas:
        print(f"  {p}")
else:
    print("\n[OK] TODO ESTÁ CORRECTO")

conn.close()
