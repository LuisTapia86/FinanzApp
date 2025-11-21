# -*- coding: utf-8 -*-
# migrate_tdc_system.py - Migración para sistema de Tarjetas de Crédito
import sqlite3
from config import Config

def migrate():
    """Crear nuevas tablas para sistema de TDC"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    c = conn.cursor()

    try:
        # 1. Crear tabla de tarjetas de crédito
        c.execute('''CREATE TABLE IF NOT EXISTS tarjetas_credito
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      nombre TEXT NOT NULL,
                      fecha_corte INTEGER NOT NULL,
                      fecha_pago_estimada INTEGER NOT NULL,
                      limite_credito REAL DEFAULT 0,
                      activo INTEGER DEFAULT 1)''')

        # 2. Crear tabla de gastos de TDC (corrientes y MSI)
        c.execute('''CREATE TABLE IF NOT EXISTS gastos_tdc
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      tarjeta_id INTEGER NOT NULL,
                      fecha TEXT NOT NULL,
                      concepto TEXT NOT NULL,
                      monto REAL NOT NULL,
                      tipo TEXT DEFAULT 'corriente',
                      meses_msi INTEGER DEFAULT 0,
                      mensualidad_msi REAL DEFAULT 0,
                      meses_restantes INTEGER DEFAULT 0,
                      categoria_id INTEGER,
                      activo INTEGER DEFAULT 1,
                      FOREIGN KEY (tarjeta_id) REFERENCES tarjetas_credito(id),
                      FOREIGN KEY (categoria_id) REFERENCES categorias(id))''')

        # 3. Renombrar tabla antigua de créditos a préstamos (para claridad)
        # Primero verificar si existe la tabla prestamos
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='prestamos'")
        if not c.fetchone():
            # Crear nueva tabla prestamos con estructura simplificada
            c.execute('''CREATE TABLE IF NOT EXISTS prestamos
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          nombre TEXT NOT NULL,
                          monto_mensual REAL NOT NULL,
                          dia_pago INTEGER NOT NULL,
                          fecha_inicio TEXT NOT NULL,
                          fecha_fin TEXT NOT NULL,
                          dias_alerta INTEGER DEFAULT 10,
                          activo INTEGER DEFAULT 1)''')

            # Copiar datos de creditos_programados a prestamos (solo campos relevantes)
            c.execute('''INSERT INTO prestamos (id, nombre, monto_mensual, dia_pago, fecha_inicio, fecha_fin, dias_alerta, activo)
                         SELECT id, nombre, monto_mensual, dia_pago, fecha_inicio, fecha_fin, dias_alerta, activo
                         FROM creditos_programados''')

            print(f"[OK] Migrados {c.rowcount} créditos a tabla 'prestamos'")

        conn.commit()
        print("[OK] Migración de TDC completada:")
        print("  - Tabla 'tarjetas_credito' creada")
        print("  - Tabla 'gastos_tdc' creada")
        print("  - Tabla 'prestamos' creada con datos migrados")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error en migración: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
