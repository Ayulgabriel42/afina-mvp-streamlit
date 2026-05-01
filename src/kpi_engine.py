import pandas as pd

from src.kpi_catalog import KPI_CATALOG


# =========================
# Utilidades base
# =========================
def safe_float(value):
    try:
        if pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


def safe_divide(numerator, denominator):
    numerator = safe_float(numerator)
    denominator = safe_float(denominator)

    if numerator is None or denominator is None:
        return None

    if denominator == 0:
        return None

    return numerator / denominator


def safe_abs(value):
    value = safe_float(value)
    if value is None:
        return None
    return abs(value)


def safe_divide_abs_denominator(numerator, denominator):
    denominator = safe_abs(denominator)
    return safe_divide(numerator, denominator)


def get_item_row(financial_items_df, internal_code):
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
    row = get_item_row(financial_items_df, internal_code)

    if row is None:
        return None

    if row.get("Estado") != "Detectada":
        return None

    return safe_float(row.get("Valor detectado"))


def get_item_trace(financial_items_df, internal_code):
    row = get_item_row(financial_items_df, internal_code)

    if row is None:
        return {
            "partida": internal_code,
            "estado": "No encontrada",
            "fuente": "",
            "hoja": "",
            "cuenta_detectada": "",
            "valor": None,
            "confianza": 0,
        }

    return {
        "partida": row.get("Partida FP&A", internal_code),
        "estado": row.get("Estado", ""),
        "fuente": row.get("Fuente utilizada", ""),
        "hoja": row.get("Hoja", ""),
        "cuenta_detectada": row.get("Cuenta detectada", ""),
        "valor": row.get("Valor detectado", None),
        "confianza": row.get("Confianza", 0),
    }


def get_item_label(financial_items_df, internal_code):
    trace = get_item_trace(financial_items_df, internal_code)
    return trace.get("partida", internal_code)


def build_group_trace(financial_items_df, item_codes):
    traces = [get_item_trace(financial_items_df, code) for code in item_codes if code]

    labels = [trace.get("partida", "") for trace in traces if trace.get("partida")]
    values = [trace.get("valor", None) for trace in traces]
    sources = [trace.get("fuente", "") for trace in traces if trace.get("fuente")]
    sheets = [trace.get("hoja", "") for trace in traces if trace.get("hoja")]
    accounts = [trace.get("cuenta_detectada", "") for trace in traces if trace.get("cuenta_detectada")]

    return {
        "labels": " + ".join(labels),
        "values": values,
        "sources": " | ".join(dict.fromkeys(sources)),
        "sheets": " | ".join(dict.fromkeys(sheets)),
        "accounts": " | ".join(dict.fromkeys(accounts)),
    }


def detect_missing_items(financial_items_df, required_items):
    missing = []

    for item_code in required_items:
        value = get_item_value(financial_items_df, item_code)
        if value is None:
            missing.append(item_code)

    return missing


