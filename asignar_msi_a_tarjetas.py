# -*- coding: utf-8 -*-
"""
Script para asignar MSI a sus tarjetas correspondientes
Banamex Oro (ID 5): $1664.79 y $151.27
Resto: AMEX (ID 4)
"""
import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=== MSI ACTUALES ===")
c.execute('SELECT id, producto, mensualidad, tarjeta_id FROM compras_msi WHERE activo=1')
msis = c.fetchall()
for msi in msis:
    print(f"ID {msi['id']}: {msi['producto']} - ${msi['mensualidad']:.2f} - Tarjeta: {msi['tarjeta_id']}")

print("\n=== ASIGNANDO TARJETAS ===")

# Los 2 seguros auto van en Banamex Oro (ID 5)
c.execute('UPDATE compras_msi SET tarjeta_id=5 WHERE producto LIKE "%SEGURO AUTO%" AND activo=1')
actualizados = c.rowcount
print(f"Seguros Auto -> Banamex Oro (ID 5): {actualizados} MSI")

# El resto va en AMEX (ID 4)
c.execute('UPDATE compras_msi SET tarjeta_id=4 WHERE tarjeta_id IS NULL AND activo=1')
actualizados = c.rowcount
print(f"Resto -> AMEX (ID 4): {actualizados} MSI")

conn.commit()

print("\n=== MSI ACTUALIZADOS ===")
c.execute('SELECT id, producto, mensualidad, tarjeta_id FROM compras_msi WHERE activo=1 ORDER BY tarjeta_id')
msis = c.fetchall()
for msi in msis:
    tarjeta_nombre = "AMEX" if msi['tarjeta_id'] == 4 else "Banamex Oro" if msi['tarjeta_id'] == 5 else "SIN ASIGNAR"
    print(f"ID {msi['id']}: {msi['producto']} - ${msi['mensualidad']:.2f} - {tarjeta_nombre}")

conn.close()
print("\n[OK] MSI asignados a tarjetas")
