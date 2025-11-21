# -*- coding: utf-8 -*-
import sqlite3
from config import Config

conn = sqlite3.connect(Config.DATABASE_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=== CÁLCULO POR TARJETA ===\n")

# AMEX (ID 4) - Pago día 31
c.execute('SELECT SUM(monto) FROM gastos_tdc WHERE tarjeta_id=4 AND activo=1')
gastos_amex = c.fetchone()[0] or 0

c.execute('SELECT SUM(mensualidad) FROM compras_msi WHERE tarjeta_id=4 AND activo=1')
msi_amex = c.fetchone()[0] or 0

total_amex = gastos_amex + msi_amex
print(f"AMEX (pago día 31):")
print(f"  Gastos corrientes: ${gastos_amex:.2f}")
print(f"  MSI mensuales: ${msi_amex:.2f}")
print(f"  TOTAL: ${total_amex:.2f}\n")

# Banamex Oro (ID 5) - Pago día 10
c.execute('SELECT SUM(monto) FROM gastos_tdc WHERE tarjeta_id=5 AND activo=1')
gastos_banamex = c.fetchone()[0] or 0

c.execute('SELECT SUM(mensualidad) FROM compras_msi WHERE tarjeta_id=5 AND activo=1')
msi_banamex = c.fetchone()[0] or 0

total_banamex = gastos_banamex + msi_banamex
print(f"Banamex Oro (pago día 10):")
print(f"  Gastos corrientes: ${gastos_banamex:.2f}")
print(f"  MSI mensuales: ${msi_banamex:.2f}")
print(f"  TOTAL: ${total_banamex:.2f}\n")

# NU (ID 3) - Pago día 16
c.execute('SELECT SUM(monto) FROM gastos_tdc WHERE tarjeta_id=3 AND activo=1')
gastos_nu = c.fetchone()[0] or 0

c.execute('SELECT SUM(mensualidad) FROM compras_msi WHERE tarjeta_id=3 AND activo=1')
msi_nu = c.fetchone()[0] or 0

total_nu = gastos_nu + msi_nu
print(f"NU (pago día 16):")
print(f"  Gastos corrientes: ${gastos_nu:.2f}")
print(f"  MSI mensuales: ${msi_nu:.2f}")
print(f"  TOTAL: ${total_nu:.2f}\n")

# Banamex Clásica (ID 6) - Pago día 7
c.execute('SELECT SUM(monto) FROM gastos_tdc WHERE tarjeta_id=6 AND activo=1')
gastos_clasica = c.fetchone()[0] or 0

c.execute('SELECT SUM(mensualidad) FROM compras_msi WHERE tarjeta_id=6 AND activo=1')
msi_clasica = c.fetchone()[0] or 0

total_clasica = gastos_clasica + msi_clasica
if total_clasica > 0:
    print(f"Banamex Clásica (pago día 7):")
    print(f"  Gastos corrientes: ${gastos_clasica:.2f}")
    print(f"  MSI mensuales: ${msi_clasica:.2f}")
    print(f"  TOTAL: ${total_clasica:.2f}\n")

# Resumen para quincena 26-Nov a 10-Dic
print("=" * 50)
print("PAGOS EN QUINCENA 26-NOV A 10-DIC:")
print("=" * 50)
print(f"Banamex Clásica (día 7): ${total_clasica:.2f}" if total_clasica > 0 else "")
print(f"Banamex Oro (día 10): ${total_banamex:.2f}")
print(f"-" * 50)
total_quincena = total_banamex + total_clasica
print(f"TOTAL ESTA QUINCENA: ${total_quincena:.2f}")
print(f"\nPENDIENTE PRÓXIMA QUINCENA (11-25 Dic):")
print(f"NU (día 16): ${total_nu:.2f}")
print(f"\nPENDIENTE SIGUIENTE QUINCENA (26-Dic a 10-Ene):")
print(f"AMEX (día 31): ${total_amex:.2f}")

print(f"\n" + "=" * 50)
print(f"TOTAL GENERAL: ${total_amex + total_banamex + total_nu + total_clasica:.2f}")
print(f"Esperado por Luis: $27,058.07")
print(f"Diferencia: ${27058.07 - (total_amex + total_banamex + total_nu + total_clasica):.2f}")

conn.close()
