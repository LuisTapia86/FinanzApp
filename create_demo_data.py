# -*- coding: utf-8 -*-
"""
Script para crear datos de demostración para FinanzApp
Ejecutar este script creará una base de datos con datos ficticios
"""
import sqlite3
from datetime import datetime, timedelta
import os

# Crear base de datos de demo
DB_PATH = 'finanzas_demo.db'

# Si existe, eliminarla
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print(f"[OK] Base de datos anterior eliminada")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# ========== CREAR TABLAS ==========
print("Creando tablas...")

# Configuración
c.execute('''CREATE TABLE IF NOT EXISTS configuracion (
    id INTEGER PRIMARY KEY,
    balance_inicial REAL DEFAULT 0,
    primera_vez INTEGER DEFAULT 1
)''')

# Ingresos
c.execute('''CREATE TABLE IF NOT EXISTS ingresos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    monto REAL NOT NULL,
    fecha DATE NOT NULL,
    categoria TEXT
)''')

# Gastos
c.execute('''CREATE TABLE IF NOT EXISTS gastos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    monto REAL NOT NULL,
    fecha DATE NOT NULL,
    tipo TEXT,
    categoria TEXT
)''')

# Tarjetas de crédito
c.execute('''CREATE TABLE IF NOT EXISTS tarjetas_credito (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    fecha_pago_estimada INTEGER NOT NULL,
    activo INTEGER DEFAULT 1
)''')

# Gastos de TDC
c.execute('''CREATE TABLE IF NOT EXISTS gastos_tdc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tarjeta_id INTEGER NOT NULL,
    concepto TEXT NOT NULL,
    monto REAL NOT NULL,
    fecha DATE NOT NULL,
    tipo TEXT NOT NULL,
    meses_msi INTEGER,
    mensualidad_msi REAL,
    meses_restantes INTEGER,
    activo INTEGER DEFAULT 1,
    FOREIGN KEY (tarjeta_id) REFERENCES tarjetas_credito(id)
)''')

# Préstamos
c.execute('''CREATE TABLE IF NOT EXISTS prestamos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    monto_mensual REAL NOT NULL,
    dia_pago INTEGER NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    activo INTEGER DEFAULT 1
)''')

# Ingresos recurrentes
c.execute('''CREATE TABLE IF NOT EXISTS ingresos_recurrentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    monto REAL NOT NULL,
    dia_pago INTEGER NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    activo INTEGER DEFAULT 1
)''')

# Categorías
c.execute('''CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    tipo TEXT NOT NULL
)''')

print("[OK] Tablas creadas")

# ========== INSERTAR DATOS DE DEMO ==========
print("\nInsertando datos de demostración...")

# Configuración inicial
c.execute("INSERT INTO configuracion (id, balance_inicial, primera_vez) VALUES (1, 45000.00, 0)")
print("[OK] Balance inicial: $45,000")

# Categorías
categorias = [
    ('Alimentación', 'gasto'),
    ('Transporte', 'gasto'),
    ('Entretenimiento', 'gasto'),
    ('Salud', 'gasto'),
    ('Servicios', 'gasto'),
    ('Salario', 'ingreso'),
    ('Freelance', 'ingreso'),
    ('Bonos', 'ingreso')
]
c.executemany("INSERT INTO categorias (nombre, tipo) VALUES (?, ?)", categorias)
print(f"[OK] {len(categorias)} categorías creadas")

# Ingresos recurrentes
ingresos_rec = [
    ('Nómina Quincenal', 12500.00, 10, '2025-01-10', '2099-12-31'),
    ('Nómina Quincenal', 12500.00, 25, '2025-01-25', '2099-12-31'),
    ('Aguinaldo', 25000.00, 17, '2025-12-17', '2099-12-31')
]
c.executemany("INSERT INTO ingresos_recurrentes (nombre, monto, dia_pago, fecha_inicio, fecha_fin, activo) VALUES (?, ?, ?, ?, ?, 1)", ingresos_rec)
print(f"[OK] {len(ingresos_rec)} ingresos recurrentes")

# Tarjetas de crédito
tarjetas = [
    ('Visa Platino', 16),
    ('Mastercard Gold', 31),
    ('American Express', 9),
    ('Tarjeta Departamental', 7)
]
c.executemany("INSERT INTO tarjetas_credito (nombre, fecha_pago_estimada, activo) VALUES (?, ?, 1)", tarjetas)
print(f"[OK] {len(tarjetas)} tarjetas creadas")

