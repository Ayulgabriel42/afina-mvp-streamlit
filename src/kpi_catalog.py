# Catálogo oficial de KPIs FP&A para AFINA
# Basado en el SRS: 19 KPIs núcleo organizados en 5 dimensiones FPA.

DIMENSION_ORDER = [
    "Estructura de inversión",
    "Capital de trabajo",
    "Rentabilidad",
    "Fluidez financiera",
    "Equilibrio financiero",
]


KPI_CATALOG = [
    # ============================================================
    # 1. Estructura de inversión
    # ============================================================
    {
        "srs_code": "K-01",
        "code": "debt_ratio",
        "name": "Endeudamiento",
        "dimension": "Estructura de inversión",
        "formula": "Pasivo total / Activo total",
        "unit": "percentage",
        "required_items": ["total_liabilities", "total_assets"],
        "order": 1,
    },
    {
        "srs_code": "K-02",
        "code": "debt_to_equity",
        "name": "Debt to Equity",
        "dimension": "Estructura de inversión",
        "formula": "Pasivo total / Patrimonio",
        "unit": "ratio",
        "required_items": ["total_liabilities", "equity"],
        "order": 2,
    },
    {
        "srs_code": "K-03",
        "code": "equity_multiplier",
        "name": "IAF / Equity Multiplier",
        "dimension": "Estructura de inversión",
        "formula": "Activo total / Patrimonio",
        "unit": "ratio",
        "required_items": ["total_assets", "equity"],
        "order": 3,
    },

    # ============================================================
    # 2. Capital de trabajo
    # ============================================================
    {
        "srs_code": "K-04",
        "code": "inventory_days",
        "name": "PMRI",
        "dimension": "Capital de trabajo",
        "formula": "(Inventarios × 360) / Costo de ventas",
        "unit": "days",
        "required_items": ["inventory", "cost_of_sales"],
        "order": 4,
    },
    {
        "srs_code": "K-05",
        "code": "receivables_days",
        "name": "PMCC",
        "dimension": "Capital de trabajo",
        "formula": "(Cuentas por cobrar × 360) / Ventas",
        "unit": "days",
        "required_items": ["accounts_receivable", "sales"],
        "order": 5,
    },
    {
        "srs_code": "K-06",
        "code": "payables_days",
        "name": "PMPP",
        "dimension": "Capital de trabajo",
        "formula": "(Cuentas por pagar × 360) / Costo de ventas",
        "unit": "days",
        "required_items": ["accounts_payable", "cost_of_sales"],
        "order": 6,
    },
    {
        "srs_code": "K-07",
        "code": "cash_conversion_cycle",
        "name": "Ciclo de caja",
        "dimension": "Capital de trabajo",
        "formula": "PMRI + PMCC - PMPP",
        "unit": "days",
        "required_items": ["inventory", "accounts_receivable", "accounts_payable", "cost_of_sales", "sales"],
        "order": 7,
    },

    # ============================================================
    # 3. Rentabilidad
    # ============================================================
    {
        "srs_code": "K-08",
        "code": "operating_margin",
        "name": "Margen operativo",
        "dimension": "Rentabilidad",
        "formula": "Resultado operativo / Ventas",
        "unit": "percentage",
        "required_items": ["operating_result", "sales"],
        "order": 8,
    },
    {
        "srs_code": "K-09",
        "code": "asset_turnover",
        "name": "Rotación de activos",
        "dimension": "Rentabilidad",
        "formula": "Ventas / Activo total",
        "unit": "ratio",
        "required_items": ["sales", "total_assets"],
        "order": 9,
    },
    {
        "srs_code": "K-10",
        "code": "roi",
        "name": "ROI",
        "dimension": "Rentabilidad",
        "formula": "Utilidad neta / Inversión total",
        "unit": "percentage",
        "required_items": ["net_income", "investment_total"],
        "order": 10,
    },
    {
        "srs_code": "K-11",
        "code": "roa",
        "name": "ROA",
        "dimension": "Rentabilidad",
        "formula": "Utilidad neta / Activo total",
        "unit": "percentage",
        "required_items": ["net_income", "total_assets"],
        "order": 11,
    },
    {
        "srs_code": "K-12",
        "code": "roe",
        "name": "ROE",
        "dimension": "Rentabilidad",
        "formula": "Utilidad neta / Patrimonio",
        "unit": "percentage",
        "required_items": ["net_income", "equity"],
        "order": 12,
    },

    # ============================================================
    # 4. Fluidez financiera
    # ============================================================
    {
        "srs_code": "K-13",
        "code": "current_ratio",
        "name": "Liquidez corriente",
        "dimension": "Fluidez financiera",
        "formula": "Activo corriente / Pasivo corriente",
        "unit": "ratio",
        "required_items": ["current_assets", "current_liabilities"],
        "order": 13,
    },
    {
        "srs_code": "K-14",
        "code": "quick_ratio",
        "name": "Quick Ratio",
        "dimension": "Fluidez financiera",
        "formula": "(Activo corriente - Inventarios) / Pasivo corriente",
        "unit": "ratio",
        "required_items": ["current_assets", "inventory", "current_liabilities"],
        "order": 14,
    },
    {
        "srs_code": "K-15",
        "code": "cash_ratio",
        "name": "Cash Ratio",
        "dimension": "Fluidez financiera",
        "formula": "Efectivo / Pasivo corriente",
        "unit": "ratio",
        "required_items": ["cash", "current_liabilities"],
        "order": 15,
    },
    {
        "srs_code": "K-16",
        "code": "ocf_to_current_liabilities",
        "name": "FCO / Pasivo corriente",
        "dimension": "Fluidez financiera",
        "formula": "Flujo de caja operativo / Pasivo corriente",
        "unit": "percentage",
        "required_items": ["operating_cash_flow", "current_liabilities"],
        "order": 16,
    },

    # ============================================================
    # 5. Equilibrio financiero
    # ============================================================
    {
        "srs_code": "K-17",
        "code": "debt_index",
        "name": "Índice de endeudamiento",
        "dimension": "Equilibrio financiero",
        "formula": "Deuda total / Patrimonio",
        "unit": "ratio",
        "required_items": ["total_debt", "equity"],
        "order": 17,
    },
    {
        "srs_code": "K-18",
        "code": "interest_coverage",
        "name": "Cobertura de gastos financieros",
        "dimension": "Equilibrio financiero",
        "formula": "EBIT / Gastos financieros",
        "unit": "ratio",
        "required_items": ["operating_result", "financial_expenses"],
        "order": 18,
    },
    {
        "srs_code": "K-19",
        "code": "debt_to_ebitda",
        "name": "Deuda / EBITDA",
        "dimension": "Equilibrio financiero",
        "formula": "Deuda total / EBITDA",
        "unit": "ratio",
        "required_items": ["total_debt", "ebitda"],
        "order": 19,
    },
]


KPI_BY_CODE = {item["code"]: item for item in KPI_CATALOG}


def get_kpi_definition(kpi_code):
    return KPI_BY_CODE.get(kpi_code)


def get_catalog_codes():
    return [item["code"] for item in KPI_CATALOG]


def get_dimension_order():
    return DIMENSION_ORDER
