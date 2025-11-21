# -*- coding: utf-8 -*-
"""
Migrar MSI de compras_msi a gastos_tdc
Los MSI deben estar en gastos_tdc con tipo='msi' y tarjeta_id
"""
import sqlite3
from config import Config
from datetime import datetime

conn = sqlite3.connect(Config.DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=" * 70)
print("MIGRACION: compras_msi a gastos_tdc")
print("=" * 70)

# Obtener todos los MSI activos de compras_msi
c.execute('SELECT * FROM compras_msi WHERE activo=1')
msis = c.fetchall()

print(f"\nMSI a migrar: {len(msis)}")

migrados = 0
errores = 0

for msi in msis:
    try:
        # Datos del MSI
        producto = msi['producto']
        precio_total = msi['precio_total']
        meses = msi['meses']
        mensualidad = msi['mensualidad']
        meses_restantes = msi['meses_restantes']
        tarjeta_id = msi['tarjeta_id']
        fecha_primera = msi['fecha_primera_mensualidad']

        if not tarjeta_id:
            print(f"  [ERROR] {producto} no tiene tarjeta_id asignado")
            errores += 1
            continue

        # Insertar en gastos_tdc
        c.execute('''INSERT INTO gastos_tdc
                     (tarjeta_id, fecha, concepto, monto, tipo, meses_msi, mensualidad_msi, meses_restantes, activo, usuario_id)
                     VALUES (?, ?, ?, ?, 'msi', ?, ?, ?, 1, 1)''',
                  (tarjeta_id, fecha_primera, producto, precio_total, meses, mensualidad, meses_restantes))

        print(f"  [OK] {producto} -> Tarjeta ID {tarjeta_id} (${mensualidad:.2f}/mes)")
        migrados += 1

    except Exception as e:
        print(f"  [ERROR] {producto}: {e}")
        errores += 1

# Desactivar los MSI de compras_msi (no borrar por seguridad)
c.execute('UPDATE compras_msi SET activo=0 WHERE activo=1')

conn.commit()
conn.close()

print(f"\n" + "=" * 70)
print(f"RESULTADO:")
print(f"  Migrados exitosamente: {migrados}")
print(f"  Errores: {errores}")
print(f"  MSI en compras_msi desactivados")
print("=" * 70)