# Gastos corrientes de TDC
gastos_corrientes = [
    (1, 'Supermercado', 2500.50, '2025-11-15', 'corriente', None, None, None),
    (1, 'Gasolina', 1200.00, '2025-11-18', 'corriente', None, None, None),
    (2, 'Restaurantes', 3800.75, '2025-11-20', 'corriente', None, None, None),
    (3, 'Compras varias', 5200.00, '2025-11-10', 'corriente', None, None, None),
    (4, 'Ropa', 2100.00, '2025-11-05', 'corriente', None, None, None)
]
c.executemany("INSERT INTO gastos_tdc (tarjeta_id, concepto, monto, fecha, tipo, meses_msi, mensualidad_msi, meses_restantes, activo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)", gastos_corrientes)
print(f"[OK] {len(gastos_corrientes)} gastos corrientes")

# MSI
msi_data = [
    (2, 'Laptop Dell', 18000.00, '2025-09-15', 'msi', 12, 1500.00, 9),
    (2, 'iPhone 15', 24000.00, '2025-10-01', 'msi', 18, 1333.33, 17),
    (3, 'Smart TV 55"', 15000.00, '2025-08-20', 'msi', 12, 1250.00, 8),
    (1, 'Refrigerador', 21000.00, '2025-07-10', 'msi', 24, 875.00, 19),
    (4, 'Muebles sala', 12000.00, '2025-10-15', 'msi', 12, 1000.00, 11)
]
c.executemany("INSERT INTO gastos_tdc (tarjeta_id, concepto, monto, fecha, tipo, meses_msi, mensualidad_msi, meses_restantes, activo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)", msi_data)
print(f"[OK] {len(msi_data)} compras MSI")

# Préstamos
prestamos = [
    ('Préstamo Personal Banco', 4500.00, 3, '2025-01-03', '2026-12-03'),
    ('Crédito Auto', 6800.00, 15, '2024-06-15', '2028-06-15'),
    ('Préstamo Familiar', 2000.00, 28, '2025-03-28', '2026-03-28')
]
c.executemany("INSERT INTO prestamos (nombre, monto_mensual, dia_pago, fecha_inicio, fecha_fin, activo) VALUES (?, ?, ?, ?, ?, 1)", prestamos)
print(f"[OK] {len(prestamos)} préstamos")

# Algunos gastos históricos para las gráficas
gastos_hist = [
    ('Supermercado', 3200.00, '2025-10-15', 'recurrente', 'Alimentación'),
    ('Gasolina', 1500.00, '2025-10-20', 'recurrente', 'Transporte'),
    ('Netflix', 199.00, '2025-10-05', 'suscripción', 'Entretenimiento'),
    ('Spotify', 129.00, '2025-10-10', 'suscripción', 'Entretenimiento'),
    ('Luz', 850.00, '2025-10-25', 'servicio', 'Servicios'),
    ('Agua', 320.00, '2025-10-28', 'servicio', 'Servicios'),
    ('Internet', 599.00, '2025-10-01', 'servicio', 'Servicios')
]
c.executemany("INSERT INTO gastos (nombre, monto, fecha, tipo, categoria) VALUES (?, ?, ?, ?, ?)", gastos_hist)
print(f"[OK] {len(gastos_hist)} gastos históricos")

# Algunos ingresos históricos
ingresos_hist = [
    ('Nómina', 12500.00, '2025-10-10', 'Salario'),
    ('Nómina', 12500.00, '2025-10-25', 'Salario'),
    ('Proyecto Freelance', 8500.00, '2025-10-15', 'Freelance')
]
c.executemany("INSERT INTO ingresos (nombre, monto, fecha, categoria) VALUES (?, ?, ?, ?)", ingresos_hist)
print(f"[OK] {len(ingresos_hist)} ingresos históricos")

conn.commit()
conn.close()

print(f"\n{'='*60}")
print(f"[SUCCESS] Base de datos de DEMO creada exitosamente: {DB_PATH}")
print(f"{'='*60}")
print("\nPara usar esta base de datos de demo:")
print("1. Renombra tu base de datos actual: finanzas.db -> finanzas_personal.db")
print("2. Renombra esta: finanzas_demo.db -> finanzas.db")
print("3. Reinicia la app")
print("\nPara volver a tus datos reales:")
print("1. Renombra: finanzas.db -> finanzas_demo.db")
print("2. Renombra: finanzas_personal.db -> finanzas.db")
print("3. Reinicia la app")
