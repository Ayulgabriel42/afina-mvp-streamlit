import pandas as pd
import unicodedata


FINANCIAL_ITEMS = {
    # Balance general
    "cash": {
        "label": "Caja / efectivo",
        "source_role": ["balance", "database"],
        "keywords": ["caja", "efectivo", "fondo fijo", "cuentas corrientes", "bancos"],
        "priority": 1
    },
    "accounts_receivable": {
        "label": "Cuentas por cobrar",
        "source_role": ["balance", "database"],
        "keywords": ["cuentas por cobrar", "documentos por cobrar", "clientes", "créditos comerciales", "creditos comerciales"],
        "priority": 1
    },
    "inventory": {
        "label": "Inventarios / existencias",
        "source_role": ["balance", "database"],
        "keywords": ["inventarios", "existencias", "mercadería", "mercaderia", "stock"],
        "priority": 1
    },
    "current_assets": {
        "label": "Activo corriente",
        "source_role": ["balance"],
        "keywords": ["total activos corrientes", "activos corrientes", "activo corriente"],
        "priority": 1
    },
    "non_current_assets": {
        "label": "Activo no corriente",
        "source_role": ["balance"],
        "keywords": ["activos no corrientes", "activo no corriente"],
        "priority": 2
    },
    "total_assets": {
        "label": "Activo total",
        "source_role": ["balance"],
        "keywords": ["total activos", "activo total"],
        "priority": 1
    },
    "current_liabilities": {
        "label": "Pasivo corriente",
        "source_role": ["balance"],
        "keywords": ["total pasivos corrientes", "pasivos corrientes", "pasivo corriente"],
        "priority": 1
    },
    "non_current_liabilities": {
        "label": "Pasivo no corriente",
        "source_role": ["balance"],
        "keywords": ["pasivos no corrientes", "pasivo no corriente"],
        "priority": 2
    },
    "total_liabilities": {
        "label": "Pasivo total",
        "source_role": ["balance"],
        "keywords": ["total pasivos", "pasivo total"],
        "priority": 1
    },
    "equity": {
        "label": "Patrimonio",
        "source_role": ["balance"],
        "keywords": ["patrimonio", "total patrimonio", "capital", "resultados acumulados"],
        "priority": 1
    },

    # Estado de resultados
    "sales": {
        "label": "Ventas / ingresos",
        "source_role": ["pnl", "database"],
        "keywords": ["ingresos por ventas", "ventas", "ingresos operacionales", "ingresos"],
        "priority": 1
    },
    "cost_of_sales": {
        "label": "Costo de ventas",
        "source_role": ["pnl", "database"],
        "keywords": ["costo de ventas", "costos de ventas", "consumo de mercaderías", "consumo de mercaderias"],
        "priority": 1
    },
    "gross_profit": {
        "label": "Utilidad bruta",
        "source_role": ["pnl", "database"],
        "keywords": ["utilidad bruta", "margen bruto", "margen comercial"],
        "priority": 1
    },
    "operating_result": {
        "label": "Resultado operativo",
        "source_role": ["pnl", "database"],
        "keywords": ["resultado operativo", "resultado de explotación", "resultado de explotacion", "ebit"],
        "priority": 1
    },
    "financial_expenses": {
        "label": "Gastos financieros",
        "source_role": ["pnl", "cashflow", "database"],
        "keywords": ["gastos financieros", "gasto financiero", "intereses"],
        "priority": 2
    },
    "net_income": {
        "label": "Utilidad neta / resultado del ejercicio",
        "source_role": ["pnl", "database"],
        "keywords": ["utilidad neta", "resultado del ejercicio", "determinación del resultado del ejercicio", "determinacion del resultado del ejercicio"],
        "priority": 1
    },

    # Flujo de caja
    "operating_cash_flow": {
        "label": "Flujo operativo",
        "source_role": ["cashflow"],
        "keywords": ["efectivo generado en la operación", "efectivo generado en la operacion", "actividades de operación", "actividades de operacion"],
        "priority": 1
    },
    "investing_cash_flow": {
        "label": "Flujo de inversión",
        "source_role": ["cashflow"],
        "keywords": ["efectivo utilizado en actividades de inversión", "efectivo utilizado en actividades de inversion", "actividades de inversión", "actividades de inversion"],
        "priority": 1
    },
    "financing_cash_flow": {
        "label": "Flujo de financiamiento",
        "source_role": ["cashflow"],
        "keywords": ["efectivo proveniente de actividades de financiamiento", "actividades de financiamiento"],
        "priority": 1
    },
    "ending_cash": {
        "label": "Saldo final de efectivo",
        "source_role": ["cashflow", "balance"],
        "keywords": ["saldo de efectivo al final", "saldo final de efectivo", "efectivo al final"],
        "priority": 1
    },

    # Ratios
    "current_ratio": {
        "label": "Ratio de liquidez corriente",
        "source_role": ["ratios"],
        "keywords": ["current ratio", "ratio de liquidez", "liquidez corriente"],
        "priority": 1
    },
    "quick_ratio": {
        "label": "Quick ratio / prueba ácida",
        "source_role": ["ratios"],
        "keywords": ["quick ratio", "prueba ácida", "prueba acida"],
        "priority": 1
    },
    "roe": {
        "label": "ROE",
        "source_role": ["ratios"],
        "keywords": ["roe", "return on equity", "rentabilidad sobre patrimonio"],
        "priority": 1
    },
    "roa": {
        "label": "ROA",
        "source_role": ["ratios"],
        "keywords": ["roa", "return on assets", "rentabilidad sobre activos"],
        "priority": 1
    },
    "debt_ratio": {
        "label": "Nivel de endeudamiento",
        "source_role": ["ratios", "balance"],
        "keywords": ["debt ratio", "endeudamiento", "deuda total", "pasivo total / activo total"],
        "priority": 1
    },
    "cash_conversion_cycle": {
        "label": "Ciclo de caja",
        "source_role": ["ratios"],
        "keywords": ["cash conversion cycle", "ciclo de caja", "ciclo financiero"],
        "priority": 2
    }
}


