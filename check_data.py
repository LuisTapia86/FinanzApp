import sqlite3

conn = sqlite3.connect('finanzas.db')
c = conn.cursor()

print("=== ULTIMOS 3 GASTOS ===")
c.execute('SELECT * FROM gastos ORDER BY id DESC LIMIT 3')
for row in c.fetchall():
    print(f'ID: {row[0]}, Fecha: {row[1]}, Tipo: {row[2]}, Nombre: {row[3]}, Monto: {row[4]}, Cat_ID: {row[5]}')

print("\n=== ULTIMOS 3 INGRESOS ===")
c.execute('SELECT * FROM ingresos ORDER BY id DESC LIMIT 3')
for row in c.fetchall():
    print(f'ID: {row[0]}, Fecha: {row[1]}, Concepto: {row[2]}, Monto: {row[3]}, Cat_ID: {row[4]}')

print("\n=== CATEGORIAS DISPONIBLES ===")
c.execute('SELECT * FROM categorias')
for row in c.fetchall():
    print(f'ID: {row[0]}, Nombre: {row[1]}, Tipo: {row[2]}, Color: {row[3]}')

conn.close()
