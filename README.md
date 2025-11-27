# 💰 FinanzApp - Personal Finance Management System

A full-stack financial management web application built with Python/Flask featuring automated cash flow projections, intelligent alert systems, and comprehensive financial analytics.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-orange.svg)](https://www.sqlite.org/)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Online-success?style=flat&logo=render)](https://finanzapp-i59z.onrender.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents
- [Overview](#overview)
- [Key Features](#-key-features)
- [Technical Stack](#-technical-stack)
- [Architecture](#-architecture)
- [Installation](#-installation--setup)
- [Project Structure](#-project-structure)
- [Backend Highlights](#-backend-highlights)
- [Database Schema](#-database-schema)
- [Deployment](#-deployment)
- [Roadmap](#-roadmap)

## Overview

FinanzApp is a sophisticated personal finance tracker that helps users manage their financial health through predictive analytics and automated cash flow management. The system processes recurring income, credit card payments, installment plans, and loans to generate accurate biweekly financial projections up to 12 months in advance.

**Live Demo:** [https://finanzapp-i59z.onrender.com](https://finanzapp-i59z.onrender.com)

## 🚀 Key Features

### 📊 Smart Biweekly Projection Engine
- **Automated cash flow forecasting** up to 12 months ahead
- **Visual traffic light system** (🟢 Green: Healthy | 🟡 Yellow: Warning | 🔴 Red: Critical)
- **Customizable payment dates** with precise day-of-month calculations
- **Trend analysis** and minimum projected balance tracking
- Handles edge cases (month-end dates, leap years, invalid dates)

### 💳 Multi-Card Credit Management
- **Concurrent tracking** of multiple credit cards
- **Intelligent payment categorization**: Regular charges vs. Interest-Free Installments
- **Automated monthly payment calculations**
- **Due date alerts** with 15-day advance notifications
- **Expense aggregation** by card with detailed breakdowns

### 📈 Analytical Dashboard
- **Interactive visualizations** powered by Chart.js
- **Historical trend analysis** (income vs. expenses over time)
- **Category-based expense distribution**
- **Real-time balance updates** with transaction logging
- **Customizable date range filtering**

### 🎯 Purchase Impact Simulator
- **Pre-purchase financial impact analysis**
- **Side-by-side comparison** (with/without purchase scenarios)
- **Risk assessment** based on projected cash flow
- **Automatic recommendations** ("Safe to buy" / "Caution advised" / "Not recommended")
- **Multi-month impact visualization**

### 🔔 Intelligent Alert System
- **Payment reminders** (15-day advance window)
- **Critical balance warnings**
- **Upcoming installment notifications**
- **Custom alert thresholds**

## 🛠️ Technical Stack

### Backend
| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Core language | 3.9+ |
| **Flask** | Web framework | 3.0+ |
| **SQLite** | Database | 3.x |
| **python-dateutil** | Date calculations | 2.8+ |

### Frontend
| Technology | Purpose |
|------------|---------|
| **HTML5/CSS3** | Markup & styling |
| **JavaScript ES6+** | Client-side logic |
| **Chart.js** | Data visualization |
| **Responsive Design** | Mobile-first approach |

### DevOps & Deployment
- **Render.com** - Cloud hosting
- **Git/GitHub** - Version control
- **Environment Variables** - Configuration management

## 🏗️ Architecture

### Design Patterns
- **MVC Architecture** - Separation of concerns
- **Blueprint Pattern** - Modular route organization
- **Repository Pattern** - Database abstraction layer
- **Service Layer** - Business logic isolation

### Core Components
```
┌─────────────────────────────────────────────────────┐
│                   Flask Application                  │
├─────────────────────────────────────────────────────┤
│  Routes Layer         │  Services Layer             │
│  ├── Dashboard        │  ├── Projection Engine      │
│  ├── Transactions     │  ├── Alert System          │
│  ├── Cards            │  ├── Balance Calculator     │
│  └── Configuration    │  └── Date Handler          │
├─────────────────────────────────────────────────────┤
│              Database Layer (SQLite)                 │
│  ├── Transactions     │  ├── Credit Cards           │
│  ├── Recurring Income │  ├── Loans                  │
│  └── Installments     │  └── Configuration         │
└─────────────────────────────────────────────────────┘
```

## 📦 Installation & Setup

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Git

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/LuisTapia86/FinanzApp.git
cd FinanzApp

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set environment variable for demo data (optional)
# On Windows:
set USAR_DATOS_DEMO=false
# On macOS/Linux:
export USAR_DATOS_DEMO=false

# 6. Run the application
python app.py
```

The application will be available at `http://localhost:5000`

### Using Demo Data

To populate the application with demonstration data (recommended for first-time setup):

```bash
# Set the environment variable before running
export USAR_DATOS_DEMO=true  # Linux/macOS
set USAR_DATOS_DEMO=true     # Windows

python app.py
```

## 📁 Project Structure

```
FinanzApp/
├── app.py                      # Application entry point
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
│
├── database/
│   ├── __init__.py
│   └── db.py                   # Database initialization & migrations
│
├── routes/
│   ├── __init__.py             # Blueprint registration
│   ├── dashboard.py            # Dashboard endpoints
│   ├── ingresos.py             # Income management routes
│   ├── gastos.py               # Expense management routes
│   └── configuracion.py        # Settings routes
│
├── services/
│   ├── __init__.py
│   └── proyeccion.py           # Projection calculation engine
│
├── utils/
│   ├── __init__.py
│   ├── validators.py           # Input validation functions
│   └── helpers.py              # Utility functions
│
├── templates/
│   └── index.html              # Main application template
│
└── static/
    ├── css/                    # Stylesheets
    └── js/                     # JavaScript modules
```

## 💡 Backend Highlights

### 1. **Intelligent Date Handling**
```python
# Handles edge cases like month-end dates
def calculate_payment_date(day, month, year):
    """
    Safely calculates payment dates accounting for:
    - Invalid dates (e.g., Feb 31st → Feb 28/29)
    - Leap years
    - Month-end scenarios
    """
```

### 2. **Efficient Projection Algorithm**
- **O(n) time complexity** for projection calculations
- **Caching strategy** for recurring computations
- **Batch processing** for multi-month projections
- Handles concurrent data modifications safely

### 3. **Robust Error Handling**
- **Try-catch blocks** in all critical paths
- **User-friendly error messages** with flash notifications
- **Logging system** for debugging production issues
- **Input validation** at multiple layers

### 4. **Data Validation Layer**
```python
# Example from validators.py
def validate_amount(amount_str, field_name, minimum=0):
    """
    Validates monetary amounts with:
    - Type checking
    - Range validation
    - Precision handling
    - User-friendly error messages
    """
```

### 5. **Environment-Based Configuration**
- **Separate configs** for development/production
- **Environment variables** for sensitive data
- **Demo mode** controlled via `USAR_DATOS_DEMO` flag

## 🗄️ Database Schema

### Core Tables

**transactions** - Income and expense records
```sql
- id (PRIMARY KEY)
- type (income/expense)
- amount (DECIMAL)
- date (DATE)
- description (TEXT)
- category_id (FOREIGN KEY)
```

**credit_cards** - Credit card management
```sql
- id (PRIMARY KEY)
- name (VARCHAR)
- billing_date (INTEGER)
- payment_date (INTEGER)
- credit_limit (DECIMAL)
- active (BOOLEAN)
```

**installments** - MSI (Interest-Free) purchases
```sql
- id (PRIMARY KEY)
- card_id (FOREIGN KEY)
- total_amount (DECIMAL)
- monthly_payment (DECIMAL)
- months_total (INTEGER)
- months_remaining (INTEGER)
- start_date (DATE)
```

**recurring_income** - Salary, payroll, etc.
```sql
- id (PRIMARY KEY)
- name (VARCHAR)
- amount (DECIMAL)
- payment_day (INTEGER)
- start_date (DATE)
- end_date (DATE)
- frequency (monthly/biweekly)
```

## 🚀 Deployment

### Render.com (Recommended)

1. Fork/clone this repository
2. Create a new Web Service on [Render.com](https://render.com)
3. Connect your GitHub repository
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
   - **Environment Variable:** `USAR_DATOS_DEMO=true`
5. Deploy automatically on every push to main

### Railway.app (Alternative)

```bash
# Install Railway CLI
npm install -g railway

# Login and initialize
railway login
railway init

# Deploy
railway up
```

## 🗺️ Roadmap

### Upcoming Features
- [ ] 💰 **Cashback Tracking Module** - Category-based cashback calculation and projections
- [ ] 📈 **Investment Portfolio Manager** - Track stocks, bonds, and crypto with ROI calculations
- [ ] 🔐 **Multi-user Authentication** - User accounts with JWT-based auth
- [ ] 📊 **Advanced Analytics** - ML-based spending pattern recognition
- [ ] 📱 **Mobile App** - React Native companion app
- [ ] 🌐 **RESTful API** - Public API for third-party integrations
- [ ] 🧪 **Unit Testing** - pytest suite with >80% coverage
- [ ] 📧 **Email Notifications** - Automated payment reminders

### Backend Improvements
- [ ] Redis caching layer
- [ ] PostgreSQL migration (from SQLite)
- [ ] GraphQL API
- [ ] Celery task queue for async operations
- [ ] Docker containerization
- [ ] CI/CD pipeline with GitHub Actions

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linter
flake8 .

# Format code
black .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

**Developer:** Luis Tapia
**GitHub:** [@LuisTapia86](https://github.com/LuisTapia86)
**Project Link:** [https://github.com/LuisTapia86/FinanzApp](https://github.com/LuisTapia86/FinanzApp)

---

⭐ **Star this repository if you found it helpful!**
