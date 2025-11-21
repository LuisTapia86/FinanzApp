# -*- coding: utf-8 -*-
# migrate_dias_alerta_10.py - Actualizar dias_alerta a 10 días por defecto
import sqlite3
from config import Config

def migrate():
    """Actualizar dias_alerta de todos los créditos y MSI a 10 días"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    c = conn.cursor()

    try:
        # Actualizar créditos que tienen 3 días o NULL a 10 días
        c.execute('''UPDATE creditos_programados
                     SET dias_alerta = 10
                     WHERE dias_alerta IS NULL OR dias_alerta = 3''')
        creditos_actualizados = c.rowcount

        # Actualizar MSI que tienen 3 días o NULL a 10 días
        c.execute('''UPDATE compras_msi
                     SET dias_alerta = 10
                     WHERE dias_alerta IS NULL OR dias_alerta = 3''')
        msi_actualizados = c.rowcount

        conn.commit()
        print(f"[OK] Migración completada:")
        print(f"  - {creditos_actualizados} créditos actualizados a 10 días de alerta")
        print(f"  - {msi_actualizados} MSI actualizados a 10 días de alerta")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error en migración: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
