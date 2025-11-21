# -*- coding: utf-8 -*-
import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=== TODOS los gastos Banamex (activos e inactivos) ===")
c.execute('SELECT id, fecha, concepto, monto, activo FROM gastos_tdc WHERE tarjeta_id=5 ORDER BY id')
gastos = c.fetchall()
for g in gastos:
    estado = "ACTIVO" if g['activo'] == 1 else "INACTIVO"
    print(f"ID {g['id']}: {g['fecha']} | {g['concepto']} | ${g['monto']:.2f} | {estado}")

conn.close()