BASE_COLUMNS = {
    "Fila original",
    "Tipo de fila",
    "Estado financiero",
    "Categoría",
    "Cuenta detectada",
    "Código"
}


def normalize_text(value):
    if pd.isna(value):
        return ""

    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join([c for c in text if not unicodedata.combining(c)])
    text = " ".join(text.split())

    return text


def get_numeric_columns(df):
    numeric_columns = []

    for col in df.columns:
        if col in BASE_COLUMNS:
            continue

        numeric_series = pd.to_numeric(df[col], errors="coerce")

        if numeric_series.notna().sum() > 0:
            numeric_columns.append(col)

    return numeric_columns


def get_last_numeric_value(row, numeric_columns):
    """
    Toma el último valor numérico disponible en la fila.
    En estados financieros suele representar el período más reciente dentro de la tabla.
    """
    last_value = None
    last_column = None

    for col in numeric_columns:
        value = pd.to_numeric(row.get(col), errors="coerce")

        if pd.notna(value):
            last_value = float(value)
            last_column = col

    return last_value, last_column


def match_score(account_name, keywords):
    normalized_account = normalize_text(account_name)

    if not normalized_account:
        return 0

    best_score = 0

    for keyword in keywords:
        normalized_keyword = normalize_text(keyword)

        if not normalized_keyword:
            continue

        if normalized_account == normalized_keyword:
            best_score = max(best_score, 100)

        elif normalized_keyword in normalized_account:
            best_score = max(best_score, 80)

        elif any(part in normalized_account for part in normalized_keyword.split() if len(part) > 4):
            best_score = max(best_score, 45)

    return best_score


def find_best_match(normalized_df, item_config):
    if normalized_df is None or normalized_df.empty:
        return None

    if "Cuenta detectada" not in normalized_df.columns:
        return None

    numeric_columns = get_numeric_columns(normalized_df)

    if not numeric_columns:
        return None

    candidates = []

    for _, row in normalized_df.iterrows():
        account_name = row.get("Cuenta detectada", "")
        score = match_score(account_name, item_config["keywords"])

        if score <= 0:
            continue

        value, value_column = get_last_numeric_value(row, numeric_columns)

        candidates.append({
            "score": score,
            "account_name": account_name,
            "value": value,
            "value_column": value_column,
            "row_type": row.get("Tipo de fila", ""),
            "category": row.get("Categoría", ""),
            "statement": row.get("Estado financiero", ""),
            "code": row.get("Código", "")
        })

    if not candidates:
        return None

    # Prioriza coincidencia textual fuerte y, luego, filas con valores numéricos.
    candidates = sorted(
        candidates,
        key=lambda item: (
            item["score"],
            item["value"] is not None,
            item["row_type"] in ["Subtotal / total", "Cuenta financiera"]
        ),
        reverse=True
    )

    return candidates[0]


def extract_financial_items(documents):
    """
    Extrae partidas financieras clave desde documentos FP&A mapeados.
    """
    extracted_rows = []

    for item_key, item_config in FINANCIAL_ITEMS.items():
        best_global_match = None
        best_source_role = None
        best_source_label = None
        best_sheet = None

        for role in item_config["source_role"]:
            if role not in documents:
                continue

            doc = documents[role]
            normalized_df = doc["normalization"]["normalized_df"]

            match = find_best_match(normalized_df, item_config)

            if match is None:
                continue

            if best_global_match is None or match["score"] > best_global_match["score"]:
                best_global_match = match
                best_source_role = role
                best_source_label = doc["role_label"]
                best_sheet = doc["sheet_name"]

        if best_global_match is None:
            extracted_rows.append({
                "Código interno": item_key,
                "Partida FP&A": item_config["label"],
                "Fuente esperada": ", ".join(item_config["source_role"]),
                "Estado": "No detectada",
                "Fuente utilizada": "",
                "Hoja": "",
                "Cuenta detectada": "",
                "Categoría": "",
                "Valor detectado": None,
                "Columna valor": "",
                "Confianza": 0
            })
        else:
            extracted_rows.append({
                "Código interno": item_key,
                "Partida FP&A": item_config["label"],
                "Fuente esperada": ", ".join(item_config["source_role"]),
                "Estado": "Detectada",
                "Fuente utilizada": best_source_label,
                "Hoja": best_sheet,
                "Cuenta detectada": best_global_match["account_name"],
                "Categoría": best_global_match["category"],
                "Valor detectado": best_global_match["value"],
                "Columna valor": best_global_match["value_column"],
                "Confianza": best_global_match["score"]
            })

    items_df = pd.DataFrame(extracted_rows)

    detected_count = int((items_df["Estado"] == "Detectada").sum())
    total_count = len(items_df)

    coverage = round((detected_count / total_count) * 100, 1) if total_count else 0

    if coverage >= 75:
        status = "Alta"
        detail = "AFINA detectó la mayoría de las partidas necesarias para iniciar KPIs y diagnóstico financiero."
    elif coverage >= 45:
        status = "Media"
        detail = "AFINA detectó varias partidas clave, pero algunas deberán validarse o completarse antes del informe final."
    else:
        status = "Baja"
        detail = "AFINA detectó pocas partidas clave. Conviene revisar el mapeo de hojas o normalización."

    summary = {
        "total_items": total_count,
        "detected_items": detected_count,
        "missing_items": total_count - detected_count,
        "coverage": coverage,
        "status": status,
        "detail": detail
    }

    return items_df, summary
