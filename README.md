# tp-_limite_credito
Tp Implementación de Aplicaciones de Aprendizaje Automático en la Nube - Martinez y Calandri

# Recomendador de Límite de Crédito

PoC de MLOps para apoyar al Área de Riesgo Crediticio en la recomendación de límites de crédito.

La solución expone un modelo predictivo mediante una API FastAPI, una interfaz web para evaluación individual, validación de archivos Excel y un dashboard operativo de la sesión.

> Demo académica con datos anonimizados/sintéticos. La recomendación del modelo no reemplaza la revisión humana.

---

## Objetivo

A partir de información financiera y de comportamiento de pago de un cliente, el modelo estima un límite de crédito recomendado y devuelve una decisión de negocio:

- **Aumentar**
- **Mantener**
- **Reducir**

La decisión utiliza un umbral de tolerancia del 10% respecto del límite actual.

---

## Arquitectura

```text
Excel anonimizado/sintético
          │
          ▼
Validación de cartera (/ingesta)
          │
          ▼
Modelo entrenado (.joblib)
          │
          ▼
API FastAPI
(/health, /predict, /batch-score)
          │
          ▼
Ficha de evaluación crediticia
          │
          ▼
Recomendación y revisión humana
          │
          ▼
Dashboard, logs y métricas operativas
```

---

## Estructura del repositorio

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

---

## Requisitos

- Python 3.12 o superior
- Docker (opcional, recomendado para reproducir el despliegue)
- Acceso al repositorio privado
- El archivo `models/credito-limite.joblib`

El archivo `.joblib` es el artefacto binario del modelo entrenado. Es indispensable para ejecutar inferencias.

---

## Ejecución local

### 1. Clonar el repositorio

```bash
git clone https://github.com/pimartinez97/tp-_limite_credito.git
cd tp-_limite_credito
```

### 2. Crear y activar un entorno virtual

Mac/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Verificar que existe el modelo

Debe existir este archivo:

```text
models/credito-limite.joblib
```

También debe existir:

```text
models/credito-limite-metrics.json
```

### 5. Levantar la API y la interfaz

```bash
export MODEL_PATH="models/credito-limite.joblib"
export METRICS_PATH="models/credito-limite-metrics.json"

---

## Verificación de reproducibilidad

Una persona con acceso al repositorio debe poder ejecutar la solución sin utilizar Cloud Shell ni credenciales de Google Cloud.

### Pasos de validación

```bash
git clone https://github.com/pimartinez97/tp-_limite_credito.git
cd tp-_limite_credito

docker build -t credito-api .
docker run --rm -p 8080:8080 credito-api
```

En una segunda terminal:

```bash
curl http://localhost:8080/health
```

Resultado esperado:

```json
{
  "status": "ok",
  "model_loaded": true,
  "model_version": "credito-limite"
}
```

Luego:

```bash
curl -X POST "http://localhost:8080/predict" \
  -H "Content-Type: application/json" \
  -d @data/fixtures/customer-example.json
```

La respuesta debe contener una recomendación `Aumentar`, `Mantener` o `Reducir`.

Finalmente, abrir:

```text
http://localhost:8080
```

Debe visualizarse la ficha de evaluación crediticia, permitir solicitar una recomendación y registrar la revisión humana en la sesión del navegador.

> Requisito: el repositorio debe incluir `models/credito-limite.joblib`. Sin el artefacto del modelo no es posible ejecutar inferencias.
