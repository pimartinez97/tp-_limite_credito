# Recomendador de Límite de Crédito

PoC de MLOps para apoyar al Área de Riesgo Crediticio mediante recomendaciones de límite de crédito.

> Demo académica con datos anonimizados/sintéticos. La recomendación no reemplaza la revisión humana.

## Objetivo

El modelo recibe información financiera y de comportamiento de pago de un cliente. Devuelve un límite de crédito recomendado y una decisión:

- Aumentar
- Mantener
- Reducir

La solución incluye API, interfaz web, validación de cartera, revisión humana, logs y despliegue en Google Cloud Run.

## Arquitectura

```text
Datos anonimizados/sintéticos
        │
        ▼
Validación de cartera (/ingesta)
        │
        ▼
Modelo entrenado (.joblib)
        │
        ▼
API FastAPI
        │
        ▼
Ficha de evaluación crediticia
        │
        ▼
Recomendación + revisión humana
        │
        ▼
Dashboard y observabilidad
```

## Estructura

```text
app/
├── __init__.py
├── main.py
├── observability.py
└── static/
    ├── index.html
    ├── ingesta.html
    └── dashboard.html

data/fixtures/
└── customer-example.json

models/
├── credito-limite.joblib
└── credito-limite-metrics.json

scripts/
├── check_drift.py
└── smoke_load.py

Dockerfile
requirements.txt
README.md
```

## Ejecución local y verificación de reproducibilidad

Una persona con acceso al repositorio puede ejecutar el proyecto sin usar Cloud Shell ni credenciales de Google Cloud.

### 1. Clonar el repositorio

```bash
git clone https://github.com/pimartinez97/tp-_limite_credito.git
cd tp-_limite_credito
```

### 2. Crear entorno e instalar dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Verificar el modelo

```bash
ls models
```

Deben aparecer:

```text
credito-limite.joblib
credito-limite-metrics.json
```

> `credito-limite.joblib` es el modelo entrenado y es indispensable para realizar predicciones.

### 4. Iniciar la API

```bash
export MODEL_PATH="models/credito-limite.joblib"
export METRICS_PATH="models/credito-limite-metrics.json"

uvicorn app.main:app --host 0.0.0.0 --port 8080 > api.log 2>&1 &
```

### 5. Verificar el estado del servicio

```bash
sleep 3
curl http://localhost:8080/health
```

Resultado esperado:

```json
{"status":"ok","model_loaded":true,"model_version":"credito-limite"}
```

### 6. Probar una predicción

```bash
curl -X POST "http://localhost:8080/predict" \
  -H "Content-Type: application/json" \
  -d @data/fixtures/customer-example.json
```

La respuesta debe contener:

- `assigned_credit_limit_pred`
- `credit_limit_actual`
- `umbral_abs`
- `decision`

La decisión será `Aumentar`, `Mantener` o `Reducir`.

### 7. Abrir la interfaz

Con la API ejecutándose, abrir:

```text
http://localhost:8080
```

Pantallas disponibles:

| Ruta | Función |
|---|---|
| `/` | Ficha de evaluación crediticia |
| `/ingesta` | Validación de cartera Excel |
| `/dashboard` | Indicadores de actividad de la sesión |
| `/docs` | Documentación Swagger de la API |
| `/health` | Estado del modelo y del servicio |

## Ejecución con Docker

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

## Despliegue

La PoC fue desplegada en Google Cloud Run como servicio privado mediante IAM.

Incluye:

- API FastAPI con endpoints `/health`, `/predict` y `/batch-score`;
- imagen Docker;
- Artifact Registry y Cloud Build;
- logs estructurados de inferencia;
- métricas de solicitudes, latencia y errores;
- revisiones de Cloud Run para rollback;
- validación de drift mediante PSI.

## Privacidad y uso responsable

- Se utilizan datos anonimizados o sintéticos.
- No se publican datos personales identificables.
- La interfaz no persiste información de clientes en una base de datos.
- El dashboard resume únicamente la sesión actual del navegador.
- La recomendación del modelo requiere revisión humana.
- El repositorio y el servicio de producción se mantienen privados.
