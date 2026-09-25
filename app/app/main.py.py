import json 
from io import BytesIO
import os
from typing import Literal
import time
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from app.observability import log_prediction
import joblib
import pandas as pd
from pydantic import BaseModel
from pathlib import Path
from fastapi.responses import FileResponse

app = FastAPI(
    title="API de Límite de Crédito",
    description="Predice el límite de crédito recomendado por cliente.",
    version="1.0.0",
)

BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(BASE_DIR / "static" / "index.html")
REQUIRED_INPUT_COLUMNS = [
    "Credit_Limit",
    "SEX",
    "EDUCATION",
    "MARRIAGE",
    "AGE",
    "PAY_0",
    "PAY_2",
    "PAY_3",
    "PAY_4",
    "PAY_5",
    "PAY_6",
    "BILL_AMT1",
    "BILL_AMT2",
    "BILL_AMT3",
    "BILL_AMT4",
    "BILL_AMT5",
    "BILL_AMT6",
    "PAY_AMT1",
    "PAY_AMT2",
    "PAY_AMT3",
    "PAY_AMT4",
    "PAY_AMT5",
    "PAY_AMT6",
    "DEFAULT",
]

TARGET_COLUMN = "Assigned_Credit_Limit"


@app.get("/ingesta", include_in_schema=False)
def ingestion_page():
    return FileResponse(BASE_DIR / "static" / "ingesta.html")

@app.get("/dashboard", include_in_schema=False)
def dashboard_page():
    return FileResponse(BASE_DIR / "static" / "dashboard.html")


@app.post("/validate-dataset")
async def validate_dataset(file: UploadFile = File(...)):
    filename = file.filename or ""

    if not filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Seleccioná un archivo Excel con extensión .xlsx.",
        )

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="El archivo está vacío.",
        )

    if len(file_content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="El archivo supera el máximo permitido de 10 MB.",
        )

    try:
        df = pd.read_excel(BytesIO(file_content))
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="No fue posible leer el Excel. Verificá el formato del archivo.",
        )

    missing_columns = [
        column
        for column in REQUIRED_INPUT_COLUMNS
        if column not in df.columns
    ]

    available_columns = [
        column
        for column in REQUIRED_INPUT_COLUMNS
        if column in df.columns
    ]

    null_values = int(df[available_columns].isna().sum().sum())

    non_numeric_columns = []

    for column in available_columns:
        converted = pd.to_numeric(df[column], errors="coerce")
        original_non_null = df[column].notna()

        if converted[original_non_null].isna().any():
            non_numeric_columns.append(column)

    duplicate_ids = 0

    if "ID" in df.columns:
        duplicate_ids = int(df["ID"].duplicated().sum())

    target_available = TARGET_COLUMN in df.columns

    valid_for_training = (
        not missing_columns
        and not non_numeric_columns
        and null_values == 0
        and target_available
    )

    print(
        json.dumps(
            {
                "event": "dataset_validation",
                "rows": int(len(df)),
                "columns": int(len(df.columns)),
                "valid_for_training": valid_for_training,
            }
        )
    )

    return {
        "filename": filename,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "target_available": target_available,
        "missing_columns": missing_columns,
        "null_values": null_values,
        "non_numeric_columns": non_numeric_columns,
        "duplicate_ids": duplicate_ids,
        "valid_for_training": valid_for_training,
        "message": (
            "Dataset apto para el flujo de entrenamiento."
            if valid_for_training
            else "Dataset requiere correcciones antes del entrenamiento."
        ),
    }
MODEL_PATH = Path(
    os.environ.get("MODEL_PATH", "models/credito-limite.joblib")
)
UMBRAL_PCT = 0.10
BREAK_MODEL = os.environ.get("BREAK_MODEL", "0") == "1"

METRICS_PATH = Path(
    os.environ.get(
        "METRICS_PATH",
        "models/credito-limite-metrics.json"
    )
)

loaded_model = joblib.load(MODEL_PATH)

# Admite ambos formatos: Pipeline directo o artefacto con pipeline + metadata.
if isinstance(loaded_model, dict) and "pipeline" in loaded_model:
    pipeline = loaded_model["pipeline"]
    metadata = loaded_model["metadata"]
else:
    pipeline = loaded_model
    metadata = json.loads(METRICS_PATH.read_text())

MODEL_VERSION = metadata.get("model_version", "credito-limite")


class Cliente(BaseModel):
    Credit_Limit: float
    SEX: int
    EDUCATION: int
    MARRIAGE: int
    AGE: int
    PAY_0: int
    PAY_2: int
    PAY_3: int
    PAY_4: int
    PAY_5: int
    PAY_6: int
    BILL_AMT1: float
    BILL_AMT2: float
    BILL_AMT3: float
    BILL_AMT4: float
    BILL_AMT5: float
    BILL_AMT6: float
    PAY_AMT1: float
    PAY_AMT2: float
    PAY_AMT3: float
    PAY_AMT4: float
    PAY_AMT5: float
    PAY_AMT6: float
    DEFAULT: int


class Prediccion(BaseModel):
    model_version: str
    assigned_credit_limit_pred: float
    credit_limit_actual: float
    umbral_abs: float
    decision: Literal["Aumentar", "Reducir", "Mantener"]


def predecir(cliente: Cliente) -> Prediccion:
    if BREAK_MODEL:
        raise HTTPException(
            status_code=503,
            detail="Modelo no disponible: falla simulada para rollback",
        )

    inicio = time.perf_counter()

    entrada = pd.DataFrame([cliente.model_dump()])
    limite_predicho = float(pipeline.predict(entrada)[0])

    limite_actual = cliente.Credit_Limit
    umbral_abs = limite_actual * UMBRAL_PCT

    if limite_predicho > limite_actual + umbral_abs:
        decision = "Aumentar"
    elif limite_predicho < limite_actual - umbral_abs:
        decision = "Reducir"
    else:
        decision = "Mantener"

    respuesta = Prediccion(
        model_version=MODEL_VERSION,
        assigned_credit_limit_pred=round(limite_predicho, 2),
        credit_limit_actual=limite_actual,
        umbral_abs=round(umbral_abs, 2),
        decision=decision,
    )

    latencia_ms = (time.perf_counter() - inicio) * 1000
    log_prediction(latencia_ms, decision, MODEL_VERSION)

    return respuesta


@app.get("/health")
def health():
    if BREAK_MODEL:
        return {
            "status": "degraded",
            "model_loaded": False,
            "model_version": MODEL_VERSION,
        }

    return {
        "status": "ok",
        "model_loaded": True,
        "model_version": MODEL_VERSION,
    }


@app.post("/predict", response_model=Prediccion)
def predict(cliente: Cliente):
    return predecir(cliente)


@app.post("/batch-score", response_model=list[Prediccion])
def batch_score(clientes: list[Cliente]):
    return [predecir(cliente) for cliente in clientes]