# =========================
# Umbrales generales iniciales
# Luego esto debería migrar a thresholds.py por industria
# =========================
def evaluate_kpi_status(kpi_code, value, industry="Sector Químico"):
    if value is None:
        return {
            "estado": "Sin datos",
            "color": "gray",
            "lectura": "No se pudo calcular el indicador con las partidas disponibles.",
        }

    # Estructura de inversión
    if kpi_code == "debt_ratio":
        if value <= 0.50:
            return {"estado": "Verde", "color": "green", "lectura": "El endeudamiento sobre activos se mantiene en un rango saludable."}
        if value <= 0.65:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "El endeudamiento es moderado y requiere seguimiento."}
        return {"estado": "Rojo", "color": "red", "lectura": "El endeudamiento sobre activos es elevado."}

    if kpi_code in ["debt_to_equity", "debt_index"]:
        if value <= 1.50:
            return {"estado": "Verde", "color": "green", "lectura": "La relación deuda/patrimonio se mantiene controlada."}
        if value <= 2.50:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "La relación deuda/patrimonio es moderada."}
        return {"estado": "Rojo", "color": "red", "lectura": "La relación deuda/patrimonio es elevada."}

    if kpi_code == "equity_multiplier":
        if value <= 3.50:
            return {"estado": "Verde", "color": "green", "lectura": "El apalancamiento financiero se encuentra dentro de un rango razonable."}
        if value <= 4.50:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "El apalancamiento financiero requiere seguimiento."}
        return {"estado": "Rojo", "color": "red", "lectura": "El apalancamiento financiero es elevado."}

    # Capital de trabajo
    if kpi_code == "inventory_days":
        if value <= 90:
            return {"estado": "Verde", "color": "green", "lectura": "La permanencia de inventarios es razonable."}
        if value <= 120:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "La permanencia de inventarios es moderada y puede afectar capital de trabajo."}
        return {"estado": "Rojo", "color": "red", "lectura": "La permanencia de inventarios es elevada."}

    if kpi_code == "receivables_days":
        if value <= 65:
            return {"estado": "Verde", "color": "green", "lectura": "El plazo promedio de cobro es saludable."}
        if value <= 90:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "El plazo promedio de cobro requiere seguimiento."}
        return {"estado": "Rojo", "color": "red", "lectura": "El plazo promedio de cobro es elevado."}

    if kpi_code == "payables_days":
        if value >= 65:
            return {"estado": "Verde", "color": "green", "lectura": "El plazo promedio de pago favorece la gestión de caja."}
        if value >= 45:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "El plazo promedio de pago es aceptable, pero podría optimizarse."}
        return {"estado": "Rojo", "color": "red", "lectura": "El plazo promedio de pago es bajo y puede presionar la caja."}

    if kpi_code == "cash_conversion_cycle":
        if value <= 90:
            return {"estado": "Verde", "color": "green", "lectura": "El ciclo de caja es razonable para la operación."}
        if value <= 120:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "El ciclo de caja es moderado y puede presionar el capital de trabajo."}
        return {"estado": "Rojo", "color": "red", "lectura": "El ciclo de caja es elevado y puede tensionar la liquidez."}

    # Rentabilidad
    if kpi_code == "operating_margin":
        if value >= 0.12:
            return {"estado": "Verde", "color": "green", "lectura": "El margen operativo muestra una rentabilidad operativa saludable."}
        if value >= 0.05:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "El margen operativo es positivo, pero requiere mejora."}
        return {"estado": "Rojo", "color": "red", "lectura": "El margen operativo es bajo o insuficiente."}

    if kpi_code == "asset_turnover":
        if value >= 1.25:
            return {"estado": "Verde", "color": "green", "lectura": "La empresa genera ventas relevantes en relación con sus activos."}
        if value >= 0.75:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "La rotación de activos es moderada."}
        return {"estado": "Rojo", "color": "red", "lectura": "La rotación de activos es baja."}

    if kpi_code == "roi":
        if value >= 0.113:
            return {"estado": "Verde", "color": "green", "lectura": "El retorno sobre la inversión supera el umbral objetivo."}
        if value >= 0.05:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "El retorno sobre la inversión es moderado."}
        return {"estado": "Rojo", "color": "red", "lectura": "El retorno sobre la inversión es bajo."}

    if kpi_code == "roa":
        if value >= 0.075:
            return {"estado": "Verde", "color": "green", "lectura": "La rentabilidad sobre activos es saludable."}
        if value >= 0.03:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "La rentabilidad sobre activos es moderada."}
        return {"estado": "Rojo", "color": "red", "lectura": "La rentabilidad sobre activos es baja."}

    if kpi_code == "roe":
        if value >= 0.27:
            return {"estado": "Verde", "color": "green", "lectura": "La rentabilidad sobre patrimonio supera el umbral objetivo."}
        if value >= 0.10:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "La rentabilidad patrimonial es moderada."}
        return {"estado": "Rojo", "color": "red", "lectura": "La rentabilidad patrimonial es baja."}

    # Fluidez financiera
    if kpi_code == "current_ratio":
        if value >= 1.50:
            return {"estado": "Verde", "color": "green", "lectura": "La liquidez corriente muestra capacidad de cubrir obligaciones de corto plazo."}
        if value >= 1.00:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "La liquidez corriente es aceptable, pero requiere seguimiento."}
        return {"estado": "Rojo", "color": "red", "lectura": "La liquidez corriente es baja."}

    if kpi_code == "quick_ratio":
        if value >= 1.00:
            return {"estado": "Verde", "color": "green", "lectura": "La prueba ácida indica buena liquidez sin depender de inventarios."}
        if value >= 0.70:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "La prueba ácida es moderada."}
        return {"estado": "Rojo", "color": "red", "lectura": "La prueba ácida es baja."}

    if kpi_code == "cash_ratio":
        if value >= 0.20:
            return {"estado": "Verde", "color": "green", "lectura": "La cobertura inmediata con efectivo es adecuada."}
        if value >= 0.10:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "La cobertura inmediata con efectivo es limitada."}
        return {"estado": "Rojo", "color": "red", "lectura": "La cobertura inmediata con efectivo es baja."}

    if kpi_code == "ocf_to_current_liabilities":
        if value >= 0.40:
            return {"estado": "Verde", "color": "green", "lectura": "El flujo operativo cubre una proporción saludable del pasivo corriente."}
        if value >= 0.15:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "La cobertura del pasivo corriente con flujo operativo es moderada."}
        return {"estado": "Rojo", "color": "red", "lectura": "La cobertura del pasivo corriente con flujo operativo es baja."}

    # Equilibrio financiero
    if kpi_code == "interest_coverage":
        if value >= 4.50:
            return {"estado": "Verde", "color": "green", "lectura": "La empresa cubre cómodamente sus gastos financieros con resultado operativo."}
        if value >= 2.00:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "La cobertura de gastos financieros es moderada."}
        return {"estado": "Rojo", "color": "red", "lectura": "La cobertura de gastos financieros es baja."}

    if kpi_code == "debt_to_ebitda":
        if value <= 3.00:
            return {"estado": "Verde", "color": "green", "lectura": "La deuda en relación con EBITDA se encuentra en rango razonable."}
        if value <= 4.00:
            return {"estado": "Amarillo", "color": "yellow", "lectura": "La deuda sobre EBITDA requiere seguimiento."}
        return {"estado": "Rojo", "color": "red", "lectura": "La deuda sobre EBITDA es elevada."}

    return {
        "estado": "Sin umbral",
        "color": "blue",
        "lectura": "Indicador calculado sin umbral específico configurado.",
    }


