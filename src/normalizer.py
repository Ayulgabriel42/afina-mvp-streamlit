import re
import unicodedata
import pandas as pd


CATEGORY_KEYWORDS = {
    "Flujo de caja": [
        "estado de flujos de efectivo",
        "flujo de efectivo",
        "flujo de caja",
        "cash flow",
        "efectivo proveniente",
        "efectivo utilizado",
        "efectivo demandado",
        "efectivo generado",
        "efectivo provisto",
        "actividades de operacion",
        "actividades de operación",
        "actividades operativas",
        "actividades de inversion",
        "actividades de inversión",
        "actividades de financiamiento",
        "aumento disminucion del efectivo",
        "aumento (disminucion) del efectivo",
        "saldo de efectivo",
        "capex"
    ],
    "Resultados": [
        "estado de resultados",
        "ventas",
        "ingresos",
        "costos",
        "costo de ventas",
        "gastos",
        "margen comercial",
        "valor agregado",
        "excedente bruto",
        "resultado de explotacion",
        "resultado de explotación",
        "resultado operativo",
        "ebit",
        "ebitda",
        "utilidad",
        "ganancia",
        "perdida",
        "pérdida",
        "impuesto a la renta",
        "gastos financieros",
        "otros ingresos",
        "otros gastos"
    ],
    "Capital de trabajo": [
        "capital de trabajo",
        "cuentas por cobrar",
        "documentos por cobrar",
        "clientes",
        "deudores",
        "cuentas por pagar",
        "proveedores",
        "inventarios",
        "stock",
        "mercaderia",
        "mercadería"
    ],
    "Pasivos": [
        "pasivo",
        "pasivos",
        "cuentas por pagar",
        "proveedores",
        "deuda",
        "deudas",
        "prestamos",
        "préstamos",
        "obligaciones",
        "acreedores",
        "tributos",
        "impuestos por pagar",
        "pasivos por impuestos diferidos"
    ],
    "Patrimonio": [
        "patrimonio",
        "capital",
        "reserva",
        "reservas",
        "resultados acumulados",
        "utilidades retenidas",
        "resultado del ejercicio",
        "utilidades acumuladas"
    ],
    "Activos": [
        "activo",
        "activos",
        "efectivo",
        "caja",
        "banco",
        "bancos",
        "cuentas corrientes",
        "fondo fijo",
        "depositos",
        "depósitos",
        "propiedades",
        "planta",
        "equipo",
        "intangibles",
        "inversiones"
    ]
}


STATEMENT_KEYWORDS = {
    "Flujo de caja": [
        "estado de flujos de efectivo",
        "flujo de efectivo",
        "flujo de caja",
        "cash flow",
        "actividades de operacion",
        "actividades de operación",
        "actividades de inversion",
        "actividades de inversión",
        "actividades de financiamiento",
        "efectivo proveniente",
        "efectivo generado",
        "efectivo utilizado",
        "saldo de efectivo"
    ],
    "Estado de resultados": [
        "estado de resultados",
        "p&l",
        "profit and loss",
        "ventas",
        "ingresos",
        "costo de ventas",
        "margen comercial",
        "resultado operativo",
        "ebit",
        "ebitda",
        "utilidad neta",
        "gastos financieros"
    ],
    "Balance general": [
        "balance general",
        "balance sheet",
        "activo total",
        "pasivo total",
        "patrimonio",
        "activos corrientes",
        "pasivos corrientes"
    ]
}


TITLE_KEYWORDS = [
    "andes chemical",
    "estado de flujos de efectivo",
    "estado de resultados",
    "balance general",
    "balance sheet",
    "expresado en",
    "expresado en usd",
    "expresado en soles",
    "moneda",
    "concepto",
    "c o n c e p t o"
]


SUBTOTAL_KEYWORDS = [
    "total",
    "subtotal",
    "resultado",
    "saldo final",
    "saldo inicial",
    "efectivo generado",
    "efectivo demandado",
    "efectivo provisto",
    "aumento",
    "disminucion",
    "disminución"
]


def normalize_text(value):
    if pd.isna(value):
        return ""

    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join([c for c in text if not unicodedata.combining(c)])
    text = " ".join(text.split())

    return text


def is_unnamed_column(col):
    return str(col).lower().startswith("unnamed")


def is_numeric_like(value):
    if pd.isna(value):
        return False

    text = str(value).strip()

    if text == "":
        return False

    text = text.replace(".", "").replace(",", "").replace("-", "")
    return text.isdigit()


def safe_to_numeric(series):
    return pd.to_numeric(series, errors="coerce")


