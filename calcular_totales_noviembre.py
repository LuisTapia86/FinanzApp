# -*- coding: utf-8 -*-
import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=== CÁLCULO PARA QUINCENA 26-NOV A 10-DIC ===\n")

# Gastos TDC AMEX (tarjeta_id = 4)
c.execute('SELECT SUM(monto) FROM gastos_tdc WHERE tarjeta_id=4 AND activo=1')
total_amex = c.fetchone()[0] or 0
print(f"Gastos TDC AMEX (ID 4): ${total_amex:.2f}")

# MSI activos
c.execute('SELECT SUM(mensualidad) FROM compras_msi WHERE activo=1 AND meses_restantes > 0')
total_msi = c.fetchone()[0] or 0
print(f"Total MSI mensuales: ${total_msi:.2f}")

# Gastos TDC Banamex Oro (tarjeta_id = 5)
c.execute('SELECT SUM(monto) FROM gastos_tdc WHERE tarjeta_id=5 AND activo=1')
total_banamex = c.fetchone()[0] or 0
print(f"Gastos TDC Banamex Oro (ID 5): ${total_banamex:.2f}")

# Gastos TDC NU (tarjeta_id = 3)
c.execute('SELECT SUM(monto) FROM gastos_tdc WHERE tarjeta_id=3 AND activo=1')
total_nu = c.fetchone()[0] or 0
print(f"Gastos TDC NU (ID 3): ${total_nu:.2f}")

print(f"\n=== TOTALES ===")
print(f"AMEX (pago día 31): ${total_amex:.2f}")
print(f"MSI (deberían estar en AMEX): ${total_msi:.2f}")
print(f"AMEX TOTAL (si MSI están incluidos): ${total_amex + total_msi:.2f}")
print(f"\nBanamex Oro (pago día 10): ${total_banamex:.2f}")
print(f"NU (pago día 16): ${total_nu:.2f}")
print(f"\nTOTAL A PAGAR 26-NOV a 10-DIC: ${total_amex + total_msi + total_banamex:.2f}")

print(f"\n=== COMPARACIÓN ===")
print(f"Esperado por Luis: $27,058.07")
print(f"Calculado: ${total_amex + total_msi + total_banamex:.2f}")
print(f"Diferencia: ${27058.07 - (total_amex + total_msi + total_banamex):.2f}")

conn.close()