def format_kpi_value(kpi_code, value, unit="ratio"):
    if value is None:
        return "Sin datos"

    if unit == "percentage":
        return f"{value * 100:.2f}%"

    if unit == "ratio":
        return f"{value:.2f}x"

    if unit == "days":
        return f"{value:.0f} días"

    return f"{value:.2f}"


# =========================
# Cálculo de KPIs
# =========================
def calculate_single_kpi(kpi_code, values):
    source_type = "Calculado"
    calculation_note = ""

    if kpi_code == "debt_ratio":
        value = safe_divide(values["total_liabilities"], values["total_assets"])
        if value is None and values.get("debt_ratio_direct") is not None:
            value = values.get("debt_ratio_direct")
            source_type = "Detectado directo"
        return value, source_type, calculation_note, ["total_liabilities"], ["total_assets"]

    if kpi_code == "debt_to_equity":
        return safe_divide(values["total_liabilities"], values["equity"]), source_type, calculation_note, ["total_liabilities"], ["equity"]

    if kpi_code == "equity_multiplier":
        return safe_divide(values["total_assets"], values["equity"]), source_type, calculation_note, ["total_assets"], ["equity"]

    if kpi_code == "inventory_days":
        value = safe_divide_abs_denominator(
            safe_float(values["inventory"]) * 360 if values["inventory"] is not None else None,
            values["cost_of_sales"]
        )
        return value, source_type, calculation_note, ["inventory"], ["cost_of_sales"]

    if kpi_code == "receivables_days":
        value = safe_divide(
            safe_float(values["accounts_receivable"]) * 360 if values["accounts_receivable"] is not None else None,
            values["sales"]
        )
        return value, source_type, calculation_note, ["accounts_receivable"], ["sales"]

    if kpi_code == "payables_days":
        value = safe_divide_abs_denominator(
            safe_float(values["accounts_payable"]) * 360 if values["accounts_payable"] is not None else None,
            values["cost_of_sales"]
        )
        return value, source_type, calculation_note, ["accounts_payable"], ["cost_of_sales"]

    if kpi_code == "cash_conversion_cycle":
        pmri, _, _, _, _ = calculate_single_kpi("inventory_days", values)
        pmcc, _, _, _, _ = calculate_single_kpi("receivables_days", values)
        pmpp, _, _, _, _ = calculate_single_kpi("payables_days", values)

        if pmri is not None and pmcc is not None and pmpp is not None:
            return pmri + pmcc - pmpp, source_type, calculation_note, ["inventory", "accounts_receivable", "accounts_payable"], ["cost_of_sales", "sales"]

        if values.get("cash_conversion_cycle_direct") is not None:
            return values.get("cash_conversion_cycle_direct"), "Detectado directo", "No se pudo recalcular el ciclo completo; se usa el valor detectado en ratios.", ["cash_conversion_cycle"], []

        return None, "No calculado", "Faltan partidas para PMRI, PMCC o PMPP.", ["inventory", "accounts_receivable", "accounts_payable"], ["cost_of_sales", "sales"]

    if kpi_code == "operating_margin":
        return safe_divide(values["operating_result"], values["sales"]), source_type, calculation_note, ["operating_result"], ["sales"]

    if kpi_code == "asset_turnover":
        return safe_divide(values["sales"], values["total_assets"]), source_type, calculation_note, ["sales"], ["total_assets"]

    if kpi_code == "roi":
        value = safe_divide(values["net_income"], values["investment_total"])
        if value is None:
            return None, "No calculado", "No se detectó inversión total. Se evita usar ROA como sustituto para no duplicar indicadores.", ["net_income"], ["investment_total"]
        return value, source_type, calculation_note, ["net_income"], ["investment_total"]

    if kpi_code == "roa":
        value = safe_divide(values["net_income"], values["total_assets"])
        if value is None and values.get("roa_direct") is not None:
            value = values.get("roa_direct")
            source_type = "Detectado directo"
        return value, source_type, calculation_note, ["net_income"], ["total_assets"]

    if kpi_code == "roe":
        value = safe_divide(values["net_income"], values["equity"])
        if value is None and values.get("roe_direct") is not None:
            value = values.get("roe_direct")
            source_type = "Detectado directo"
        return value, source_type, calculation_note, ["net_income"], ["equity"]

    if kpi_code == "current_ratio":
        value = safe_divide(values["current_assets"], values["current_liabilities"])
        if value is None and values.get("current_ratio_direct") is not None:
            value = values.get("current_ratio_direct")
            source_type = "Detectado directo"
        return value, source_type, calculation_note, ["current_assets"], ["current_liabilities"]

    if kpi_code == "quick_ratio":
        if values["current_assets"] is not None and values["inventory"] is not None:
            numerator = safe_float(values["current_assets"]) - safe_float(values["inventory"])
        else:
            numerator = None

        value = safe_divide(numerator, values["current_liabilities"])

        if value is None and values.get("quick_ratio_direct") is not None:
            value = values.get("quick_ratio_direct")
            source_type = "Detectado directo"

        return value, source_type, calculation_note, ["current_assets", "inventory"], ["current_liabilities"]

    if kpi_code == "cash_ratio":
        return safe_divide(values["cash"], values["current_liabilities"]), source_type, calculation_note, ["cash"], ["current_liabilities"]

    if kpi_code == "ocf_to_current_liabilities":
        return safe_divide(values["operating_cash_flow"], values["current_liabilities"]), source_type, calculation_note, ["operating_cash_flow"], ["current_liabilities"]

    if kpi_code == "debt_index":
        debt_value = values.get("total_debt")
        source_items = ["total_debt"]

        if debt_value is None:
            debt_value = values.get("total_liabilities")
            source_type = "Calculado con aproximación"
            calculation_note = "No se detectó deuda total separada; se utiliza pasivo total como aproximación."
            source_items = ["total_liabilities"]

        return safe_divide(debt_value, values["equity"]), source_type, calculation_note, source_items, ["equity"]

    if kpi_code == "interest_coverage":
        return safe_divide_abs_denominator(values["operating_result"], values["financial_expenses"]), source_type, calculation_note, ["operating_result"], ["financial_expenses"]

    if kpi_code == "debt_to_ebitda":
        debt_value = values.get("total_debt")
        debt_source = ["total_debt"]

        if debt_value is None:
            debt_value = values.get("total_liabilities")
            debt_source = ["total_liabilities"]
            source_type = "Calculado con aproximación"
            calculation_note = "No se detectó deuda total separada; se utiliza pasivo total como aproximación."

        ebitda_value = values.get("ebitda")
        ebitda_source = ["ebitda"]

        if ebitda_value is None:
            ebitda_value = values.get("operating_result")
            ebitda_source = ["operating_result"]
            source_type = "Calculado con aproximación"
            if calculation_note:
                calculation_note += " Además, no se detectó EBITDA; se utiliza resultado operativo como proxy preliminar."
            else:
                calculation_note = "No se detectó EBITDA; se utiliza resultado operativo como proxy preliminar."

        return safe_divide(debt_value, ebitda_value), source_type, calculation_note, debt_source, ebitda_source

    return None, "No calculado", "No existe fórmula implementada para este KPI.", [], []


