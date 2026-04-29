import pandas as pd


# =========================
# Utilidades base
# =========================
def safe_float(value):
    """
    Convierte un valor a float de forma segura.
    """
    try:
        if pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


def safe_divide(numerator, denominator):
    """
    División segura para evitar errores por nulos o cero.
    """
    numerator = safe_float(numerator)
    denominator = safe_float(denominator)

    if numerator is None or denominator is None:
        return None

    if denominator == 0:
        return None

    return numerator / denominator


def get_item_row(financial_items_df, internal_code):
    """
    Busca una partida FP&A por su código interno.
    """
    if financial_items_df is None or financial_items_df.empty:
        return None

    if "Código interno" not in financial_items_df.columns:
        return None

    match = financial_items_df[
        financial_items_df["Código interno"] == internal_code
    ]

    if match.empty:
        return None

    return match.iloc[0]


def get_item_value(financial_items_df, internal_code):
    """
    Obtiene el valor detectado de una partida.
    """
    row = get_item_row(financial_items_df, internal_code)

    if row is None:
        return None

    if row.get("Estado") != "Detectada":
        return None

    return safe_float(row.get("Valor detectado"))


def get_item_trace(financial_items_df, internal_code):
    """
    Devuelve trazabilidad de la partida usada.
    """
    row = get_item_row(financial_items_df, internal_code)

    if row is None:
        return {
            "partida": internal_code,
            "estado": "No encontrada",
            "fuente": "",
            "hoja": "",
            "cuenta_detectada": "",
            "valor": None,
            "confianza": 0
        }

    return {
        "partida": row.get("Partida FP&A", internal_code),
        "estado": row.get("Estado", ""),
        "fuente": row.get("Fuente utilizada", ""),
        "hoja": row.get("Hoja", ""),
        "cuenta_detectada": row.get("Cuenta detectada", ""),
        "valor": row.get("Valor detectado", None),
        "confianza": row.get("Confianza", 0)
    }


# =========================
# Umbrales iniciales
# =========================
def evaluate_kpi_status(kpi_code, value, industry="Sector Químico"):
    """
    Evalúa semáforo inicial para cada KPI.
    Estos umbrales son una primera aproximación FP&A.
    Luego se pueden parametrizar por industria en un archivo thresholds.py.
    """
    if value is None:
        return {
            "estado": "Sin datos",
            "color": "gray",
            "lectura": "No se pudo calcular el indicador con las partidas disponibles."
        }

    # Liquidez corriente
    if kpi_code == "current_ratio":
        if value >= 1.5:
            return {
                "estado": "Verde",
                "color": "green",
                "lectura": "La empresa muestra una posición de liquidez saludable."
            }
        elif value >= 1.0:
            return {
                "estado": "Amarillo",
                "color": "yellow",
                "lectura": "La liquidez es aceptable, pero requiere seguimiento."
            }
        else:
            return {
                "estado": "Rojo",
                "color": "red",
                "lectura": "La liquidez corriente es baja y puede comprometer pagos de corto plazo."
            }

    # Endeudamiento
    if kpi_code == "debt_ratio":
        if value <= 0.45:
            return {
                "estado": "Verde",
                "color": "green",
                "lectura": "El nivel de endeudamiento se mantiene controlado."
            }
        elif value <= 0.65:
            return {
                "estado": "Amarillo",
                "color": "yellow",
                "lectura": "El endeudamiento es moderado y debe monitorearse."
            }
        else:
            return {
                "estado": "Rojo",
                "color": "red",
                "lectura": "El endeudamiento es elevado respecto del activo total."
            }

    # ROE
    if kpi_code == "roe":
        if value >= 0.15:
            return {
                "estado": "Verde",
                "color": "green",
                "lectura": "La rentabilidad sobre patrimonio es sólida."
            }
        elif value >= 0.07:
            return {
                "estado": "Amarillo",
                "color": "yellow",
                "lectura": "La rentabilidad patrimonial es moderada."
            }
        else:
            return {
                "estado": "Rojo",
                "color": "red",
                "lectura": "La rentabilidad sobre patrimonio es baja."
            }

    # ROA
    if kpi_code == "roa":
        if value >= 0.08:
            return {
                "estado": "Verde",
                "color": "green",
                "lectura": "La rentabilidad sobre activos es saludable."
            }
        elif value >= 0.03:
            return {
                "estado": "Amarillo",
                "color": "yellow",
                "lectura": "La rentabilidad sobre activos es moderada."
            }
        else:
            return {
                "estado": "Rojo",
                "color": "red",
                "lectura": "La rentabilidad sobre activos es baja."
            }

    # Márgenes
    if kpi_code in ["gross_margin", "operating_margin"]:
        if value >= 0.25:
            return {
                "estado": "Verde",
                "color": "green",
                "lectura": "El margen muestra una posición favorable."
            }
        elif value >= 0.10:
            return {
                "estado": "Amarillo",
                "color": "yellow",
                "lectura": "El margen es positivo, pero requiere seguimiento."
            }
        else:
            return {
                "estado": "Rojo",
                "color": "red",
                "lectura": "El margen es bajo y puede indicar presión sobre costos o eficiencia."
            }

    # Rotación de activos
    if kpi_code == "asset_turnover":
        if value >= 1.0:
            return {
                "estado": "Verde",
                "color": "green",
                "lectura": "La empresa genera ventas relevantes en relación con sus activos."
            }
        elif value >= 0.5:
            return {
                "estado": "Amarillo",
                "color": "yellow",
                "lectura": "La rotación de activos es moderada."
            }
        else:
            return {
                "estado": "Rojo",
                "color": "red",
                "lectura": "La rotación de activos es baja."
            }

    # Ciclo de caja
    if kpi_code == "cash_conversion_cycle":
        if value <= 60:
            return {
                "estado": "Verde",
                "color": "green",
                "lectura": "El ciclo de caja es razonable para una operación comercial/industrial."
            }
        elif value <= 120:
            return {
                "estado": "Amarillo",
                "color": "yellow",
                "lectura": "El ciclo de caja es moderado y puede presionar el capital de trabajo."
            }
        else:
            return {
                "estado": "Rojo",
                "color": "red",
                "lectura": "El ciclo de caja es elevado y puede tensionar la liquidez."
            }

    return {
        "estado": "Sin umbral",
        "color": "blue",
        "lectura": "Indicador calculado sin umbral específico configurado."
    }


