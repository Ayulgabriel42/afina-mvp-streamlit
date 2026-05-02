import json
import re
from datetime import datetime, timezone

import pandas as pd


STATUS_POINTS = {
    "Verde": 100,
    "Amarillo": 50,
    "Rojo": 0,
    "Sin datos": 0,
    "Sin umbral": 50,
}


DIMENSION_ORDER = [
    "Estructura de inversión",
    "Capital de trabajo",
    "Rentabilidad",
    "Fluidez financiera",
    "Equilibrio financiero",
]


def clean_value(value):
    """
    Convierte valores de pandas/numpy a tipos JSON seguros.
    """
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    return value


def clean_text(value, max_length=160):
    """
    Limpia textos largos o ruidosos para evitar ensuciar el JSON y el futuro prompt de IA.
    Ejemplo: filas originales con muchos valores separados por '|'.
    """
    value = clean_value(value)

    if value is None:
        return None

    text = str(value).strip()
    text = " ".join(text.split())

    if "|" in text:
        parts = [part.strip() for part in text.split("|") if part.strip()]
        if parts:
            # Conservamos la descripción principal y descartamos valores arrastrados de la fila.
            text = parts[0]

    # Elimina secuencias muy largas de números que suelen venir de filas originales.
    text = re.sub(r"\s+-?\d+(\.\d+)?(\s+-?\d+(\.\d+)?){2,}", "", text)

    if len(text) > max_length:
        return text[:max_length].rstrip() + "..."

    return text


def infer_company_name(company_name, source_file):
    """
    Inferencia simple para evitar que el snapshot quede como 'Empresa analizada'
    cuando el archivo contiene un nombre útil.
    """
    if company_name and company_name not in ["Empresa analizada", "No identificado"]:
        return company_name

    if source_file:
        name = str(source_file)
        name = name.replace(".xlsx", "").replace(".xls", "").replace(".csv", "").replace(".pdf", "")
        name = re.sub(r"\s*\(\d+\)\s*$", "", name).strip()

        if name and name not in ["Archivo financiero cargado", "No disponible"]:
            return name

    return "Empresa analizada"


def df_to_records(df, clean_text_fields=True):
    """
    Convierte DataFrame a lista de diccionarios JSON-safe.
    """
    if df is None or df.empty:
        return []

    records = []

    for row in df.to_dict(orient="records"):
        clean_row = {}

        for key, value in row.items():
            key_str = str(key)

            if clean_text_fields and key_str in [
                "Cuenta detectada",
                "Categoría",
                "Fuente utilizada",
                "Hoja",
                "Partida FP&A",
                "Fuente esperada",
            ]:
                clean_row[key_str] = clean_text(value)
            else:
                clean_row[key_str] = clean_value(value)

        records.append(clean_row)

    return records


def calculate_score_from_statuses(df):
    """
    Calcula score ponderado:
    Verde = 100
    Amarillo = 50
    Rojo / Sin datos = 0
    """
    if df is None or df.empty:
        return 0.0

    calculated_df = df[df["Fuente cálculo"] != "No calculado"].copy()

    if calculated_df.empty:
        return 0.0

    calculated_df["Puntaje"] = calculated_df["Estado"].map(STATUS_POINTS).fillna(0)

    return round(float(calculated_df["Puntaje"].sum() / len(calculated_df)), 1)


def score_label(score):
    if score >= 75:
        return "Salud financiera sólida"
    if score >= 50:
        return "Salud financiera moderada"
    if score >= 30:
        return "Salud financiera bajo observación"
    return "Salud financiera crítica"


def dimension_label(score, calculated_count):
    if calculated_count == 0:
        return "Sin datos"
    if score >= 75:
        return "Sólida"
    if score >= 50:
        return "Moderada"
    if score >= 30:
        return "Bajo observación"
    return "Crítica"


def build_kpi_summary(kpis_df, kpis_summary=None):
    if kpis_df is None or kpis_df.empty:
        return {
            "total": 0,
            "calculados": 0,
            "pendientes": 0,
            "cobertura": 0,
            "verdes": 0,
            "amarillos": 0,
            "rojos": 0,
            "sin_datos": 0,
            "sin_umbral": 0,
        }

    total = int(len(kpis_df))
    calculated = int((kpis_df["Fuente cálculo"] != "No calculado").sum())
    pending = total - calculated

    return {
        "total": total,
        "calculados": calculated,
        "pendientes": pending,
        "cobertura": clean_value(kpis_summary.get("coverage", 0)) if kpis_summary else round((calculated / total) * 100, 1),
        "verdes": int((kpis_df["Estado"] == "Verde").sum()),
        "amarillos": int((kpis_df["Estado"] == "Amarillo").sum()),
        "rojos": int((kpis_df["Estado"] == "Rojo").sum()),
        "sin_datos": int((kpis_df["Estado"] == "Sin datos").sum()),
        "sin_umbral": int((kpis_df["Estado"] == "Sin umbral").sum()),
    }


