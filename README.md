# 💰 FinanzApp - Sistema de Gestión Financiera Personal

Aplicación web full-stack para gestión financiera personal con proyecciones quincenales automatizadas, sistema de alertas y dashboard analítico.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-orange.svg)

## 🚀 Características Principales

### 📊 Proyección Quincenal Inteligente
- Proyecciones automatizadas hasta 12 meses adelante
- Sistema de semáforo visual (🟢 Verde, 🟡 Amarillo, 🔴 Rojo)
- Cálculos precisos considerando fechas de pago personalizadas
- Análisis de tendencias y saldo mínimo proyectado

### 💳 Gestión de Tarjetas de Crédito
- Soporte para múltiples tarjetas
- Distinción entre gastos corrientes y MSI (Meses Sin Intereses)
- Tracking automático de pagos mensuales
- Alertas de vencimientos próximos

### 📈 Dashboard Analítico
- Gráficas interactivas con Chart.js
- Análisis de ingresos vs gastos históricos
- Distribución de gastos por categoría
- Proyección visual de saldo futuro

### 🎯 Simulador de Compras
- Proyección de impacto financiero antes de comprar
- Comparación con/sin compra
- Recomendaciones automáticas basadas en saldo proyectado

## 🛠️ Tecnologías Utilizadas

**Backend:**
- Python 3.9+
- Flask 3.0
- SQLite
- python-dateutil

**Frontend:**
- HTML5 / CSS3
- JavaScript (ES6+)
- Chart.js
- Diseño responsivo

## 📦 Instalación

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/finanzapp.git
cd finanzapp

# Instalar dependencias
pip install flask python-dateutil

# Crear datos de demo
python create_demo_data.py

# Ejecutar aplicación
python app.py
```

Abre http://localhost:5000 en tu navegador

## 📁 Estructura del Proyecto

```
FinanzApp/
├── app.py                  # Punto de entrada
├── config.py              # Configuración
├── database.py            # Gestión DB
├── routes/                # Blueprints Flask
│   └── dashboard.py
├── services/              # Lógica de negocio
│   └── proyeccion.py
├── Templates/             # Templates HTML
└── finanzas.db           # Base de datos
```

## 🎮 Uso Básico

1. **Primera configuración**: Establece balance inicial y fechas de pago
2. **Registra ingresos recurrentes**: Nómina, aguinaldo, etc.
3. **Agrega gastos**: TDC, préstamos, MSI
4. **Revisa proyecciones**: Dashboard visual con semáforo
5. **Simula compras**: Antes de comprometerte financieramente

## 🚀 Deploy Gratis

### Railway
1. Sube tu código a GitHub
2. Conecta en Railway.app
3. Deploy automático

### Render
1. New Web Service en Render.com
2. Conecta repositorio
3. Build: `pip install flask python-dateutil`
4. Start: `python app.py`

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Abre un Issue o Pull Request.

## 📄 Licencia

MIT License - ver LICENSE para detalles

---

**Hecho con ❤️ en México**
