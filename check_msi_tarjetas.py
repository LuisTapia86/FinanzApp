# -*- coding: utf-8 -*-
import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=== TARJETAS (creditos_programados) ===")
c.execute('SELECT id, nombre, monto_mensual, dia_pago FROM creditos_programados WHERE activo=1')
tarjetas = c.fetchall()
for row in tarjetas:
    print(f"ID: {row['id']} | {row['nombre']} | ${row['monto_mensual']:.2f} | Día pago: {row['dia_pago']}")

print("\n=== MSI (compras_msi) ===")
c.execute('SELECT id, producto, mensualidad, dia_pago, tarjeta_id FROM compras_msi WHERE activo=1')
msis = c.fetchall()
for row in msis:
    tarjeta = row['tarjeta_id'] if row['tarjeta_id'] else 'SIN VINCULAR'
    print(f"ID: {row['id']} | {row['producto']} | ${row['mensualidad']:.2f}/mes | Día: {row['dia_pago']} | Tarjeta ID: {tarjeta}")

conn.close()