def build_dimensions_snapshot(kpis_df):
    if kpis_df is None or kpis_df.empty or "Dimensión FPA" not in kpis_df.columns:
        return []

    dimensions = []

    for dimension in DIMENSION_ORDER:
        dimension_df = kpis_df[kpis_df["Dimensión FPA"] == dimension].copy()

        if dimension_df.empty:
            continue

        calculated_df = dimension_df[dimension_df["Fuente cálculo"] != "No calculado"].copy()

        total = int(len(dimension_df))
        calculated = int(len(calculated_df))
        pending = total - calculated
        score = calculate_score_from_statuses(dimension_df)

        kpis = []

        for _, row in dimension_df.iterrows():
            kpis.append({
                "codigo_srs": clean_value(row.get("Código SRS")),
                "codigo_kpi": clean_value(row.get("Código KPI")),
                "nombre": clean_text(row.get("KPI")),
                "formula": clean_text(row.get("Fórmula")),
                "valor": clean_value(row.get("Valor")),
                "valor_formateado": clean_value(row.get("Valor formateado")),
                "unidad": clean_value(row.get("Unidad")),
                "fuente_calculo": clean_value(row.get("Fuente cálculo")),
                "estado_calculo": clean_value(row.get("Estado cálculo")),
                "estado": clean_value(row.get("Estado")),
                "lectura": clean_text(row.get("Lectura"), max_length=220),
                "nota_calculo": clean_text(row.get("Nota cálculo"), max_length=260),
                "partidas_requeridas": clean_text(row.get("Partidas requeridas"), max_length=240),
                "partidas_faltantes": clean_text(row.get("Partidas faltantes"), max_length=240),
                "trazabilidad": {
                    "numerador_usado": clean_text(row.get("Numerador usado")),
                    "fuente_numerador": clean_text(row.get("Fuente numerador")),
                    "hoja_numerador": clean_text(row.get("Hoja numerador")),
                    "cuenta_numerador": clean_text(row.get("Cuenta numerador")),
                    "denominador_usado": clean_text(row.get("Denominador usado")),
                    "fuente_denominador": clean_text(row.get("Fuente denominador")),
                    "hoja_denominador": clean_text(row.get("Hoja denominador")),
                    "cuenta_denominador": clean_text(row.get("Cuenta denominador")),
                }
            })

        dimensions.append({
            "dimension": dimension,
            "score": score,
            "estado_dimension": dimension_label(score, calculated),
            "total_kpis": total,
            "kpis_calculados": calculated,
            "kpis_pendientes": pending,
            "verdes": int((dimension_df["Estado"] == "Verde").sum()),
            "amarillos": int((dimension_df["Estado"] == "Amarillo").sum()),
            "rojos": int((dimension_df["Estado"] == "Rojo").sum()),
            "sin_datos": int((dimension_df["Estado"] == "Sin datos").sum()),
            "kpis": kpis,
        })

    return dimensions


def build_alerts(kpis_df):
    """
    Genera alertas simples y trazables a partir de KPIs rojos o no calculados.
    La IA usará estas alertas como base, sin inventar datos.
    """
    if kpis_df is None or kpis_df.empty:
        return []

    alerts = []

    red_df = kpis_df[kpis_df["Estado"] == "Rojo"].copy()

    for _, row in red_df.iterrows():
        alerts.append({
            "tipo": "KPI crítico",
            "severidad": "Alta",
            "dimension": clean_value(row.get("Dimensión FPA")),
            "codigo_srs": clean_value(row.get("Código SRS")),
            "kpi": clean_text(row.get("KPI")),
            "valor": clean_value(row.get("Valor formateado")),
            "mensaje": clean_text(row.get("Lectura"), max_length=220),
        })

    pending_df = kpis_df[kpis_df["Fuente cálculo"] == "No calculado"].copy()

    for _, row in pending_df.iterrows():
        alerts.append({
            "tipo": "KPI sin datos",
            "severidad": "Media",
            "dimension": clean_value(row.get("Dimensión FPA")),
            "codigo_srs": clean_value(row.get("Código SRS")),
            "kpi": clean_text(row.get("KPI")),
            "valor": None,
            "mensaje": clean_text(row.get("Nota cálculo"), max_length=260),
        })

    return alerts


