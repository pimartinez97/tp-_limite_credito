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
- Acceso al repositorio privado

El archivo `models/credito-limite.joblib` es obligatorio: contiene el modelo ya entrenado.

---

# Verificación de reproducibilidad

Estos pasos permiten levantar una copia independiente del proyecto en Cloud Shell, sin utilizar el proyecto de GCP ni las credenciales de otra persona.

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

En Cloud Shell ejecutar:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade -r requirements.txt
```

> Aunque se abra Cloud Shell desde una computadora Windows, Cloud Shell utiliza Linux. Por eso se deben usar estos comandos y no las rutas `Scripts\` de Windows.

## 4. Iniciar la API

Abrir una primera terminal y ejecutar:

```bash
cd ~/tp-_limite_credito
source .venv/bin/activate

export MODEL_PATH="models/credito-limite.joblib"
export METRICS_PATH="models/credito-limite-metrics.json"

uvicorn app.main:app --host 0.0.0.0 --port 8080
```

La terminal debe mostrar:

```text
Uvicorn running on http://0.0.0.0:8080
```

Mantener esta terminal abierta mientras se realizan las pruebas.

## 5. Comprobar que el servicio funciona

Abrir una segunda terminal y ejecutar:

```bash
curl -i http://127.0.0.1:8080/health
```

Resultado esperado:

```text
HTTP/1.1 200 OK
```

```json
{"status":"ok","model_loaded":true,"model_version":"credito-limite"}
```

En la primera terminal se registrará:

```text
GET /health HTTP/1.1" 200 OK
```

## 6. Probar una predicción

En la segunda terminal, ejecutar:

```bash
cd ~/tp-_limite_credito

curl -i -X POST "http://127.0.0.1:8080/predict" \
  -H "Content-Type: application/json" \
  -d @data/fixtures/customer-example.json
```

La respuesta debe devolver:

```text
HTTP/1.1 200 OK
```

y contener:

```text
model_version
assigned_credit_limit_pred
credit_limit_actual
umbral_abs
decision
```

El valor de `decision` será `Aumentar`, `Mantener` o `Reducir`.

## 7. Abrir la interfaz web en Cloud Shell

Con Uvicorn ejecutándose en la primera terminal:

1. En la parte superior derecha de Cloud Shell, hacer clic en **Web Preview**.
2. Elegir **Preview on port 8080**.
3. Se abrirá una URL temporal propia de la sesión de Cloud Shell.

La pantalla inicial mostrará:

```text
Recomendador de Límite de Crédito
PoC para apoyar decisiones del Área de Riesgo Crediticio.
```

Desde esa pantalla se puede acceder a:

| Sección | Uso |
|---|---|
| Recomendador de Límite de Crédito | Evaluación individual, recomendación y revisión humana |
| Ingesta y validación de cartera | Validación de un archivo Excel antes de utilizarlo en el flujo |
| Dashboard de operación | Resumen de evaluaciones y decisiones de la sesión |
---

````markdown
Cuando terminen las pruebas y la navegación por la interfaz, volver a la primera terminal y presionar:

```text
Ctrl + C

# Despliegue y operación

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
