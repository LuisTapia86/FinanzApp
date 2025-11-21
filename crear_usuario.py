# crear_usuario.py - Script para crear usuarios de prueba
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def crear_usuario(username, password, nombre_completo, email=None):
    """Crear un nuevo usuario en la base de datos"""
    conn = sqlite3.connect('finanzas.db')
    c = conn.cursor()

    try:
        # Generar hash de la contraseña
        password_hash = generate_password_hash(password)
        fecha_ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insertar usuario
        c.execute('''INSERT INTO usuarios
                     (username, password_hash, nombre_completo, email, fecha_creacion, activo)
                     VALUES (?, ?, ?, ?, ?, 1)''',
                  (username, password_hash, nombre_completo, email, fecha_ahora))

        usuario_id = c.lastrowid
        conn.commit()

        print(f"\nUsuario creado exitosamente!")
        print(f"  ID: {usuario_id}")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print(f"  Nombre: {nombre_completo}")
        if email:
            print(f"  Email: {email}")

        return usuario_id

    except sqlite3.IntegrityError:
        print(f"\nERROR: El usuario '{username}' ya existe!")
        return None
    except Exception as e:
        conn.rollback()
        print(f"\nERROR al crear usuario: {str(e)}")
        return None
    finally:
        conn.close()

def listar_usuarios():
    """Listar todos los usuarios"""
    conn = sqlite3.connect('finanzas.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('SELECT id, username, nombre_completo, email, fecha_creacion, activo FROM usuarios ORDER BY id')
    usuarios = c.fetchall()

    if usuarios:
        print("\n=== USUARIOS REGISTRADOS ===")
        for u in usuarios:
            estado = "ACTIVO" if u['activo'] else "INACTIVO"
            print(f"\nID: {u['id']} - {estado}")
            print(f"  Username: {u['username']}")
            print(f"  Nombre: {u['nombre_completo']}")
            if u['email']:
                print(f"  Email: {u['email']}")
            print(f"  Creado: {u['fecha_creacion']}")
    else:
        print("\nNo hay usuarios registrados")

    conn.close()

def menu_interactivo():
    """Menú interactivo para crear usuarios"""
    print("\n" + "="*50)
    print("  CREADOR DE USUARIOS - FinanzApp")
    print("="*50)
    print("\n1. Crear nuevo usuario")
    print("2. Listar usuarios existentes")
    print("3. Salir")

    opcion = input("\nSelecciona una opcion (1-3): ").strip()

    if opcion == '1':
        print("\n--- CREAR NUEVO USUARIO ---")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        nombre_completo = input("Nombre completo: ").strip()
        email = input("Email (opcional, presiona Enter para omitir): ").strip() or None

        if username and password and nombre_completo:
            crear_usuario(username, password, nombre_completo, email)
        else:
            print("\nERROR: Username, password y nombre completo son obligatorios")

    elif opcion == '2':
        listar_usuarios()

    elif opcion == '3':
        print("\nHasta luego!")
        return False

    else:
        print("\nOpcion invalida")

    return True

if __name__ == '__main__':
    # Si ejecutas el script directamente, abre el menú interactivo
    continuar = True
    while continuar:
        continuar = menu_interactivo()

    # También puedes importar este módulo y usar las funciones directamente:
    # from crear_usuario import crear_usuario
    # crear_usuario('juan', 'juan123', 'Juan Pérez', 'juan@email.com')
