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



def row_to_searchable_text(row):
    parts = []

    for value in row:
        if pd.isna(value):
            continue

        text = str(value).strip()

        if text and text.lower() != "none":
            parts.append(text)

    return " | ".join(parts)


def get_last_numeric_value_from_raw_row(row):
    last_value = None
    last_column = None

    for col, value in row.items():
        numeric_value = pd.to_numeric(value, errors="coerce")

        if pd.notna(numeric_value):
            last_value = float(numeric_value)
            last_column = col

    return last_value, last_column


def find_best_match_raw(raw_df, item_config):
    """
    Búsqueda alternativa sobre la fila completa del Excel original.
    Esto ayuda especialmente en hojas de ratios donde el normalizador puede confundir
    la columna de unidad con la columna de indicador.
    """
    if raw_df is None or raw_df.empty:
        return None

    candidates = []

    for _, row in raw_df.iterrows():
        searchable_text = row_to_searchable_text(row)
        score = match_score(searchable_text, item_config["keywords"])

        if score <= 0:
            continue

        value, value_column = get_last_numeric_value_from_raw_row(row)

        candidates.append({
            "score": score,
            "account_name": searchable_text[:180],
            "value": value,
            "value_column": value_column,
            "row_type": "Cuenta financiera",
            "category": "Detectado desde fila original",
            "statement": "No determinado",
            "code": ""
        })

    if not candidates:
        return None

    candidates = sorted(
        candidates,
        key=lambda item: (
            item["score"],
            item["value"] is not None
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

            raw_match = find_best_match_raw(
                doc.get("dataframe"),
                item_config
            )

            if raw_match is not None and (
                match is None or raw_match["score"] > match["score"]
            ):
                match = raw_match

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


# ============================================================
# Mejora de calidad FP&A - selección más confiable de partidas
# ============================================================

QUALITY_RULES = {
    "total_assets": {
        "extra_keywords": ["total activo", "activos totales", "total de activos"],
        "negative_keywords": [
            "activos corrientes",
            "activo corriente",
            "activos no corrientes",
            "activo no corriente",
            "total activos corrientes",
            "total activos no corrientes"
        ],
        "preferred_roles": ["balance"],
        "prefer_subtotal": True,
        "avoid_zero": True
    },
    "current_assets": {
        "extra_keywords": ["total activos corrientes", "activos corrientes", "activo corriente"],
        "negative_keywords": ["no corriente", "no corrientes"],
        "preferred_roles": ["balance"],
        "prefer_subtotal": True,
        "avoid_zero": True
    },
    "total_liabilities": {
        "extra_keywords": ["total pasivo", "pasivos totales", "total de pasivos"],
        "negative_keywords": [
            "pasivos corrientes",
            "pasivo corriente",
            "pasivos no corrientes",
            "pasivo no corriente",
            "total pasivos corrientes",
            "total pasivos no corrientes"
        ],
        "preferred_roles": ["balance"],
        "prefer_subtotal": True,
        "avoid_zero": True
    },
    "current_liabilities": {
        "extra_keywords": ["total pasivos corrientes", "pasivos corrientes", "pasivo corriente"],
        "negative_keywords": ["no corriente", "no corrientes"],
        "preferred_roles": ["balance"],
        "prefer_subtotal": True,
        "avoid_zero": True
    },
    "equity": {
        "extra_keywords": [
            "total patrimonio",
            "patrimonio neto",
            "total patrimonio neto",
            "patrimonio atribuible",
            "capital y reservas"
        ],
        "negative_keywords": [
            "pasivo y patrimonio",
            "total pasivos y patrimonio",
            "pasivos y patrimonio"
        ],
        "preferred_roles": ["balance"],
        "prefer_subtotal": True,
        "avoid_zero": True
    },
    "sales": {
        "extra_keywords": [
            "ingresos por ventas",
            "ventas netas",
            "ingresos de actividades ordinarias",
            "ingresos operacionales"
        ],
        "negative_keywords": [
            "costo",
            "gasto",
            "descuento",
            "devolucion",
            "devolución"
        ],
        "preferred_roles": ["pnl", "database"],
        "avoid_zero": True
    },
    "gross_profit": {
        "extra_keywords": [
            "utilidad bruta",
            "ganancia bruta",
            "margen bruto",
            "margen comercial"
        ],
        "negative_keywords": [],
        "preferred_roles": ["pnl", "database"],
        "prefer_subtotal": True
    },
    "operating_result": {
        "extra_keywords": [
            "resultado operativo",
            "resultado de explotacion",
            "resultado de explotación",
            "utilidad operativa",
            "ebit"
        ],
        "negative_keywords": [
            "antes de participaciones",
            "antes de impuestos",
            "resultado antes"
        ],
        "preferred_roles": ["pnl", "database"],
        "prefer_subtotal": True
    },
    "net_income": {
        "extra_keywords": [
            "utilidad neta",
            "resultado neto",
            "ganancia neta",
            "resultado del ejercicio",
            "determinacion del resultado del ejercicio",
            "determinación del resultado del ejercicio"
        ],
        "negative_keywords": [
            "bruta",
            "operativo",
            "operativa",
            "antes de impuestos",
            "antes de participaciones"
        ],
        "preferred_roles": ["pnl", "database"],
        "prefer_subtotal": True,
        "avoid_zero": True
    },
    "debt_ratio": {
        "extra_keywords": [
            "debt ratio",
            "ratio de endeudamiento",
            "endeudamiento",
            "pasivo total activo total",
            "pasivo total / activo total"
        ],
        "negative_keywords": [],
        "preferred_roles": ["ratios", "balance"]
    },
    "current_ratio": {
        "extra_keywords": [
            "current ratio",
            "liquidez corriente",
            "ratio corriente",
            "razon corriente",
            "razón corriente"
        ],
        "negative_keywords": [],
        "preferred_roles": ["ratios"]
    },
    "quick_ratio": {
        "extra_keywords": [
            "quick ratio",
            "acid test",
            "prueba acida",
            "prueba ácida"
        ],
        "negative_keywords": [],
        "preferred_roles": ["ratios"]
    },
    "roe": {
        "extra_keywords": [
            "roe",
            "return on equity",
            "rentabilidad sobre patrimonio",
            "rentabilidad patrimonial"
        ],
        "negative_keywords": [],
        "preferred_roles": ["ratios"]
    },
    "roa": {
        "extra_keywords": [
            "roa",
            "return on assets",
            "rentabilidad sobre activos"
        ],
        "negative_keywords": [],
        "preferred_roles": ["ratios"]
    },
    "cash_conversion_cycle": {
        "extra_keywords": [
            "cash conversion cycle",
            "ciclo de caja",
            "ciclo financiero",
            "cash cycle"
        ],
        "negative_keywords": [],
        "preferred_roles": ["ratios"]
    }
}


def build_quality_item_config(item_key, item_config):
    """
    Crea una copia de la configuración original sumando keywords específicas
    para mejorar la detección sin modificar el diccionario base.
    """
    config = dict(item_config)
    rules = QUALITY_RULES.get(item_key, {})
    extra_keywords = rules.get("extra_keywords", [])

    config["keywords"] = list(dict.fromkeys(
        list(item_config.get("keywords", [])) + extra_keywords
    ))

    return config


def contains_any_keyword(text, keywords):
    normalized = normalize_text(text)

    for keyword in keywords:
        if normalize_text(keyword) in normalized:
            return True

    return False


def is_bad_quality_match(item_key, match):
    """
    Descarta coincidencias que parecen correctas por texto parcial,
    pero que financieramente corresponden a otra partida.
    """
    if match is None:
        return True

    rules = QUALITY_RULES.get(item_key, {})
    negative_keywords = rules.get("negative_keywords", [])

    account_name = match.get("account_name", "")

    if negative_keywords and contains_any_keyword(account_name, negative_keywords):
        return True

    return False


def adjusted_match_score(item_key, role, match, item_config):
    """
    Ajusta el score por calidad financiera:
    - Penaliza falsos positivos.
    - Premia fuentes esperadas.
    - Premia subtotales/totales cuando corresponde.
    - Penaliza valores cero en partidas donde un cero suele ser sospechoso.
    """
    if match is None:
        return -9999

    if is_bad_quality_match(item_key, match):
        return -9999

    rules = QUALITY_RULES.get(item_key, {})
    score = float(match.get("score", 0))

    preferred_roles = rules.get("preferred_roles", item_config.get("source_role", []))

    if role in preferred_roles:
        role_position = preferred_roles.index(role)
        score += max(0, 40 - (role_position * 10))

    row_type = str(match.get("row_type", ""))

    if rules.get("prefer_subtotal") and row_type == "Subtotal / total":
        score += 20

    if row_type == "Cuenta financiera":
        score += 8

    value = match.get("value", None)

    try:
        numeric_value = float(value) if value is not None else None
    except Exception:
        numeric_value = None

    if rules.get("avoid_zero") and numeric_value == 0:
        score -= 35

    if numeric_value is not None:
        score += 5

    return score


def choose_better_match(item_key, role, normalized_match, raw_match, item_config):
    """
    Elige entre la coincidencia encontrada en tabla normalizada y la encontrada
    en fila original.
    """
    normalized_score = adjusted_match_score(item_key, role, normalized_match, item_config)
    raw_score = adjusted_match_score(item_key, role, raw_match, item_config)

    if raw_score > normalized_score:
        raw_match["adjusted_score"] = raw_score
        return raw_match

    if normalized_match is not None:
        normalized_match["adjusted_score"] = normalized_score

    return normalized_match


def extract_financial_items(documents):
    """
    Extrae partidas financieras clave desde documentos FP&A mapeados.
    Versión mejorada:
    - Evita confundir totales con corrientes/no corrientes.
    - Prioriza P&L para resultados.
    - Prioriza Balance para activos/pasivos/patrimonio.
    - Usa búsqueda en fila original como respaldo.
    """
    extracted_rows = []

    for item_key, original_item_config in FINANCIAL_ITEMS.items():
        item_config = build_quality_item_config(item_key, original_item_config)

        best_global_match = None
        best_global_score = -9999
        best_source_label = None
        best_sheet = None

        for role in item_config["source_role"]:
            if role not in documents:
                continue

            doc = documents[role]
            normalized_df = doc["normalization"]["normalized_df"]

            normalized_match = find_best_match(normalized_df, item_config)

            try:
                raw_match = find_best_match_raw(
                    doc.get("dataframe"),
                    item_config
                )
            except NameError:
                raw_match = None

            match = choose_better_match(
                item_key,
                role,
                normalized_match,
                raw_match,
                item_config
            )

            if match is None:
                continue

            adjusted_score = match.get(
                "adjusted_score",
                adjusted_match_score(item_key, role, match, item_config)
            )

            if adjusted_score > best_global_score:
                best_global_score = adjusted_score
                best_global_match = match
                best_source_label = doc["role_label"]
                best_sheet = doc["sheet_name"]

        if best_global_match is None or best_global_score <= 0:
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
                "Confianza": round(best_global_score, 1)
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


# ============================================================
# Ajuste específico: priorizar Resultado Operativo desde P&L
# ============================================================

_BASE_EXTRACT_FINANCIAL_ITEMS_OPERATING_FIX = extract_financial_items


def _afina_get_latest_value_from_raw_financial_row(row):
    """
    Toma el último valor financiero de la fila, evitando columnas técnicas sueltas
    que pueden aparecer al final del Excel.
    Busca el bloque consecutivo más largo de valores numéricos y toma su último valor.
    """
    blocks = []
    current_block = []

    for col, value in row.items():
        numeric_value = pd.to_numeric(value, errors="coerce")

        if pd.notna(numeric_value):
            current_block.append((col, float(numeric_value)))
        else:
            if current_block:
                blocks.append(current_block)
                current_block = []

    if current_block:
        blocks.append(current_block)

    if not blocks:
        return None, None

    # Elegimos el bloque numérico más largo porque suele representar los períodos financieros.
    best_block = max(blocks, key=len)

    if not best_block:
        return None, None

    last_col, last_value = best_block[-1]

    return last_value, last_col


def _afina_find_operating_result_from_pnl(pnl_doc):
    """
    Busca Resultado Operativo específicamente dentro del P&L Statement.
    Prioriza:
    - Utilidad operativa
    - Resultado de explotación
    - Resultado operativo
    - EBIT

    Evita tomar resultados antes de impuestos o partidas auxiliares.
    """
    if pnl_doc is None:
        return None

    raw_df = pnl_doc.get("dataframe")

    if raw_df is None or raw_df.empty:
        return None

    positive_keywords = [
        "utilidad operativa",
        "resultado de explotacion",
        "resultado de explotación",
        "resultado operativo",
        "ebit"
    ]

    negative_keywords = [
        "antes de impuesto",
        "antes de impuestos",
        "antes imp",
        "despues imp",
        "después imp",
        "utilidad neta",
        "resultado neto",
        "gastos",
        "ingresos gastos"
    ]

    candidates = []

    for _, row in raw_df.iterrows():
        text_parts = []

        for value in row.values:
            if pd.isna(value):
                continue

            text = str(value).strip()

            if text:
                text_parts.append(text)

        searchable_text = " | ".join(text_parts)
        normalized_text = normalize_text(searchable_text)

        if not normalized_text:
            continue

        if any(normalize_text(word) in normalized_text for word in negative_keywords):
            continue

        score = 0

        for keyword in positive_keywords:
            normalized_keyword = normalize_text(keyword)

            if normalized_keyword in normalized_text:
                if keyword in ["utilidad operativa", "resultado de explotacion", "resultado de explotación", "resultado operativo"]:
                    score = max(score, 120)
                elif keyword == "ebit":
                    score = max(score, 90)

        if score <= 0:
            continue

        value, value_column = _afina_get_latest_value_from_raw_financial_row(row)

        if value is None:
            continue

        # Para este caso puntual, evitamos reemplazar con cero.
        if value == 0:
            continue

        candidates.append({
            "score": score,
            "account_name": searchable_text[:180],
            "value": value,
            "value_column": value_column,
            "row_type": "Subtotal / total",
            "category": "Resultados",
            "statement": "Estado de resultados",
            "code": ""
        })

    if not candidates:
        return None

    candidates = sorted(
        candidates,
        key=lambda item: (
            item["score"],
            abs(item["value"])
        ),
        reverse=True
    )

    return candidates[0]


def extract_financial_items(documents):
    """
    Wrapper final del extractor.
    Mantiene toda la lógica existente y solo corrige operating_result
    para priorizar P&L Statement cuando encuentra una partida no nula.
    """
    items_df, summary = _BASE_EXTRACT_FINANCIAL_ITEMS_OPERATING_FIX(documents)

    if documents is None or "pnl" not in documents:
        return items_df, summary

    pnl_doc = documents.get("pnl")
    better_operating_result = _afina_find_operating_result_from_pnl(pnl_doc)

    if better_operating_result is None:
        return items_df, summary

    mask = items_df["Código interno"] == "operating_result"

    if mask.any():
        items_df.loc[mask, "Estado"] = "Detectada"
        items_df.loc[mask, "Fuente utilizada"] = pnl_doc.get("role_label", "Estado de resultados")
        items_df.loc[mask, "Hoja"] = pnl_doc.get("sheet_name", "P&L Statement")
        items_df.loc[mask, "Cuenta detectada"] = better_operating_result["account_name"]
        items_df.loc[mask, "Categoría"] = better_operating_result["category"]
        items_df.loc[mask, "Valor detectado"] = better_operating_result["value"]
        items_df.loc[mask, "Columna valor"] = better_operating_result["value_column"]
        items_df.loc[mask, "Confianza"] = better_operating_result["score"]

    detected_count = int((items_df["Estado"] == "Detectada").sum())
    total_count = len(items_df)
    coverage = round((detected_count / total_count) * 100, 1) if total_count else 0

    summary = {
        "total_items": total_count,
        "detected_items": detected_count,
        "missing_items": total_count - detected_count,
        "coverage": coverage,
        "status": summary.get("status", "Alta"),
        "detail": summary.get(
            "detail",
            "AFINA detectó las partidas necesarias para iniciar KPIs y diagnóstico financiero."
        )
    }

    return items_df, summary
