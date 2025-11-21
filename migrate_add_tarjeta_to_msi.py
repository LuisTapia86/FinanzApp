# -*- coding: utf-8 -*-
"""
Migración: Agregar campo tarjeta_id a la tabla compras_msi
- tarjeta_id: INTEGER - Referencia a creditos_programados (la tarjeta donde se cargan los MSI)
"""
import sqlite3
from config import Config

def migrate():
    """Agregar campo tarjeta_id a compras_msi para vincular MSI con tarjetas"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    c = conn.cursor()

    try:
        # Agregar columna tarjeta_id (puede ser NULL para MSI antiguos)
        c.execute('''ALTER TABLE compras_msi
                     ADD COLUMN tarjeta_id INTEGER''')
        print("[OK] Columna 'tarjeta_id' agregada a compras_msi")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("[INFO] Columna 'tarjeta_id' ya existe")
        else:
            raise

    conn.commit()
    conn.close()
    print("\n[SUCCESS] Migración completada")
    print("Ahora los MSI pueden vincularse a tarjetas de crédito específicas")
    print("Los MSI se pagarán en la fecha de pago de la tarjeta vinculada")

if __name__ == '__main__':
    migrate()
