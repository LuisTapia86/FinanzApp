# -*- coding: utf-8 -*-
import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=== TODOS LOS GASTOS ===")
c.execute('SELECT fecha, tipo, nombre, monto FROM gastos ORDER BY fecha DESC')
gastos = c.fetchall()

total = 0
por_tipo = {}

for row in gastos:
    print(f"{row['fecha']} | {row['tipo']} | {row['nombre']} | ${row['monto']:.2f}")
    total += row['monto']
    tipo = row['tipo']
    if tipo not in por_tipo:
        por_tipo[tipo] = 0
    por_tipo[tipo] += row['monto']

print(f"\n=== RESUMEN ===")
print(f"Total gastado: ${total:.2f}")
for tipo, monto in por_tipo.items():
    print(f"{tipo}: ${monto:.2f}")

conn.close()
