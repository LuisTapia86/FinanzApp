# migrate_add_users.py - Migración para agregar sistema de usuarios
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def migrate():
    """Agregar tabla de usuarios y columna usuario_id a todas las tablas"""
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()

    print("Iniciando migracion del sistema de usuarios...")

    try:
        # 1. Crear tabla de usuarios
        print("\n1. Creando tabla 'usuarios'...")
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        nombre_completo TEXT NOT NULL,
                        email TEXT,
                        fecha_creacion TEXT NOT NULL,
                        activo INTEGER DEFAULT 1
                    )''')

        # Crear usuario por defecto
        fecha_ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        password_hash = generate_password_hash('admin123')

        c.execute('''INSERT OR IGNORE INTO usuarios
                     (id, username, password_hash, nombre_completo, email, fecha_creacion, activo)
                     VALUES (1, 'admin', ?, 'Administrador', 'admin@finanzapp.com', ?, 1)''',
                  (password_hash, fecha_ahora))

        print("   OK Usuario por defecto creado: username='admin', password='admin123'")

        # 2. Agregar columna usuario_id a todas las tablas existentes
        tablas = [
            'ingresos',
            'gastos',
            'creditos_programados',
            'compras_msi',
            'ingresos_recurrentes',
            'configuracion',
            'prestamos',
            'tarjetas_credito',
            'gastos_tdc',
            'categorias',
            'simulaciones_historial'
        ]

        print("\n2. Agregando columna 'usuario_id' a todas las tablas...")
        for tabla in tablas:
            try:
                # Verificar si la tabla existe
                c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabla}'")
                if c.fetchone():
                    # Verificar si la columna ya existe
                    c.execute(f"PRAGMA table_info({tabla})")
                    columnas = [col[1] for col in c.fetchall()]

                    if 'usuario_id' not in columnas:
                        c.execute(f'ALTER TABLE {tabla} ADD COLUMN usuario_id INTEGER DEFAULT 1')
                        print(f"   OK Columna agregada a '{tabla}'")
                    else:
                        print(f"   SKIP '{tabla}' ya tiene columna usuario_id")
                else:
                    print(f"   WARN Tabla '{tabla}' no existe, saltando...")
            except Exception as e:
                print(f"   ERROR en tabla '{tabla}': {str(e)}")

        # 3. Actualizar registros existentes con usuario_id = 1
        print("\n3. Asignando usuario_id = 1 a registros existentes...")
        for tabla in tablas:
            try:
                c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabla}'")
                if c.fetchone():
                    c.execute(f'UPDATE {tabla} SET usuario_id = 1 WHERE usuario_id IS NULL OR usuario_id = 0')
                    registros_actualizados = c.rowcount
                    if registros_actualizados > 0:
                        print(f"   OK {registros_actualizados} registros actualizados en '{tabla}'")
            except Exception as e:
                print(f"   ERROR actualizando '{tabla}': {str(e)}")

        conn.commit()
        print("\nMigracion completada exitosamente!")
        print("\nCredenciales de acceso:")
        print("   Usuario: admin")
        print("   Contrasena: admin123")
        print("\nRecuerda: SKIP_LOGIN esta activado en config.py, el login esta deshabilitado para desarrollo")

    except Exception as e:
        conn.rollback()
        print(f"\nERROR durante la migracion: {str(e)}")
        raise

    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