# =========================
# Motor principal
# =========================
def calculate_kpis(financial_items_df, industry="Sector Químico"):
    values = {
        # Balance
        "cash": get_item_value(financial_items_df, "cash"),
        "accounts_receivable": get_item_value(financial_items_df, "accounts_receivable"),
        "accounts_payable": get_item_value(financial_items_df, "accounts_payable"),
        "inventory": get_item_value(financial_items_df, "inventory"),
        "current_assets": get_item_value(financial_items_df, "current_assets"),
        "total_assets": get_item_value(financial_items_df, "total_assets"),
        "current_liabilities": get_item_value(financial_items_df, "current_liabilities"),
        "total_liabilities": get_item_value(financial_items_df, "total_liabilities"),
        "equity": get_item_value(financial_items_df, "equity"),
        "total_debt": get_item_value(financial_items_df, "total_debt"),
        "investment_total": get_item_value(financial_items_df, "investment_total"),

        # Resultados
        "sales": get_item_value(financial_items_df, "sales"),
        "cost_of_sales": get_item_value(financial_items_df, "cost_of_sales"),
        "operating_result": get_item_value(financial_items_df, "operating_result"),
        "financial_expenses": get_item_value(financial_items_df, "financial_expenses"),
        "net_income": get_item_value(financial_items_df, "net_income"),
        "ebitda": get_item_value(financial_items_df, "ebitda"),

        # Flujo de efectivo
        "operating_cash_flow": get_item_value(financial_items_df, "operating_cash_flow"),

        # Ratios directos detectados
        "current_ratio_direct": get_item_value(financial_items_df, "current_ratio"),
        "quick_ratio_direct": get_item_value(financial_items_df, "quick_ratio"),
        "roe_direct": get_item_value(financial_items_df, "roe"),
        "roa_direct": get_item_value(financial_items_df, "roa"),
        "debt_ratio_direct": get_item_value(financial_items_df, "debt_ratio"),
        "cash_conversion_cycle_direct": get_item_value(financial_items_df, "cash_conversion_cycle"),
    }

    rows = []

    for kpi_def in KPI_CATALOG:
        code = kpi_def["code"]

        value, source_type, calculation_note, numerator_items, denominator_items = calculate_single_kpi(code, values)

        if value is None:
            source_type = "No calculado"

        evaluation = evaluate_kpi_status(code, value, industry=industry)

        numerator_trace = build_group_trace(financial_items_df, numerator_items)
        denominator_trace = build_group_trace(financial_items_df, denominator_items)

        required_items = kpi_def.get("required_items", [])
        missing_items = detect_missing_items(financial_items_df, required_items)

        if value is None and not calculation_note:
            if missing_items:
                missing_labels = [
                    get_item_label(financial_items_df, item_code)
                    for item_code in missing_items
                ]
                calculation_note = "Faltan partidas requeridas: " + ", ".join(missing_labels)
            else:
                calculation_note = "No se pudo calcular el indicador con los datos disponibles."

        estado_calculo = "Calculado" if value is not None else "Pendiente"

        rows.append({
            "Código SRS": kpi_def["srs_code"],
            "Código KPI": code,
            "Dimensión FPA": kpi_def["dimension"],
            "Orden": kpi_def["order"],
            "KPI": kpi_def["name"],
            "Valor": value,
            "Valor formateado": format_kpi_value(code, value, unit=kpi_def["unit"]),
            "Unidad": kpi_def["unit"],
            "Fórmula": kpi_def["formula"],
            "Fuente cálculo": source_type,
            "Estado cálculo": estado_calculo,
            "Partidas requeridas": ", ".join(required_items),
            "Partidas faltantes": ", ".join(missing_items),
            "Nota cálculo": calculation_note,
            "Estado": evaluation["estado"],
            "Color": evaluation["color"],
            "Lectura": evaluation["lectura"],

            # Compatibilidad con app.py y kpi_visuals.py actuales
            "Numerador usado": numerator_trace.get("labels", ""),
            "Valor numerador": None,
            "Fuente numerador": numerator_trace.get("sources", ""),
            "Hoja numerador": numerator_trace.get("sheets", ""),
            "Cuenta numerador": numerator_trace.get("accounts", ""),
            "Denominador usado": denominator_trace.get("labels", ""),
            "Valor denominador": None,
            "Fuente denominador": denominator_trace.get("sources", ""),
            "Hoja denominador": denominator_trace.get("sheets", ""),
            "Cuenta denominador": denominator_trace.get("accounts", ""),
        })

    kpis_df = pd.DataFrame(rows)
    kpis_df = kpis_df.sort_values("Orden").reset_index(drop=True)

    calculated_count = int((kpis_df["Fuente cálculo"] != "No calculado").sum())
    total_count = len(kpis_df)
    coverage = round((calculated_count / total_count) * 100, 1) if total_count else 0

    if coverage >= 80:
        status = "Alta"
        detail = "AFINA calculó la mayoría del catálogo FPA de 19 KPIs."
    elif coverage >= 50:
        status = "Media"
        detail = "AFINA calculó una parte relevante del catálogo FPA, pero faltan partidas para completar algunos indicadores."
    else:
        status = "Baja"
        detail = "AFINA todavía necesita mejorar extracción de partidas antes de completar el catálogo FPA."

    missing_detail = kpis_df[kpis_df["Fuente cálculo"] == "No calculado"][
        ["Código SRS", "KPI", "Partidas faltantes", "Nota cálculo"]
    ]

    summary = {
        "total_kpis": total_count,
        "calculated_kpis": calculated_count,
        "missing_kpis": total_count - calculated_count,
        "coverage": coverage,
        "status": status,
        "detail": detail,
        "missing_detail": missing_detail,
    }

    return kpis_df, summary
