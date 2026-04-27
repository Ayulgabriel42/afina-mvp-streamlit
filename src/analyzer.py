import unicodedata
import pandas as pd


FINANCIAL_KEYWORDS = {
    "Activos": [
        "activo", "activos corrientes", "activo corriente", "activo no corriente",
        "efectivo", "caja", "banco", "bancos", "cuentas corrientes",
        "cuentas por cobrar", "clientes", "deudores", "inventario", "inventarios",
        "existencias", "mercaderia", "mercadería"
    ],
    "Pasivos": [
        "pasivo", "pasivos corrientes", "pasivo corriente", "pasivo no corriente",
        "cuentas por pagar", "proveedores", "deuda", "deudas",
        "obligaciones", "prestamos", "préstamos", "acreedores"
    ],
    "Patrimonio": [
        "patrimonio", "capital", "capital social", "resultados acumulados",
        "reserva", "reservas", "utilidades retenidas"
    ],
    "Resultados": [
        "ventas", "ingresos", "ingreso", "costo de ventas", "costos",
        "gastos", "gasto", "ebit", "ebitda", "resultado operativo",
        "utilidad", "utilidad neta", "ganancia", "perdida", "pérdida",
        "margen", "margen operativo"
    ],
    "Flujo de caja": [
        "flujo", "flujo de caja", "cash flow", "fco", "flujo operativo",
        "capex", "inversion", "inversión", "financiamiento",
        "financiacion", "financiación"
    ],
    "Capital de trabajo": [
        "capital de trabajo", "cuentas por cobrar", "cuentas por pagar",
        "inventarios", "stock", "proveedores", "clientes"
    ]
}


def normalize_text(value):
    """
    Normaliza texto para facilitar búsquedas:
    - pasa a minúsculas
    - elimina acentos
    - limpia espacios
    """
    if pd.isna(value):
        return ""

    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join([c for c in text if not unicodedata.combining(c)])
    text = " ".join(text.split())

    return text


def row_to_readable_text(row):
    """
    Convierte una fila en un texto legible, usando solo valores no vacíos.
    """
    values = []

    for value in row:
        if pd.notna(value):
            text = str(value).strip()
            if text and text.lower() != "none":
                values.append(text)

    return " | ".join(values[:6])


def detect_financial_accounts(df, max_examples_per_category=8):
    """
    Busca posibles cuentas financieras dentro del DataFrame.
    Devuelve categorías detectadas y ejemplos de filas.
    """
    detections = {}

    for category, keywords in FINANCIAL_KEYWORDS.items():
        detections[category] = {
            "count": 0,
            "matches": []
        }

    for index, row in df.iterrows():
        readable_row = row_to_readable_text(row)

        if not readable_row:
            continue

        normalized_row = normalize_text(readable_row)

        for category, keywords in FINANCIAL_KEYWORDS.items():
            for keyword in keywords:
                normalized_keyword = normalize_text(keyword)

                if normalized_keyword in normalized_row:
                    detections[category]["count"] += 1

                    if len(detections[category]["matches"]) < max_examples_per_category:
                        detections[category]["matches"].append({
                            "fila": int(index),
                            "coincidencia": keyword,
                            "detalle": readable_row
                        })

                    break

    return detections


def analyze_data_quality(df):
    """
    Genera un diagnóstico básico de calidad de datos.
    """
    total_cells = df.shape[0] * df.shape[1]

    if total_cells == 0:
        empty_percentage = 100
    else:
        empty_cells = int(df.isna().sum().sum())
        empty_percentage = round((empty_cells / total_cells) * 100, 2)

    unnamed_columns = [
        col for col in df.columns
        if str(col).lower().startswith("unnamed")
    ]

    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    text_columns = df.select_dtypes(include=["object"]).columns.tolist()

    warnings = []

    if len(unnamed_columns) > 0:
        warnings.append(
            f"Se detectaron {len(unnamed_columns)} columnas sin nombre. Puede ser necesario normalizar encabezados."
        )

    if empty_percentage > 40:
        warnings.append(
            f"El archivo tiene {empty_percentage}% de celdas vacías. Puede contener estructuras contables con bloques separados."
        )

    if len(numeric_columns) == 0:
        warnings.append(
            "No se detectaron columnas numéricas claras. Puede ser necesario limpiar el archivo antes de calcular KPIs."
        )

    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "empty_percentage": empty_percentage,
        "unnamed_columns_count": len(unnamed_columns),
        "numeric_columns_count": len(numeric_columns),
        "text_columns_count": len(text_columns),
        "warnings": warnings
    }


def calculate_detection_score(detections):
    """
    Calcula un score simple según la cantidad de categorías financieras detectadas.
    """
    total_categories = len(detections)
    detected_categories = sum(
        1 for item in detections.values()
        if item["count"] > 0
    )

    if total_categories == 0:
        return 0

    return round((detected_categories / total_categories) * 100, 1)


def analyze_financial_dataframe(df, metadata=None):
    """
    Genera un preanálisis financiero básico.
    """
    detections = detect_financial_accounts(df)
    quality = analyze_data_quality(df)
    detection_score = calculate_detection_score(detections)

    total_matches = sum(
        item["count"] for item in detections.values()
    )

    detected_categories = [
        category for category, item in detections.items()
        if item["count"] > 0
    ]

    if detection_score >= 70:
        status = "Bueno"
        status_detail = "El archivo contiene varias partidas financieras detectables."
    elif detection_score >= 40:
        status = "Parcial"
        status_detail = "El archivo contiene algunas partidas financieras, pero puede requerir limpieza."
    else:
        status = "Bajo"
        status_detail = "AFINA detectó pocas partidas financieras. Conviene revisar hoja, período o estructura."

    return {
        "metadata": metadata or {},
        "detections": detections,
        "quality": quality,
        "detection_score": detection_score,
        "total_matches": total_matches,
        "detected_categories": detected_categories,
        "status": status,
        "status_detail": status_detail
    }
