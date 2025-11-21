# -*- coding: utf-8 -*-
"""
Migración: Agregar campos de vista quincenal a la tabla configuracion
- vista_quincenal: BOOLEAN (0 o 1) para activar/desactivar vista quincenal
- fecha_pago_1: INTEGER (1-31) primera fecha de pago del mes
- fecha_pago_2: INTEGER (1-31) segunda fecha de pago del mes
"""
import sqlite3
from config import Config

def migrate():
    """Agregar campos de vista quincenal a configuracion"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    c = conn.cursor()

    try:
        # Agregar columna vista_quincenal
        c.execute('''ALTER TABLE configuracion
                     ADD COLUMN vista_quincenal INTEGER DEFAULT 0''')
        print("[OK] Columna 'vista_quincenal' agregada")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("[INFO] Columna 'vista_quincenal' ya existe")
        else:
            raise

    try:
        # Agregar columna fecha_pago_1
        c.execute('''ALTER TABLE configuracion
                     ADD COLUMN fecha_pago_1 INTEGER DEFAULT 15''')
        print("[OK] Columna 'fecha_pago_1' agregada (default: 15)")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("[INFO] Columna 'fecha_pago_1' ya existe")
        else:
            raise

    try:
        # Agregar columna fecha_pago_2
        c.execute('''ALTER TABLE configuracion
                     ADD COLUMN fecha_pago_2 INTEGER DEFAULT 30''')
        print("[OK] Columna 'fecha_pago_2' agregada (default: 30)")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("[INFO] Columna 'fecha_pago_2' ya existe")
        else:
            raise

    conn.commit()
    conn.close()
    print("\n[SUCCESS] Migración completada - Sistema de vista quincenal configurado")
    print("Defaults: vista_quincenal=0 (desactivada), fecha_pago_1=15, fecha_pago_2=30")

if __name__ == '__main__':
    migrate()
