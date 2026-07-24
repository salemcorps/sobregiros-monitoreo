# Sobregiros Monitoreo

Prueba técnico-funcional — Monitoreo de cuentas corrientes embargadas con sobregiro.

---

## Descripción del problema

Cuando una cuenta corriente embargada recibe un crédito y tiene saldo de sobregiro pendiente, el sistema aplica primero los intereses y capital del sobregiro (transacciones `INT_SOB` y `CAP_SOB`), agotando el saldo disponible. Al día siguiente, la Gerencia de Embargos ejecuta un débito manual con la transacción `006`, la cual no tiene autorización para operar sobre el cupo de sobregiro, generando su rechazo. Esto incumple la prelación legal de los embargos sobre cualquier cobro interno.

Este repositorio contiene el análisis, diseño funcional, modelamiento de datos, visualización y cierre ejecutivo propuestos para abordar el problema.

---

## Estructura del proyecto

```
sobregiros-monitoreo/
├── data/
│   └── sobregiros.db          # Base de datos SQLite con el caso de análisis
├── src/
│   ├── __init__.py
│   ├── database.py            # Clase DatabaseConnector
│   ├── monitor.py             # Clase SobregirosMonitor (lógica principal)
│   ├── clasificador.py        # Clase ClasificadorCasos
│   └── reporte.py             # Clase GeneradorReporte
├── queries/
│   └── monitor_diario.sql     # Query principal de monitoreo
├── tests/
│   └── test_monitor.py        # Pruebas unitarias
├── docs/
│   ├── proceso_as_is.md       # Diagrama y análisis del proceso actual
│   ├── proceso_to_be.md       # Diseño funcional propuesto
│   └── cierre_ejecutivo.md    # Resumen ejecutivo
├── main.py                    # Punto de entrada
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Base de datos

Archivo: `data/sobregiros.db` (SQLite)

| Tabla | Filas | Descripción |
|---|---|---|
| `cuentas` | 7.000 | Snapshot diario de cuentas corrientes y de ahorro |
| `embargos` | 88 | Órdenes de embargo activas, cubiertas y levantadas |
| `movimientos` | 21.303 | Transacciones del período 2026-07-15 al 2026-07-21 |

---

## Instalación

### Requisitos

- Python 3.10 o superior
- pip

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/salemcorps/sobregiros-monitoreo.git
cd sobregiros-monitoreo

# 2. Crear y activar el ambiente virtual
python -m venv venv

# En Mac/Linux:
source venv/bin/activate

# En Windows:
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## Uso

```bash
# Ejecutar el monitoreo diario
python main.py

# Ejecutar las pruebas unitarias
pytest tests/
```

---

## Dependencias

```
pandas
pytest
```

> `sqlite3` es parte de la librería estándar de Python, no requiere instalación adicional.

---

## Actividades

| # | Actividad | Rama | Estado |
|---|---|---|---|
| 1 | Análisis del problema (As Is) | `actividad-1-analisis` | ✅ Completo |
| 2 | Diseño funcional (To Be) | `actividad-2-diseno` | 🔄 En progreso |
| 3 | Modelamiento de datos | `actividad-3-modelamiento` | ⏳ Pendiente |
| 4 | Visualización | `actividad-4-visualizacion` | ⏳ Pendiente |
| 5 | Cierre ejecutivo | `actividad-5-ejecutivo` | ⏳ Pendiente |

---

## Supuestos

- La base de datos representa un corte del período 2026-07-15 al 2026-07-21.
- Las cuentas con `cod_aplicacion = 'CTE'` son las cuentas corrientes objeto del análisis.
- Un embargo se considera activo cuando `estado_embargo = 'ACTIVO'` y `saldo_pendiente_embargo > 0`.
- Una cuenta está sobregirada cuando `sld_actual < 0`.
- La transacción `006` corresponde al débito manual de embargo ejecutado por la Gerencia de Embargos.
- La prelación legal establece que el embargo tiene prioridad sobre cualquier cobro de sobregiro (intereses o capital).

---

## Autor

**[Juan Andrés Valdés Ramírez]**  
Prueba técnico-funcional — Análisis de datos  
[juanexbmth@gmail.com]
