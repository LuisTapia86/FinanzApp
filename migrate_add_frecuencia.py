# -*- coding: utf-8 -*-
# migrate_add_frecuencia.py - Agregar campo de frecuencia a ingresos recurrentes
import sqlite3
from config import Config

def migrate():
    """Agregar columna frecuencia a ingresos_recurrentes"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    c = conn.cursor()

    try:
        # Verificar si la columna ya existe
        c.execute("PRAGMA table_info(ingresos_recurrentes)")
        columns = [row[1] for row in c.fetchall()]

        if 'frecuencia' not in columns:
            print("[MIGRACION] Agregando columna frecuencia a tabla ingresos_recurrentes...")
            c.execute('ALTER TABLE ingresos_recurrentes ADD COLUMN frecuencia TEXT DEFAULT "mensual"')
            print("[OK] Columna frecuencia agregada")
        else:
            print("[OK] La columna frecuencia ya existe")

        if 'mes_especifico' not in columns:
            print("[MIGRACION] Agregando columna mes_especifico a tabla ingresos_recurrentes...")
            c.execute('ALTER TABLE ingresos_recurrentes ADD COLUMN mes_especifico INTEGER DEFAULT NULL')
            print("[OK] Columna mes_especifico agregada")
        else:
            print("[OK] La columna mes_especifico ya existe")

        conn.commit()
        print("[OK] Migracion completada exitosamente")

    except Exception as e:
        print(f"[ERROR] Error durante la migracion: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("  MIGRACION: Agregar frecuencias a ingresos recurrentes")
    print("=" * 60)
    migrate()
    print("=" * 60)
