# -*- coding: utf-8 -*-
import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=== ESTRUCTURA tarjetas_credito ===")
c.execute('PRAGMA table_info(tarjetas_credito)')
for col in c.fetchall():
    print(f"{col['name']} | {col['type']}")

print("\n=== TARJETAS REGISTRADAS ===")
c.execute('SELECT * FROM tarjetas_credito')
tarjetas = c.fetchall()
for t in tarjetas:
    print(f"\nID: {t['id']}")
    for key in t.keys():
        print(f"  {key}: {t[key]}")

print("\n=== ESTRUCTURA gastos_tdc ===")
c.execute('PRAGMA table_info(gastos_tdc)')
for col in c.fetchall():
    print(f"{col['name']} | {col['type']}")

print("\n=== GASTOS TDC REGISTRADOS ===")
c.execute('SELECT * FROM gastos_tdc')
gastos = c.fetchall()
for g in gastos:
    print(f"\nID: {g['id']}")
    for key in g.keys():
        print(f"  {key}: {g[key]}")

conn.close()