def build_financial_items_snapshot(financial_items_df, financial_items_summary=None):
    if financial_items_df is None or financial_items_df.empty:
        return {
            "resumen": {
                "total": 0,
                "detectadas_con_valor": 0,
                "detectadas_sin_valor": 0,
                "pendientes": 0,
                "cobertura": 0,
            },
            "detectadas_con_valor": [],
            "detectadas_sin_valor": [],
            "pendientes": [],
        }

    detected_df = financial_items_df[financial_items_df["Estado"] == "Detectada"].copy()

    detected_with_value_df = detected_df[
        pd.to_numeric(detected_df["Valor detectado"], errors="coerce").notna()
    ].copy()

    detected_without_value_df = detected_df[
        pd.to_numeric(detected_df["Valor detectado"], errors="coerce").isna()
    ].copy()

    missing_df = financial_items_df[financial_items_df["Estado"] != "Detectada"].copy()

    return {
        "resumen": {
            "total": int(len(financial_items_df)),
            "detectadas": int(len(detected_df)),
            "detectadas_con_valor": int(len(detected_with_value_df)),
            "detectadas_sin_valor": int(len(detected_without_value_df)),
            "pendientes": int(len(missing_df)),
            "cobertura": clean_value(financial_items_summary.get("coverage", 0)) if financial_items_summary else round((len(detected_df) / len(financial_items_df)) * 100, 1),
        },
        "detectadas_con_valor": df_to_records(detected_with_value_df),
        "detectadas_sin_valor": df_to_records(detected_without_value_df),
        "pendientes": df_to_records(missing_df),
    }


def build_data_quality_warnings(financial_items_df, kpis_df):
    warnings = []

    if financial_items_df is not None and not financial_items_df.empty:
        detected_df = financial_items_df[financial_items_df["Estado"] == "Detectada"].copy()
        without_value_df = detected_df[
            pd.to_numeric(detected_df["Valor detectado"], errors="coerce").isna()
        ].copy()

        for _, row in without_value_df.iterrows():
            warnings.append({
                "tipo": "Partida detectada sin valor numérico",
                "severidad": "Media",
                "codigo_interno": clean_value(row.get("Código interno")),
                "partida": clean_text(row.get("Partida FP&A")),
                "hoja": clean_text(row.get("Hoja")),
                "cuenta_detectada": clean_text(row.get("Cuenta detectada")),
                "mensaje": "La partida fue detectada por texto, pero no tiene valor numérico utilizable para cálculos.",
            })

    if kpis_df is not None and not kpis_df.empty:
        ccc = kpis_df[kpis_df["Código KPI"] == "cash_conversion_cycle"]
        if not ccc.empty:
            warnings.append({
                "tipo": "Validación metodológica",
                "severidad": "Baja",
                "codigo_kpi": "cash_conversion_cycle",
                "kpi": "Ciclo de caja",
                "mensaje": "El ciclo de caja calculado puede diferir del ratio informado si el archivo usa promedios, períodos mensuales u otra metodología.",
            })

    return warnings


def build_methodological_notes(kpis_df):
    notes = [
        "Los KPIs son calculados por el motor determinístico de AFINA a partir de partidas FP&A detectadas.",
        "La IA debe interpretar los resultados, no recalcular indicadores financieros principales.",
        "Los indicadores sin datos no deben ser inventados; deben informarse como pendientes de validación.",
        "Los semáforos actuales usan umbrales generales. En una versión posterior se aplicarán thresholds por industria.",
    ]

    if kpis_df is not None and not kpis_df.empty:
        roi_rows = kpis_df[kpis_df["Código KPI"] == "roi"]
        if not roi_rows.empty and roi_rows.iloc[0].get("Fuente cálculo") == "No calculado":
            notes.append("ROI no se calcula si no existe una partida confiable de inversión total o capital invertido.")

        ccc_rows = kpis_df[kpis_df["Código KPI"] == "cash_conversion_cycle"]
        if not ccc_rows.empty:
            notes.append("El ciclo de caja puede diferir de ratios informados si se calcula desde saldos contables en lugar de promedios del período.")

    return notes


def build_financial_snapshot(
    company_name,
    source_file,
    industry,
    period,
    analysis_type,
    kpis_df,
    kpis_summary,
    financial_items_df,
    financial_items_summary,
):
    company_name = infer_company_name(company_name, source_file)
    score = calculate_score_from_statuses(kpis_df)
    kpi_summary = build_kpi_summary(kpis_df, kpis_summary)

    snapshot = {
        "metadata": {
            "snapshot_version": "AFINA_JSON_v0.3.3",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "project": "AFINA - Analista Financiero Inteligente",
            "source": "MVP Streamlit",
        },
        "analysis_context": {
            "company_name": company_name or "No identificado",
            "source_file": source_file or "No disponible",
            "industry": industry or "No especificada",
            "period": period or "No especificado",
            "analysis_type": analysis_type or "No especificado",
        },
        "health_score": {
            "score": score,
            "label": score_label(score),
        },
        "kpi_summary": kpi_summary,
        "dimensions_fpa": build_dimensions_snapshot(kpis_df),
        "alerts": build_alerts(kpis_df),
        "financial_items": build_financial_items_snapshot(financial_items_df, financial_items_summary),
        "data_quality_warnings": build_data_quality_warnings(financial_items_df, kpis_df),
        "methodological_notes": build_methodological_notes(kpis_df),
        "disclaimer": "Este snapshot se basa en datos suministrados por el usuario y reglas automatizadas. Se recomienda validación interna y asesoría profesional para decisiones críticas.",
    }

    return snapshot


def snapshot_to_json(snapshot):
    return json.dumps(snapshot, ensure_ascii=False, indent=2, default=str)
