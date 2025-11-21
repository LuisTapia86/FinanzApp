# -*- coding: utf-8 -*-
import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=" * 70)
print("REVISIÓN COMPLETA DE TARJETAS Y GASTOS")
print("=" * 70)

# Obtener todas las tarjetas
c.execute('SELECT * FROM tarjetas_credito WHERE activo=1 ORDER BY id')
tarjetas = c.fetchall()

for tarjeta in tarjetas:
    print(f"\n{'='*70}")
    print(f"TARJETA: {tarjeta['nombre']} (ID: {tarjeta['id']})")
    print(f"Fecha Corte: {tarjeta['fecha_corte']} | Fecha Pago: {tarjeta['fecha_pago_estimada']}")
    print(f"{'='*70}")

    # Gastos corrientes
    print(f"\n  GASTOS CORRIENTES:")
    c.execute('SELECT fecha, concepto, monto FROM gastos_tdc WHERE tarjeta_id=? AND activo=1 ORDER BY fecha', (tarjeta['id'],))
    gastos = c.fetchall()
    total_gastos = 0
    if gastos:
        for g in gastos:
            print(f"    {g['fecha']} | {g['concepto']:30s} | ${g['monto']:>10.2f}")
            total_gastos += g['monto']
        print(f"    {'-'*60}")
        print(f"    {'SUBTOTAL GASTOS':30s} | ${total_gastos:>10.2f}")
    else:
        print(f"    (Sin gastos corrientes)")

    # MSI
    print(f"\n  COMPRAS MSI:")
    c.execute('SELECT producto, mensualidad, meses_restantes FROM compras_msi WHERE tarjeta_id=? AND activo=1 ORDER BY producto', (tarjeta['id'],))
    msis = c.fetchall()
    total_msi = 0
    if msis:
        for m in msis:
            print(f"    {m['producto']:30s} | ${m['mensualidad']:>10.2f}/mes | {m['meses_restantes']} meses restantes")
            total_msi += m['mensualidad']
        print(f"    {'-'*60}")
        print(f"    {'SUBTOTAL MSI MENSUAL':30s} | ${total_msi:>10.2f}")
    else:
        print(f"    (Sin MSI)")

    # Total de la tarjeta
    total_tarjeta = total_gastos + total_msi
    print(f"\n  {'*'*60}")
    print(f"  {'TOTAL A PAGAR':30s} | ${total_tarjeta:>10.2f}")
    print(f"  {'*'*60}")

# Resumen general
print(f"\n\n{'='*70}")
print(f"RESUMEN GENERAL POR FECHA DE PAGO")
print(f"{'='*70}")

c.execute('''SELECT tc.nombre, tc.fecha_pago_estimada, tc.id,
             COALESCE(SUM(gt.monto), 0) as gastos,
             COALESCE((SELECT SUM(cm.mensualidad) FROM compras_msi cm WHERE cm.tarjeta_id=tc.id AND cm.activo=1), 0) as msi
             FROM tarjetas_credito tc
             LEFT JOIN gastos_tdc gt ON tc.id=gt.tarjeta_id AND gt.activo=1
             WHERE tc.activo=1
             GROUP BY tc.id
             ORDER BY tc.fecha_pago_estimada''')

resumen = c.fetchall()
gran_total = 0
for r in resumen:
    total = r['gastos'] + r['msi']
    gran_total += total
    print(f"Día {r['fecha_pago_estimada']:>2} | {r['nombre']:20s} | Gastos: ${r['gastos']:>10.2f} + MSI: ${r['msi']:>10.2f} = ${total:>10.2f}")

print(f"{'='*70}")
print(f"{'GRAN TOTAL':40s} ${gran_total:>10.2f}")
print(f"{'='*70}")

conn.close()
