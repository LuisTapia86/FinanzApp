# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FinanzApp is a personal finance management Flask application that tracks income, expenses, recurring payments, and provides financial projections. The app uses SQLite for data persistence and includes a "traffic light" system to visualize financial health over upcoming months.

## Running the Application

```bash
# Start the Flask development server
python app.py

# Access the app at http://127.0.0.1:5000
```

The application will automatically initialize the SQLite database (`finanzas.db`) on first run.

## Architecture

### Single-File Flask Application
The entire backend logic is contained in `app.py` with the following key components:

1. **Database Schema** (SQLite):
   - `ingresos` - One-time income entries
   - `gastos` - One-time expense entries
   - `creditos_programados` - Recurring monthly credit/loan payments with configurable dates
   - `compras_msi` - Interest-free installment purchases (Meses Sin Intereses)
   - `ingresos_recurrentes` - Recurring income (salary, etc.)
   - `configuracion` - App settings (initial balance, first-time flag)

2. **Core Financial Logic**:
   - Balance calculation: `balance_inicial + total_ingresos - total_gastos`
   - Projection engine (`calcular_proyeccion_meses()`) simulates future months considering:
     - Recurring income with date ranges
     - Scheduled credit payments with date ranges
     - MSI installments based on start dates and remaining months
   - Alert system (`obtener_proximas_alertas()`) tracks upcoming payments within 15 days
   - Traffic light states: verde (>$10,000), amarillo ($0-$10,000), rojo (<$0)

3. **Purchase Simulator**:
   - `/simular_compra` endpoint accepts JSON with `precio` and `meses`
   - Returns projection comparing scenarios with/without the purchase
   - Verdict logic: "NO" if red in first 3 months, "CUIDADO" if red later, "SI" if always safe

### Frontend Structure
- Single HTML template: `Templates/index.html`
- Inline CSS with gradient background and card-based layout
- JavaScript handles purchase simulation via AJAX

## Date Handling Considerations

The `parse_fecha()` function handles multiple date formats (YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY). Date ranges use "2099-12-31" as default for indefinite end dates.

When working with projections:
- Date comparisons use year-month only (ignore day component) via `datetime(year, month, 1)`
- Handles invalid dates (e.g., day 31 in February) by falling back to last day of month
- MSI payments track months elapsed since `fecha_primera_mensualidad`

## Key Routes

**Data Entry:**
- POST `/agregar_ingreso` - Add one-time income
- POST `/agregar_gasto` - Add one-time expense
- POST `/agregar_credito` - Add recurring credit payment
- POST `/agregar_ingreso_recurrente` - Add recurring income
- POST `/agregar_compra_msi` - Confirm MSI purchase

**Simulation:**
- POST `/simular_compra` (JSON) - Simulate purchase impact

**Management:**
- GET `/desactivar_credito/<id>` - Soft delete (sets `activo=0`)
- GET `/borrar_credito/<id>` - Hard delete
- POST `/pago_anticipado_msi/<id>` - Reduce remaining MSI months

**Configuration:**
- POST `/configurar_balance_inicial` - Set initial balance (first time)
- POST `/editar_balance_inicial` - Update initial balance

## Database Location

The SQLite database `finanzas.db` is created in the working directory (same as `app.py`). This is not version controlled.

## No External Dependencies File

This project does not currently have a `requirements.txt`. The code imports:
- `flask` - Web framework
- `sqlite3` - Database (Python standard library)
- `datetime` - Date handling (Python standard library)
- `python-dateutil` - For `relativedelta` calculations

To set up a new environment, install:
```bash
pip install flask python-dateutil
```
