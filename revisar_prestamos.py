# -*- coding: utf-8 -*-
import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=" * 70)
print("PRÉSTAMOS REGISTRADOS")
print("=" * 70)

c.execute('SELECT * FROM prestamos ORDER BY id')
prestamos = c.fetchall()

if prestamos:
    for p in prestamos:
        estado = "ACTIVO" if p['activo'] == 1 else "INACTIVO"
        print(f"\nID {p['id']}: {p['nombre']}")
        print(f"  Monto mensual: ${p['monto_mensual']:.2f}")
        print(f"  Día de pago: {p['dia_pago']}")
        print(f"  Fecha inicio: {p['fecha_inicio']}")
        print(f"  Fecha fin: {p['fecha_fin']}")
        print(f"  Estado: {estado}")
else:
    print("\nNo hay préstamos registrados")

# También revisar créditos programados
print("\n" + "=" * 70)
print("CRÉDITOS PROGRAMADOS")
print("=" * 70)

c.execute('SELECT * FROM creditos_programados WHERE activo=1 ORDER BY id')
creditos = c.fetchall()

if creditos:
    for c_row in creditos:
        print(f"\nID {c_row['id']}: {c_row['nombre']}")
        print(f"  Monto mensual: ${c_row['monto_mensual']:.2f}")
        print(f"  Día de pago: {c_row['dia_pago']}")
        print(f"  Fecha inicio: {c_row['fecha_inicio']}")
        print(f"  Fecha fin: {c_row['fecha_fin']}")
else:
    print("\nNo hay créditos programados activos")

conn.close()
