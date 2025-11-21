# -*- coding: utf-8 -*-
import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=== GASTOS TDC REGISTRADOS ===")
c.execute('SELECT fecha, tipo, nombre, monto FROM gastos WHERE tipo="tdc" ORDER BY fecha DESC LIMIT 30')
gastos = c.fetchall()
for row in gastos:
    print(f"{row['fecha']} | {row['nombre']} | ${row['monto']:.2f}")

print("\n=== CREDITOS PROGRAMADOS (TODOS) ===")
c.execute('SELECT id, nombre, monto_mensual, dia_pago, activo FROM creditos_programados')
creditos = c.fetchall()
for row in creditos:
    estado = "ACTIVO" if row['activo'] == 1 else "INACTIVO"
    print(f"ID: {row['id']} | {row['nombre']} | ${row['monto_mensual']:.2f} | Día: {row['dia_pago']} | {estado}")

conn.close()
