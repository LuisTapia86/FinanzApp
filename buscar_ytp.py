# -*- coding: utf-8 -*-
import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=== BUSCANDO YTP ===\n")

# Buscar en tarjetas
print("En tarjetas_credito:")
c.execute('SELECT * FROM tarjetas_credito WHERE nombre LIKE "%YTP%" OR nombre LIKE "%ytp%"')
tarjetas = c.fetchall()
if tarjetas:
    for t in tarjetas:
        print(f"ID {t['id']}: {t['nombre']} | Pago día {t['fecha_pago_estimada']} | Activo: {t['activo']}")
else:
    print("No encontrada")

# Buscar en gastos
print("\nEn gastos_tdc:")
c.execute('SELECT * FROM gastos_tdc WHERE concepto LIKE "%YTP%" OR concepto LIKE "%ytp%"')
gastos = c.fetchall()
if gastos:
    for g in gastos:
        print(f"ID {g['id']}: {g['concepto']} | ${g['monto']:.2f} | Tarjeta ID: {g['tarjeta_id']}")
else:
    print("No encontrado")

# Buscar en MSI
print("\nEn compras_msi:")
c.execute('SELECT * FROM compras_msi WHERE producto LIKE "%YTP%" OR producto LIKE "%ytp%"')
msis = c.fetchall()
if msis:
    for m in msis:
        print(f"ID {m['id']}: {m['producto']} | ${m['mensualidad']:.2f}/mes | Tarjeta ID: {m['tarjeta_id']}")
else:
    print("No encontrado")

# Mostrar TODAS las tarjetas
print("\n" + "="*70)
print("TODAS LAS TARJETAS REGISTRADAS:")
print("="*70)
c.execute('SELECT id, nombre, fecha_pago_estimada, activo FROM tarjetas_credito ORDER BY id')
todas = c.fetchall()
for t in todas:
    estado = "ACTIVO" if t['activo'] == 1 else "INACTIVO"
    print(f"ID {t['id']}: {t['nombre']:20s} | Día pago: {t['fecha_pago_estimada']:>2} | {estado}")

conn.close()