def clean_label(value):
    if pd.isna(value):
        return ""

    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def clean_account_name(value):
    if pd.isna(value):
        return ""

    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)

    return text


def get_short_text_hint(series):
    common_hints = [
        "MN", "ME", "USD", "ARS", "PEN", "S/.", "S/", "LOCAL",
        "EXTRANJERA", "DEBE", "HABER", "SALDO"
    ]

    sample = series.head(12).dropna()

    for value in sample:
        text = clean_label(value)

        if not text:
            continue

        upper_text = text.upper()

        if len(upper_text) <= 14 and not is_numeric_like(upper_text):
            for hint in common_hints:
                if hint in upper_text:
                    return upper_text

    return ""


def make_unique_names(names):
    seen = {}
    result = []

    for name in names:
        base = name if name else "Valor financiero"

        if base not in seen:
            seen[base] = 1
            result.append(base)
        else:
            seen[base] += 1
            result.append(f"{base} ({seen[base]})")

    return result


def build_value_column_labels(df, value_columns):
    labels = {}
    proposed_names = []
    columns = list(df.columns)

    last_named_group = None

    for col in columns:
        if not is_unnamed_column(col):
            last_named_group = clean_label(col)

        if col not in value_columns:
            continue

        if is_unnamed_column(col):
            base_label = last_named_group or "Valor financiero"
        else:
            base_label = clean_label(col)

        hint = get_short_text_hint(df[col])

        if hint and hint.upper() not in base_label.upper():
            final_label = f"{base_label} - {hint}"
        else:
            final_label = base_label

        proposed_names.append(final_label)

    unique_names = make_unique_names(proposed_names)

    for original_col, friendly_name in zip(value_columns, unique_names):
        labels[original_col] = friendly_name

    return labels


def detect_account_column(df):
    preferred_names = [
        "denominacion",
        "denominación",
        "descripcion",
        "descripción",
        "cuenta descripcion",
        "detalle",
        "glosa",
        "concepto"
    ]

    for col in df.columns:
        col_norm = normalize_text(col)
        if any(name in col_norm for name in preferred_names):
            return col

    best_col = None
    best_score = -1

    for col in df.columns:
        series = df[col].dropna()

        if series.empty:
            continue

        text_count = 0
        numeric_count = 0
        total_length = 0

        for value in series:
            value_str = str(value).strip()

            if not value_str or value_str.lower() == "none":
                continue

            if is_numeric_like(value_str):
                numeric_count += 1
            else:
                text_count += 1
                total_length += len(value_str)

        avg_length = total_length / text_count if text_count > 0 else 0
        score = (text_count * 2) + (avg_length * 0.15) - (numeric_count * 0.8)

        if score > best_score:
            best_score = score
            best_col = col

    return best_col


def detect_code_column(df, account_col):
    preferred_names = ["cuenta", "codigo", "código", "cod", "plan"]

    for col in df.columns:
        if col == account_col:
            continue

        col_norm = normalize_text(col)

        if any(name in col_norm for name in preferred_names):
            return col

    best_col = None
    best_score = -1

    for col in df.columns:
        if col == account_col:
            continue

        series = df[col].dropna()

        if series.empty:
            continue

        short_code_count = 0
        long_text_count = 0

        for value in series:
            value_str = str(value).strip()

            if not value_str or value_str.lower() == "none":
                continue

            normalized = normalize_text(value_str)

            is_short = len(value_str) <= 14
            looks_like_code = bool(re.match(r"^[A-Za-z0-9\-\.\+]+$", value_str))

            if is_short and looks_like_code:
                short_code_count += 1

            if len(normalized) > 25 and not is_numeric_like(value_str):
                long_text_count += 1

        score = short_code_count - (long_text_count * 1.5)

        if score > best_score:
            best_score = score
            best_col = col

    if best_score <= 0:
        return None

    return best_col


def detect_value_columns(df, account_col=None, code_col=None):
    value_columns = []

    for col in df.columns:
        if col == account_col or col == code_col:
            continue

        numeric_series = safe_to_numeric(df[col])
        numeric_count = numeric_series.notna().sum()
        non_null_count = df[col].notna().sum()

        if non_null_count == 0:
            continue

        numeric_ratio = numeric_count / non_null_count

        if numeric_ratio >= 0.35 and numeric_count >= 3:
            value_columns.append(col)

    return value_columns


def infer_statement_type(account_name):
    normalized = normalize_text(account_name)

    for statement, keywords in STATEMENT_KEYWORDS.items():
        for keyword in keywords:
            if normalize_text(keyword) in normalized:
                return statement

    return "No determinado"


