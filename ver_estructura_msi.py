# -*- coding: utf-8 -*-
import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=== ESTRUCTURA COMPLETA DE MSI ===")
c.execute('PRAGMA table_info(compras_msi)')
columnas = c.fetchall()
for col in columnas:
    print(f"Columna: {col['name']} | Tipo: {col['type']} | Default: {col['dflt_value']}")

print("\n=== PRIMER MSI COMPLETO (EJEMPLO) ===")
c.execute('SELECT * FROM compras_msi WHERE activo=1 LIMIT 1')
msi = c.fetchone()
if msi:
    for key in msi.keys():
        print(f"{key}: {msi[key]}")
else:
    print("No hay MSI registrados")

conn.close()
