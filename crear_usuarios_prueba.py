# crear_usuarios_prueba.py - Script para crear múltiples usuarios de prueba rápidamente
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def crear_usuario(username, password, nombre_completo, email=None):
    """Crear un nuevo usuario en la base de datos"""
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()

    try:
        password_hash = generate_password_hash(password)
        fecha_ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        c.execute('''INSERT INTO usuarios
                     (username, password_hash, nombre_completo, email, fecha_creacion, activo)
                     VALUES (?, ?, ?, ?, ?, 1)''',
                  (username, password_hash, nombre_completo, email, fecha_ahora))

        usuario_id = c.lastrowid
        conn.commit()
        conn.close()
        return usuario_id

    except sqlite3.IntegrityError:
        conn.close()
        return None
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e

def crear_usuarios_prueba():
    """Crear varios usuarios de prueba"""
    usuarios = [
        {
            'username': 'juan',
            'password': 'juan123',
            'nombre': 'Juan Pérez',
            'email': 'juan@test.com'
        },
        {
            'username': 'maria',
            'password': 'maria123',
            'nombre': 'María González',
            'email': 'maria@test.com'
        },
        {
            'username': 'pedro',
            'password': 'pedro123',
            'nombre': 'Pedro Martínez',
            'email': 'pedro@test.com'
        }
    ]

    print("\n" + "="*60)
    print("  CREADOR DE USUARIOS DE PRUEBA - FinanzApp")
    print("="*60)
    print("\nCreando usuarios de prueba...\n")

    creados = 0
    ya_existian = 0

    for u in usuarios:
        user_id = crear_usuario(u['username'], u['password'], u['nombre'], u['email'])
        if user_id:
            print(f"OK  Usuario '{u['username']}' creado (ID: {user_id})")
            print(f"    Password: {u['password']}")
            print(f"    Nombre: {u['nombre']}")
            print(f"    Email: {u['email']}\n")
            creados += 1
        else:
            print(f"SKIP  Usuario '{u['username']}' ya existe\n")
            ya_existian += 1

    print("="*60)
    print(f"\nResumen:")
    print(f"  Usuarios creados: {creados}")
    print(f"  Usuarios que ya existian: {ya_existian}")
    print(f"  Total: {creados + ya_existian}")

    print("\n" + "="*60)
    print("  CREDENCIALES DE ACCESO")
    print("="*60)
    print("\nUsuario por defecto (admin):")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nUsuarios de prueba:")
    for u in usuarios:
        print(f"  Username: {u['username']:10} | Password: {u['password']}")

    print("\n" + "="*60)
    print("IMPORTANTE:")
    print("  - SKIP_LOGIN esta activado (config.py)")
    print("  - Todos entran automaticamente como admin (ID=1)")
    print("  - Para probar multi-usuario, cambia SKIP_LOGIN = False")
    print("="*60 + "\n")

if __name__ == '__main__':
    crear_usuarios_prueba()