def classify_account(account_name):
    normalized = normalize_text(account_name)

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if normalize_text(keyword) in normalized:
                return category

    return "Sin clasificar"


def infer_row_type(account_name, numeric_values_count=0):
    normalized = normalize_text(account_name)

    if not normalized:
        return "Vacía"

    if any(normalize_text(keyword) in normalized for keyword in TITLE_KEYWORDS):
        if numeric_values_count == 0:
            return "Título / encabezado"

    if normalized.replace(" ", "") in ["concepto", "cuenta", "descripcion", "descripcioncuenta"]:
        return "Encabezado"

    if len(normalized) <= 2:
        return "Encabezado"

    if any(normalize_text(keyword) in normalized for keyword in SUBTOTAL_KEYWORDS):
        return "Subtotal / total"

    if numeric_values_count > 0:
        return "Cuenta financiera"

    return "Texto / referencia"


def normalize_financial_dataframe(
    df,
    account_col=None,
    code_col=None,
    value_columns=None
):
    working_df = df.copy()

    working_df = working_df.dropna(how="all")
    working_df = working_df.dropna(axis=1, how="all")

    if account_col is None:
        account_col = detect_account_column(working_df)

    if code_col == "No usar código":
        code_col = None

    if code_col is None:
        code_col = detect_code_column(working_df, account_col)

    if value_columns is None:
        value_columns = detect_value_columns(working_df, account_col, code_col)

    value_column_labels = build_value_column_labels(working_df, value_columns)

    normalized_rows = []

    if account_col is None:
        return {
            "normalized_df": pd.DataFrame(),
            "account_column": None,
            "code_column": None,
            "value_columns": [],
            "value_column_labels": {},
            "rows_detected": 0,
            "status": "No se pudo detectar una columna de cuentas.",
            "warnings": [
                "AFINA no pudo identificar una columna clara de cuentas contables."
            ]
        }

    for idx, row in working_df.iterrows():
        account_name = clean_account_name(row.get(account_col, ""))

        if not account_name:
            continue

        if account_name.lower() == "none":
            continue

        if len(account_name) < 3:
            continue

        numeric_values_count = 0
        value_data = {}

        for col in value_columns:
            friendly_col_name = value_column_labels.get(col, str(col))
            value = pd.to_numeric(row.get(col), errors="coerce")

            if pd.notna(value):
                numeric_values_count += 1
                value_data[friendly_col_name] = value
            else:
                value_data[friendly_col_name] = None

        row_type = infer_row_type(account_name, numeric_values_count)
        statement_type = infer_statement_type(account_name)
        category = classify_account(account_name)

        if statement_type != "No determinado" and category == "Activos":
            category = statement_type

        row_data = {
            "Fila original": idx,
            "Tipo de fila": row_type,
            "Estado financiero": statement_type,
            "Categoría": category,
            "Cuenta detectada": account_name,
        }

        if code_col is not None:
            code_value = row.get(code_col, "")
            row_data["Código"] = "" if pd.isna(code_value) else str(code_value).strip()
        else:
            row_data["Código"] = ""

        row_data.update(value_data)
        normalized_rows.append(row_data)

    normalized_df = pd.DataFrame(normalized_rows)

    warnings = []

    if account_col is not None and is_unnamed_column(account_col):
        warnings.append(
            f"La columna de cuentas fue detectada como '{account_col}'. El archivo parece tener encabezados no normalizados."
        )

    if code_col is not None and is_unnamed_column(code_col):
        warnings.append(
            f"La columna de código fue detectada como '{code_col}'. Puede requerir validación manual."
        )

    if len(value_columns) == 0:
        warnings.append(
            "No se detectaron columnas numéricas suficientes para calcular KPIs."
        )

    if normalized_df.empty:
        status = "No se pudieron normalizar cuentas financieras."
    else:
        financial_rows = (
            normalized_df["Tipo de fila"].eq("Cuenta financiera").sum()
            if "Tipo de fila" in normalized_df.columns
            else len(normalized_df)
        )

        status = (
            f"Se normalizaron {len(normalized_df)} filas, "
            f"de las cuales {financial_rows} parecen cuentas financieras."
        )

    return {
        "normalized_df": normalized_df,
        "account_column": account_col,
        "code_column": code_col,
        "value_columns": value_columns,
        "value_column_labels": value_column_labels,
        "rows_detected": len(normalized_df),
        "status": status,
        "warnings": warnings
    }
