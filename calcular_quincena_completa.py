# -*- coding: utf-8 -*-
import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=" * 70)
print("PAGOS EN QUINCENA 1: 26-NOV A 10-DIC")
print("=" * 70)

# Tarjetas
print("\n=== TARJETAS ===")
c.execute('''SELECT
                tc.nombre,
                tc.fecha_pago_estimada,
                COALESCE(SUM(gt.monto), 0) as gastos,
                COALESCE((SELECT SUM(cm.mensualidad)
                          FROM compras_msi cm
                          WHERE cm.tarjeta_id = tc.id AND cm.activo = 1 AND cm.meses_restantes > 0), 0) as msi
             FROM tarjetas_credito tc
             LEFT JOIN gastos_tdc gt ON tc.id = gt.tarjeta_id AND gt.activo = 1
             WHERE tc.activo = 1
             GROUP BY tc.id
             ORDER BY tc.fecha_pago_estimada''')
tarjetas = c.fetchall()

total_tarjetas_quincena = 0
for t in tarjetas:
    total = t['gastos'] + t['msi']
    dia = t['fecha_pago_estimada']
    # Quincena 1: del 26 al 10 (del siguiente mes)
    # En noviembre: días 26-30
    # En diciembre: días 1-10
    if dia >= 26 or dia <= 10:
        incluida = "SI"
        total_tarjetas_quincena += total
    else:
        incluida = ""

    print(f"Dia {dia:>2} | {t['nombre']:20s} | ${total:>10.2f} {incluida}")

# Préstamos
print("\n=== PRÉSTAMOS ===")
c.execute('SELECT nombre, monto_mensual, dia_pago, fecha_inicio, fecha_fin FROM prestamos WHERE activo=1 ORDER BY dia_pago')
prestamos = c.fetchall()

total_prestamos_quincena = 0
for p in prestamos:
    dia = p['dia_pago']
    monto = p['monto_mensual']
    # Verificar si cae en la quincena (26-30 nov o 1-10 dic)
    if dia >= 26 or dia <= 10:
        incluido = "SI"
        total_prestamos_quincena += monto
    else:
        incluido = ""

    print(f"Dia {dia:>2} | {p['nombre']:20s} | ${monto:>10.2f} {incluido}")

print("\n" + "=" * 70)
print(f"TOTAL TARJETAS:  ${total_tarjetas_quincena:>10.2f}")
print(f"TOTAL PRÉSTAMOS: ${total_prestamos_quincena:>10.2f}")
print("-" * 70)
print(f"TOTAL QUINCENA:  ${total_tarjetas_quincena + total_prestamos_quincena:>10.2f}")
print("=" * 70)

print(f"\nEsperado por Luis: $27,058.07")
print(f"Diferencia: ${27058.07 - (total_tarjetas_quincena + total_prestamos_quincena):.2f}")

conn.close()
