# Recomendador de Límite de Crédito

PoC de MLOps para recomendar límites de crédito mediante un modelo predictivo expuesto a través de una API FastAPI.

> Demo académica con datos anonimizados/sintéticos. La recomendación no reemplaza la revisión humana.

## Qué resuelve

A partir de datos financieros y de comportamiento de pago, el modelo estima un límite de crédito recomendado y devuelve una decisión:

- `Aumentar`
- `Mantener`
- `Reducir`

La solución incluye:

- API FastAPI;
- interfaz de evaluación individual;
- validación de cartera Excel;
- revisión humana de la recomendación;
- dashboard de la sesión;
- logs y monitoreo en Google Cloud Run.

## Estructura del proyecto

```text
.
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── observability.py
│   └── static/
│       ├── index.html
│       ├── ingesta.html
│       └── dashboard.html
├── data/
│   └── fixtures/
│       └── customer-example.json
├── models/
│   ├── credito-limite.joblib
│   └── credito-limite-metrics.json
├── scripts/
│   ├── check_drift.py
│   └── smoke_load.py
├── Dockerfile
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.12 o superior
- Git
- Docker (opcional, para ejecutar mediante contenedor)
- Acceso al repositorio privado

El archivo `models/credito-limite.joblib` es obligatorio: contiene el modelo ya entrenado.

---

# Verificación de reproducibilidad

Estos pasos permiten levantar una copia independiente del proyecto sin usar Cloud Shell, GCP ni credenciales de otra persona.

## 1. Clonar el repositorio

```bash
git clone https://github.com/pimartinez97/tp-_limite_credito.git
cd tp-_limite_credito
```

Si el repositorio ya había sido clonado anteriormente, actualizarlo:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
```

## 2. Verificar los archivos indispensables

```bash
ls -l requirements.txt
ls -l models/credito-limite.joblib
ls -l models/credito-limite-metrics.json
```

Los tres comandos deben mostrar archivos existentes.

## 3. Crear el entorno e instalar dependencias

Mac/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade -r requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade -r requirements.txt
```

## 4. Iniciar la API

Mac/Linux:

```bash
export MODEL_PATH="models/credito-limite.joblib"
export METRICS_PATH="models/credito-limite-metrics.json"

uvicorn app.main:app --host 0.0.0.0 --port 8080 > api.log 2>&1 &
```

Windows PowerShell:

```powershell
$env:MODEL_PATH="models/credito-limite.joblib"
$env:METRICS_PATH="models/credito-limite-metrics.json"

uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## 5. Comprobar que el servicio funciona

Mac/Linux:

```bash
sleep 3
curl http://localhost:8080/health
```

Resultado esperado:

```json
{"status":"ok","model_loaded":true,"model_version":"credito-limite"}
```

Si no responde, revisar el error de inicio:

```bash
cat api.log
```

## 6. Probar una predicción

```bash
curl -X POST "http://localhost:8080/predict" \
  -H "Content-Type: application/json" \
  -d @data/fixtures/customer-example.json
```

La respuesta debe contener:

```text
model_version
assigned_credit_limit_pred
credit_limit_actual
umbral_abs
decision
```

El valor de `decision` será `Aumentar`, `Mantener` o `Reducir`.

## 7. Abrir la interfaz web

Abrir en un navegador:

```text
http://localhost:8080
```

Pantallas disponibles:

| Ruta | Descripción |
|---|---|
| `/` | Ficha de evaluación crediticia y revisión humana |
| `/ingesta` | Validación de un archivo Excel de cartera |
| `/dashboard` | Resumen de actividad de la sesión |
| `/docs` | Documentación Swagger/OpenAPI |
| `/health` | Estado del modelo y de la API |

---

# Ejecución con Docker

Construir la imagen:

```bash
docker build -t credito-api .
```

Ejecutar el contenedor:

```bash
docker run --rm -p 8080:8080 credito-api
```

Luego abrir:

```text
http://localhost:8080
```

---

# Despliegue y operación

La PoC fue desplegada en Google Cloud Run como servicio privado mediante IAM.

La operación incluye:

- endpoints `/health`, `/predict` y `/batch-score`;
- logs estructurados de predicción;
- métricas de solicitudes, latencia y errores;
- revisiones de Cloud Run para rollback;
- validación de drift mediante PSI;
- interfaz de evaluación, ingesta y dashboard.

# Privacidad y uso responsable

- Los datos de demostración son anonimizados o sintéticos.
- No se incluyen datos personales identificables.
- El Excel original no se publica en el repositorio.
- El dashboard no usa una base de datos: resume la sesión actual del navegador.
- La recomendación debe ser revisada por un analista.
- El repositorio y el servicio desplegado se mantienen privados.
