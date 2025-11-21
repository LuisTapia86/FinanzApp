# -*- coding: utf-8 -*-
# migrate_add_categories.py - Agregar columnas de categorias a tablas existentes
import sqlite3
from config import Config

def migrate():
    """Agregar columnas categoria_id a ingresos y gastos"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    c = conn.cursor()

    try:
        # Verificar si la columna ya existe en gastos
        c.execute("PRAGMA table_info(gastos)")
        gastos_columns = [row[1] for row in c.fetchall()]

        if 'categoria_id' not in gastos_columns:
            print("[MIGRACION] Agregando columna categoria_id a tabla gastos...")
            c.execute('ALTER TABLE gastos ADD COLUMN categoria_id INTEGER')
            print("[OK] Columna categoria_id agregada a gastos")
        else:
            print("[OK] La columna categoria_id ya existe en gastos")

        # Verificar si la columna ya existe en ingresos
        c.execute("PRAGMA table_info(ingresos)")
        ingresos_columns = [row[1] for row in c.fetchall()]

        if 'categoria_id' not in ingresos_columns:
            print("[MIGRACION] Agregando columna categoria_id a tabla ingresos...")
            c.execute('ALTER TABLE ingresos ADD COLUMN categoria_id INTEGER')
            print("[OK] Columna categoria_id agregada a ingresos")
        else:
            print("[OK] La columna categoria_id ya existe en ingresos")

        conn.commit()
        print("[OK] Migracion completada exitosamente")

    except Exception as e:
        print(f"[ERROR] Error durante la migracion: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("  MIGRACION: Agregar soporte de categorias")
    print("=" * 60)
    migrate()
    print("=" * 60)
