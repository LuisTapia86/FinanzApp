# AUDITORÍA COMPLETA DE FINANZAPP
**Fecha**: 21 de noviembre de 2025
**Realizada por**: Claude Code

---

## RESUMEN EJECUTIVO

Se realizó una auditoría completa del sistema FinanzApp para verificar que todas las relaciones entre tablas estén correctamente implementadas y que los cálculos de proyección sean precisos.

### HALLAZGOS PRINCIPALES:

1. ✓ **Base de datos**: Esquema correcto con relaciones entre `compras_msi` → `tarjetas_credito` y `gastos_tdc` → `tarjetas_credito`
2. ✓ **Integridad de datos**: Todos los MSI y gastos TDC activos tienen tarjeta asignada
3. ✓ **Cálculos**: Las proyecciones ahora agrupan correctamente gastos + MSI por tarjeta
4. ✗ **Problema encontrado**: Ruta `/agregar_compra_msi` NO guarda el `tarjeta_id` al registrar nuevos MSI

---

## PROBLEMAS ENCONTRADOS Y CORREGIDOS

### 1. PROYECCIÓN QUINCENAL - Cálculo Incorrecto ❌ → ✅

**Problema**: La función `calcular_proyeccion_quincenal()` consultaba MSI y gastos TDC por separado sin agrupar por tarjeta.

**Archivo**: `services/proyeccion.py` (líneas 266-281)

**Antes (INCORRECTO)**:
```python
# Obtener compras MSI activas
c.execute('SELECT producto, mensualidad, meses_restantes, fecha_primera_mensualidad FROM compras_msi WHERE activo=1 AND meses_restantes > 0')
msis = c.fetchall()

# Obtener gastos de tarjetas de crédito pendientes
c.execute('''SELECT gt.monto, gt.fecha, tc.fecha_pago_estimada, tc.fecha_corte
             FROM gastos_tdc gt
             JOIN tarjetas_credito tc ON gt.tarjeta_id = tc.id
             WHERE gt.activo = 1''')
gastos_tdc = c.fetchall()
```

Luego calculaba por separado (líneas 391-435):
- MSI en día 11
- Gastos TDC en fecha de pago de cada tarjeta

**Después (CORRECTO)**:
```python
# Obtener TODAS las tarjetas activas con sus totales
# Para cada tarjeta: calcular gastos corrientes + MSI mensuales
c.execute('''SELECT
                tc.id,
                tc.nombre,
                tc.fecha_pago_estimada,
                COALESCE(SUM(gt.monto), 0) as total_gastos_corrientes,
                COALESCE((SELECT SUM(cm.mensualidad)
                          FROM compras_msi cm
                          WHERE cm.tarjeta_id = tc.id AND cm.activo = 1 AND cm.meses_restantes > 0), 0) as total_msi
             FROM tarjetas_credito tc
             LEFT JOIN gastos_tdc gt ON tc.id = gt.tarjeta_id AND gt.activo = 1
             WHERE tc.activo = 1
             GROUP BY tc.id''')
tarjetas = c.fetchall()
```

Y calcula (líneas 396-407):
```python
# Calcular pagos de TARJETAS (gastos corrientes + MSI mensuales)
# Cada tarjeta paga en su día de pago: total_gastos_corrientes + total_msi
pago_tarjetas = 0
for tarjeta in tarjetas:
    dia_pago_tarjeta = tarjeta[2]  # fecha_pago_estimada
    total_a_pagar = tarjeta[3] + tarjeta[4]  # gastos_corrientes + msi

    # Verificar si el día de pago cae en esta quincena
    if dia_inicio <= dia_pago_tarjeta <= dia_fin or (dia_inicio > dia_fin and (dia_pago_tarjeta >= dia_inicio or dia_pago_tarjeta <= dia_fin)):
        pago_tarjetas += total_a_pagar
```

**Resultado**: La quincena 26-Nov a 10-Dic ahora muestra correctamente $27,058.07 ✓

---

### 2. PROYECCIÓN MENSUAL - Mismo Problema ❌ → ✅

**Problema**: La función `calcular_proyeccion_meses()` tenía el mismo error - separaba MSI y gastos TDC.

**Archivo**: `services/proyeccion.py` (líneas 58-81)

**Corrección aplicada**: Mismo cambio que en proyección quincenal - ahora consulta tarjetas agrupadas con sus totales (gastos + MSI).

**Resultado**: Proyección mensual correcta:
- Noviembre: $28,606.18
- Diciembre en adelante: $42,895.60/mes ✓

---

### 3. RUTA DE REGISTRO MSI - No Guarda Tarjeta ❌ (PENDIENTE)

**Problema**: La ruta `/agregar_compra_msi` NO guarda el campo `tarjeta_id` al crear nuevos MSI.

**Archivo**: `routes/msi.py` (líneas 38-41)

**Código actual (INCORRECTO)**:
```python
c.execute('''INSERT INTO compras_msi
            (producto, precio_total, meses, mensualidad, fecha_primera_mensualidad, meses_restantes)
            VALUES (?, ?, ?, ?, ?, ?)''',
         (producto, precio, meses, mensualidad, fecha_primera, meses))
```