def format_kpi_value(kpi_code, value):
    """
    Formatea el valor del KPI para mostrarlo en dashboard.
    """
    if value is None:
        return "Sin datos"

    if kpi_code in [
        "roe",
        "roa",
        "gross_margin",
        "operating_margin",
        "debt_ratio"
    ]:
        return f"{value * 100:.2f}%"

    if kpi_code in [
        "current_ratio",
        "asset_turnover"
    ]:
        return f"{value:.2f}x"

    if kpi_code == "cash_conversion_cycle":
        return f"{value:.0f} días"

    return f"{value:.2f}"


# =========================
# Motor principal de KPIs
# =========================
def calculate_kpis(financial_items_df, industry="Sector Químico"):
    """
    Calcula KPIs financieros reales a partir de las partidas FP&A detectadas.
    Devuelve:
    - kpis_df: tabla de KPIs calculados
    - summary: resumen ejecutivo de cálculo
    """

    values = {
        "current_assets": get_item_value(financial_items_df, "current_assets"),
        "current_liabilities": get_item_value(financial_items_df, "current_liabilities"),
        "total_assets": get_item_value(financial_items_df, "total_assets"),
        "total_liabilities": get_item_value(financial_items_df, "total_liabilities"),
        "equity": get_item_value(financial_items_df, "equity"),
        "sales": get_item_value(financial_items_df, "sales"),
        "gross_profit": get_item_value(financial_items_df, "gross_profit"),
        "operating_result": get_item_value(financial_items_df, "operating_result"),
        "net_income": get_item_value(financial_items_df, "net_income"),
        "current_ratio_direct": get_item_value(financial_items_df, "current_ratio"),
        "roe_direct": get_item_value(financial_items_df, "roe"),
        "roa_direct": get_item_value(financial_items_df, "roa"),
        "debt_ratio_direct": get_item_value(financial_items_df, "debt_ratio"),
        "cash_conversion_cycle_direct": get_item_value(financial_items_df, "cash_conversion_cycle"),
    }

    kpi_definitions = [
        {
            "code": "current_ratio",
            "name": "Liquidez corriente",
            "formula": "Activo corriente / Pasivo corriente",
            "value": safe_divide(values["current_assets"], values["current_liabilities"]),
            "fallback": values["current_ratio_direct"],
            "numerator_code": "current_assets",
            "denominator_code": "current_liabilities"
        },
        {
            "code": "debt_ratio",
            "name": "Endeudamiento",
            "formula": "Pasivo total / Activo total",
            "value": safe_divide(values["total_liabilities"], values["total_assets"]),
            "fallback": values["debt_ratio_direct"],
            "numerator_code": "total_liabilities",
            "denominator_code": "total_assets"
        },
        {
            "code": "roe",
            "name": "ROE",
            "formula": "Utilidad neta / Patrimonio",
            "value": safe_divide(values["net_income"], values["equity"]),
            "fallback": values["roe_direct"],
            "numerator_code": "net_income",
            "denominator_code": "equity"
        },
        {
            "code": "roa",
            "name": "ROA",
            "formula": "Utilidad neta / Activo total",
            "value": safe_divide(values["net_income"], values["total_assets"]),
            "fallback": values["roa_direct"],
            "numerator_code": "net_income",
            "denominator_code": "total_assets"
        },
        {
            "code": "gross_margin",
            "name": "Margen bruto",
            "formula": "Utilidad bruta / Ventas",
            "value": safe_divide(values["gross_profit"], values["sales"]),
            "fallback": None,
            "numerator_code": "gross_profit",
            "denominator_code": "sales"
        },
        {
            "code": "operating_margin",
            "name": "Margen operativo",
            "formula": "Resultado operativo / Ventas",
            "value": safe_divide(values["operating_result"], values["sales"]),
            "fallback": None,
            "numerator_code": "operating_result",
            "denominator_code": "sales"
        },
        {
            "code": "asset_turnover",
            "name": "Rotación de activos",
            "formula": "Ventas / Activo total",
            "value": safe_divide(values["sales"], values["total_assets"]),
            "fallback": None,
            "numerator_code": "sales",
            "denominator_code": "total_assets"
        },
        {
            "code": "cash_conversion_cycle",
            "name": "Ciclo de caja",
            "formula": "Dato directo detectado desde ratios financieros",
            "value": values["cash_conversion_cycle_direct"],
            "fallback": None,
            "numerator_code": "cash_conversion_cycle",
            "denominator_code": None
        }
    ]

    rows = []

    for item in kpi_definitions:
        value = item["value"]
        source_type = "Calculado"

        if value is None and item["fallback"] is not None:
            value = item["fallback"]
            source_type = "Detectado directo"

        evaluation = evaluate_kpi_status(
            item["code"],
            value,
            industry=industry
        )

        numerator_trace = (
            get_item_trace(financial_items_df, item["numerator_code"])
            if item["numerator_code"]
            else {}
        )

        denominator_trace = (
            get_item_trace(financial_items_df, item["denominator_code"])
            if item["denominator_code"]
            else {}
        )

        rows.append({
            "Código KPI": item["code"],
            "KPI": item["name"],
            "Valor": value,
            "Valor formateado": format_kpi_value(item["code"], value),
            "Fórmula": item["formula"],
            "Fuente cálculo": source_type if value is not None else "No calculado",
            "Estado": evaluation["estado"],
            "Color": evaluation["color"],
            "Lectura": evaluation["lectura"],
            "Numerador usado": numerator_trace.get("partida", ""),
            "Valor numerador": numerator_trace.get("valor", None),
            "Fuente numerador": numerator_trace.get("fuente", ""),
            "Hoja numerador": numerator_trace.get("hoja", ""),
            "Cuenta numerador": numerator_trace.get("cuenta_detectada", ""),
            "Denominador usado": denominator_trace.get("partida", ""),
            "Valor denominador": denominator_trace.get("valor", None),
            "Fuente denominador": denominator_trace.get("fuente", ""),
            "Hoja denominador": denominator_trace.get("hoja", ""),
            "Cuenta denominador": denominator_trace.get("cuenta_detectada", "")
        })

    kpis_df = pd.DataFrame(rows)

    calculated_count = int((kpis_df["Fuente cálculo"] != "No calculado").sum())
    total_count = len(kpis_df)

    coverage = round((calculated_count / total_count) * 100, 1) if total_count else 0

    if coverage >= 80:
        status = "Alta"
        detail = "AFINA calculó la mayoría de los KPIs financieros principales."
    elif coverage >= 50:
        status = "Media"
        detail = "AFINA calculó varios KPIs, aunque algunos requieren revisión de partidas."
    else:
        status = "Baja"
        detail = "AFINA no pudo calcular suficientes KPIs con las partidas actuales."

    summary = {
        "total_kpis": total_count,
        "calculated_kpis": calculated_count,
        "missing_kpis": total_count - calculated_count,
        "coverage": coverage,
        "status": status,
        "detail": detail
    }

    return kpis_df, summary
