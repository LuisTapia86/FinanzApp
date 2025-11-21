# -*- coding: utf-8 -*-
import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=" * 70)
print("BANAMEX ORO (ID: 5) - DETALLE COMPLETO")
print("=" * 70)

print("\n=== GASTOS CORRIENTES ===")
c.execute('SELECT id, fecha, concepto, monto FROM gastos_tdc WHERE tarjeta_id=5 AND activo=1')
gastos = c.fetchall()
total_gastos = 0
for g in gastos:
    print(f"ID {g['id']}: {g['fecha']} | {g['concepto']} | ${g['monto']:.2f}")
    total_gastos += g['monto']
print(f"SUBTOTAL GASTOS: ${total_gastos:.2f}")

print("\n=== MSI ===")
c.execute('SELECT id, producto, mensualidad, meses_restantes FROM compras_msi WHERE tarjeta_id=5 AND activo=1')
msis = c.fetchall()
total_msi = 0
for m in msis:
    print(f"ID {m['id']}: {m['producto']} | ${m['mensualidad']:.2f}/mes | {m['meses_restantes']} meses")
    total_msi += m['mensualidad']
print(f"SUBTOTAL MSI: ${total_msi:.2f}")

print(f"\n{'='*70}")
print(f"TOTAL BANAMEX ORO: ${total_gastos + total_msi:.2f}")
print(f"{'='*70}")

print(f"\nEsperabas:")
print(f"  Gasto corriente: $2821.70")
print(f"  MSI 1: $1664.79")
print(f"  MSI 2: $151.27")
print(f"  Total: ${2821.70 + 1664.79 + 151.27:.2f}")

conn.close()
