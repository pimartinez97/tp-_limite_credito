from pathlib import Path

import numpy as np
import pandas as pd

possible_paths = [
    Path.home() / "data" / "raw" / "df_finalTP_LIMITE_CREDITOS_TARGET.xlsx",
    Path.home() / "tp" / "df_finalTP_LIMITE_CREDITOS_TARGET.xlsx",
]

DATA_PATH = next((path for path in possible_paths if path.exists()), None)

if DATA_PATH is None:
    raise FileNotFoundError(
        "No se encontró el Excel. Revisá data/raw/ o tp/."
    )

df = pd.read_excel(DATA_PATH)

# Referencia: distribución similar al entrenamiento.
# Producción: ventana simulada de clientes recientes.
referencia = df.sample(frac=0.70, random_state=42)
produccion = df.drop(referencia.index)

columnas = [
    "Credit_Limit",
    "AGE",
    "PAY_0",
    "BILL_AMT1",
    "PAY_AMT1",
    "DEFAULT",
]


def calcular_psi(esperado, actual, bins=10):
    esperado = esperado.dropna().to_numpy()
    actual = actual.dropna().to_numpy()

    cortes = np.unique(
        np.quantile(esperado, np.linspace(0, 1, bins + 1))
    )

    if len(cortes) < 2:
        return 0.0

    cortes[0] = -np.inf
    cortes[-1] = np.inf

    esperado_pct = np.histogram(esperado, bins=cortes)[0] / len(esperado)
    actual_pct = np.histogram(actual, bins=cortes)[0] / len(actual)

    esperado_pct = np.clip(esperado_pct, 0.0001, None)
    actual_pct = np.clip(actual_pct, 0.0001, None)

    return np.sum(
        (actual_pct - esperado_pct)
        * np.log(actual_pct / esperado_pct)
    )


print(f"Fuente: {DATA_PATH}\n")
print(f"{'Variable':<18} {'PSI':>8}  Estado")
print("-" * 46)

for columna in columnas:
    psi = float(calcular_psi(referencia[columna], produccion[columna]))

    if psi < 0.10:
        estado = "estable"
    elif psi < 0.25:
        estado = "cambio moderado"
    else:
        estado = "drift fuerte"

    print(f"{columna:<18} {psi:>8.4f}  {estado}")
