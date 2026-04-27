NO_USAR = "No usar"


STATEMENT_ROLES = {
    "balance": "Balance general / Estado de situación financiera",
    "pnl": "Estado de resultados",
    "cashflow": "Estado de flujo de efectivo",
    "ratios": "Ratios financieros",
    "database": "Base contable auxiliar"
}


SHEET_PATTERNS = {
    "balance": [
        "balance sheet",
        "balance",
        "bs mes",
        "asset accounts",
        "liability accounts",
        "estado de situacion",
        "estado de situación"
    ],
    "pnl": [
        "p&l statement",
        "p&l",
        "profit and loss",
        "resultados",
        "estado de resultados",
        "pl mes"
    ],
    "cashflow": [
        "cash flow statement",
        "cash flow",
        "flujo",
        "cfs",
        "cfs mes"
    ],
    "ratios": [
        "financial ratios",
        "ratios",
        "indicadores"
    ],
    "database": [
        "data base",
        "database",
        "base contable",
        "bc.",
        "bc. me"
    ]
}


def normalize(value):
    return str(value).strip().lower()


def suggest_sheet_mapping(sheet_names):
    """
    Sugiere qué hoja corresponde a cada estado financiero.
    """
    suggestions = {}

    normalized_sheets = {
        sheet: normalize(sheet)
        for sheet in sheet_names
    }

    for role, patterns in SHEET_PATTERNS.items():
        suggestions[role] = NO_USAR

        for sheet, normalized_sheet in normalized_sheets.items():
            for pattern in patterns:
                if pattern in normalized_sheet:
                    suggestions[role] = sheet
                    break

            if suggestions[role] != NO_USAR:
                break

    return suggestions


def calculate_mapping_completeness(mapping):
    """
    Calcula un porcentaje simple de completitud del mapeo FP&A.
    Mínimo deseable: Balance + Estado de resultados + Flujo de efectivo.
    """
    required_roles = ["balance", "pnl", "cashflow"]
    optional_roles = ["ratios", "database"]

    required_done = sum(
        1 for role in required_roles
        if mapping.get(role) and mapping.get(role) != NO_USAR
    )

    optional_done = sum(
        1 for role in optional_roles
        if mapping.get(role) and mapping.get(role) != NO_USAR
    )

    score = round(
        ((required_done / len(required_roles)) * 80)
        + ((optional_done / len(optional_roles)) * 20),
        1
    )

    if score >= 90:
        status = "Completo"
        detail = "El archivo tiene estados suficientes para un análisis FP&A integral."
    elif score >= 60:
        status = "Parcial"
        detail = "El archivo permite un análisis financiero inicial, aunque podrían faltar estados clave."
    else:
        status = "Básico"
        detail = "El archivo requiere más estados financieros para un diagnóstico completo."

    return {
        "score": score,
        "status": status,
        "detail": detail,
        "required_done": required_done,
        "optional_done": optional_done
    }