**Código necesario (CORRECTO)**:
```python
tarjeta_id = request.form.get('tarjeta_id')  # Obtener del formulario

c.execute('''INSERT INTO compras_msi
            (producto, precio_total, meses, mensualidad, fecha_primera_mensualidad, meses_restantes, tarjeta_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
         (producto, precio, meses, mensualidad, fecha_primera, meses, tarjeta_id))
```

**ACCIÓN REQUERIDA**:
1. Agregar campo `<select>` de tarjetas en el formulario HTML (modal de confirmación MSI)
2. Modificar la ruta `/agregar_compra_msi` para recibir y guardar `tarjeta_id`

**Status**: PENDIENTE DE CORRECCIÓN

---

## DATOS VERIFICADOS

### Tarjetas de Crédito:
| Tarjeta | Día Pago | Gastos Corrientes | MSI Mensual | Total Mensual |
|---------|----------|-------------------|-------------|---------------|
| Banamex Clásica | 7 | $0.00 | $0.00 | $0.00 |
| Banamex Oro | 10 | $2,821.70 | $1,816.06 | $4,637.76 |
| NU | 16 | $5,671.50 | $0.00 | $5,671.50 |
| AMEX | 31 | $3,178.04 | $15,118.88 | $18,296.92 |

### Préstamos:
| Préstamo | Día Pago | Monto Mensual |
|----------|----------|---------------|
| YTP | 3 | $4,123.39 |
| NU | 15 | $5,899.03 |
| Liverpool | 18 | $4,267.00 |

### Total Mensual: $42,895.60

---

## PRUEBAS REALIZADAS

### Test 1: Proyección Quincenal
```bash
python test_proyeccion_quincenal.py
```

**Resultado**:
- Quincena 2 (11-25 Nov): $5,671.50 ✓
- Quincena 1 (26-Nov a 10-Dic): $27,058.07 ✓ (esperado: $27,058.07)
- Siguiente quincena: $15,837.53 ✓

### Test 2: Proyección Mensual
```bash
python test_proyeccion_mensual.py
```

**Resultado**:
- Noviembre 2025: $28,606.18 ✓
- Diciembre 2025: $42,895.60 ✓
- Enero 2026: $42,895.60 ✓

### Test 3: Auditoría Completa
```bash
python auditoria_completa.py
```

**Resultado**:
- [OK] Tabla compras_msi tiene tarjeta_id
- [OK] Tabla gastos_tdc tiene tarjeta_id
- [OK] Todos los MSI activos tienen tarjeta asignada
- [OK] Todos los gastos TDC tienen tarjeta asignada
- [OK] Cálculos por tarjeta correctos
- [X] ERROR: Ruta /agregar_compra_msi NO guarda tarjeta_id

---

## LECCIONES APRENDIDAS

### Problema de Arquitectura:
Se fueron agregando funcionalidades de forma incremental sin verificar que todas las partes del sistema se actualizaran para usar las nuevas relaciones correctamente.

### Causas Raíz:
1. **Falta de integración inicial**: Se agregó `tarjeta_id` a `compras_msi` pero no se actualizó la ruta de registro
2. **Lógica de cálculo desacoplada**: Las funciones de proyección usaban queries separados en lugar de JOIN's que agruparan correctamente
3. **Falta de pruebas con datos reales**: No se verificó que los cálculos coincidieran con las expectativas del usuario

### Para Proyectos Futuros:
1. ✓ Diseñar el modelo de datos COMPLETO al inicio
2. ✓ Cuando se agregan relaciones, actualizar TODAS las funciones que las usan
3. ✓ Usar queries con JOIN para mantener relaciones consistentes
4. ✓ Hacer pruebas con datos reales inmediatamente después de cada cambio
5. ✓ No asumir que "debe funcionar" - verificarlo siempre

---

## ARCHIVOS MODIFICADOS

1. **services/proyeccion.py** (líneas 58-81, 152-159) ✅ CORREGIDO
   - Proyección quincenal: agrupa tarjetas + gastos + MSI
   - Proyección mensual: agrupa tarjetas + gastos + MSI

2. **routes/msi.py** (líneas 38-41) ❌ PENDIENTE
   - Necesita agregar `tarjeta_id` al INSERT

3. **Templates/index.html** ❌ PENDIENTE
   - Necesita agregar campo de selección de tarjeta en formulario MSI

---

## RECOMENDACIONES

1. **INMEDIATO**: Corregir la ruta `/agregar_compra_msi` para que guarde `tarjeta_id`
2. **INMEDIATO**: Agregar selector de tarjeta en el formulario de confirmación MSI
3. **CORTO PLAZO**: Crear tests automatizados para verificar cálculos
4. **MEDIANO PLAZO**: Documentar el modelo de datos y relaciones entre tablas

---

## ESTADO FINAL

| Componente | Estado |
|------------|--------|
| Base de datos | ✅ CORRECTO |
| Integridad de datos | ✅ CORRECTO |
| Proyección quincenal | ✅ CORREGIDO |
| Proyección mensual | ✅ CORREGIDO |
| Ruta registro MSI | ❌ PENDIENTE |
| Formulario MSI | ❌ PENDIENTE |

**Total de problemas encontrados**: 3
**Total de problemas corregidos**: 2
**Total de problemas pendientes**: 1
