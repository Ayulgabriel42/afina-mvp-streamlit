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


# === AFINA KPI EXTENDED METADATA ===
# Metadata complementaria no invasiva.
# No cambia la estructura base del catálogo; solo agrega campos para auditoría,
# diagnósticos, chatbot, PDF/Word e insights.

KPI_EXTENDED_METADATA = {
    "debt_ratio": {
        "direction": "lower_is_better",
        "format": "percent",
        "diagnostic_by_status": {
            "Verde": "El endeudamiento sobre activos se mantiene en un rango saludable.",
            "Amarillo": "El endeudamiento sobre activos es moderado y requiere seguimiento.",
            "Rojo": "El endeudamiento sobre activos es elevado.",
        },
        "action_suggested": "Revisar composición de pasivos, estructura de deuda y capacidad de generación de caja.",
    },
    "debt_to_equity": {
        "direction": "lower_is_better",
        "format": "ratio",
        "diagnostic_by_status": {
            "Verde": "La relación deuda/patrimonio se mantiene controlada.",
            "Amarillo": "La relación deuda/patrimonio es moderada.",
            "Rojo": "La relación deuda/patrimonio es elevada.",
        },
        "action_suggested": "Evaluar capitalización, refinanciación y equilibrio entre deuda y patrimonio.",
    },
    "equity_multiplier": {
        "direction": "lower_is_better",
        "format": "ratio",
        "diagnostic_by_status": {
            "Verde": "El apalancamiento financiero se encuentra dentro de un rango razonable.",
            "Amarillo": "El apalancamiento financiero requiere seguimiento.",
            "Rojo": "El apalancamiento financiero es elevado.",
        },
        "action_suggested": "Analizar si el crecimiento de activos se sostiene con una estructura patrimonial adecuada.",
    },
    "inventory_days": {
        "direction": "lower_is_better",
        "format": "days",
        "diagnostic_by_status": {
            "Verde": "La permanencia de inventarios es razonable.",
            "Amarillo": "La permanencia de inventarios puede afectar capital de trabajo.",
            "Rojo": "La permanencia de inventarios es elevada y puede inmovilizar caja.",
        },
        "action_suggested": "Revisar rotación de stock, obsolescencia, niveles mínimos y planificación de compras.",
    },
    "receivables_days": {
        "direction": "lower_is_better",
        "format": "days",
        "diagnostic_by_status": {
            "Verde": "El plazo promedio de cobro es saludable.",
            "Amarillo": "El plazo promedio de cobro requiere seguimiento.",
            "Rojo": "El plazo promedio de cobro es elevado y puede presionar la liquidez.",
        },
        "action_suggested": "Fortalecer gestión de cobranzas, política de crédito y seguimiento de vencimientos.",
    },
    "payables_days": {
        "direction": "higher_is_better",
        "format": "days",
        "diagnostic_by_status": {
            "Verde": "El plazo promedio de pago favorece la gestión de caja.",
            "Amarillo": "El plazo promedio de pago es aceptable, pero podría optimizarse.",
            "Rojo": "El plazo promedio de pago es bajo y puede presionar la caja.",
        },
        "action_suggested": "Negociar mejores plazos con proveedores sin deteriorar relaciones comerciales.",
    },
    "cash_conversion_cycle": {
        "direction": "lower_is_better",
        "format": "days",
        "diagnostic_by_status": {
            "Verde": "El ciclo de caja es razonable.",
            "Amarillo": "El ciclo de caja puede presionar el capital de trabajo.",
            "Rojo": "El ciclo de caja es elevado y puede tensionar la liquidez.",
        },
        "action_suggested": "Reducir días de inventario y cobranza, y optimizar plazos de pago.",
    },
    "operating_margin": {
        "direction": "higher_is_better",
        "format": "percent",
        "diagnostic_by_status": {
            "Verde": "El margen operativo muestra una rentabilidad operativa saludable.",
            "Amarillo": "El margen operativo es positivo, pero requiere mejora.",
            "Rojo": "El margen operativo es bajo o insuficiente.",
        },
        "action_suggested": "Revisar precios, mix de ventas, costos directos, gastos operativos y productividad.",
    },
    "asset_turnover": {
        "direction": "higher_is_better",
        "format": "ratio",
        "diagnostic_by_status": {
            "Verde": "La empresa genera ventas relevantes en relación con sus activos.",
            "Amarillo": "La rotación de activos es moderada.",
            "Rojo": "La rotación de activos es baja.",
        },
        "action_suggested": "Analizar productividad de activos, capacidad ociosa y eficiencia comercial.",
    },
    "roi": {
        "direction": "higher_is_better",
        "format": "percent",
        "diagnostic_by_status": {
            "Verde": "El retorno sobre la inversión supera el umbral objetivo.",
            "Amarillo": "El retorno sobre la inversión es moderado.",
            "Rojo": "El retorno sobre la inversión es bajo.",
        },
        "action_suggested": "Evaluar retorno por unidad de negocio, proyectos, activos e inversión comprometida.",
    },
    "roa": {
        "direction": "higher_is_better",
        "format": "percent",
        "diagnostic_by_status": {
            "Verde": "La rentabilidad sobre activos es saludable.",
            "Amarillo": "La rentabilidad sobre activos es moderada.",
            "Rojo": "La rentabilidad sobre activos es baja.",
        },
        "action_suggested": "Mejorar margen neto y rotación de activos.",
    },
    "roe": {
        "direction": "higher_is_better",
        "format": "percent",
        "diagnostic_by_status": {
            "Verde": "La rentabilidad sobre patrimonio supera el umbral objetivo.",
            "Amarillo": "La rentabilidad patrimonial es moderada.",
            "Rojo": "La rentabilidad patrimonial es baja.",
        },
        "action_suggested": "Analizar margen neto, rotación de activos y apalancamiento financiero bajo enfoque DuPont.",
    },
    "current_ratio": {
        "direction": "higher_is_better",
        "format": "ratio",
        "diagnostic_by_status": {
            "Verde": "La liquidez corriente muestra capacidad de cubrir obligaciones de corto plazo.",
            "Amarillo": "La liquidez corriente es aceptable, pero requiere seguimiento.",
            "Rojo": "La liquidez corriente es baja.",
        },
        "action_suggested": "Revisar caja, cobranzas, vencimientos de pasivos y capital de trabajo.",
    },
    "quick_ratio": {
        "direction": "higher_is_better",
        "format": "ratio",
        "diagnostic_by_status": {
            "Verde": "La prueba ácida indica buena liquidez sin depender de inventarios.",
            "Amarillo": "La prueba ácida es moderada.",
            "Rojo": "La prueba ácida es baja.",
        },
        "action_suggested": "Fortalecer caja y cuentas por cobrar, reduciendo dependencia de inventarios.",
    },
    "cash_ratio": {
        "direction": "higher_is_better",
        "format": "ratio",
        "diagnostic_by_status": {
            "Verde": "La cobertura inmediata con efectivo es adecuada.",
            "Amarillo": "La cobertura inmediata con efectivo es limitada.",
            "Rojo": "La cobertura inmediata con efectivo es baja.",
        },
        "action_suggested": "Definir caja mínima operativa y política de liquidez inmediata.",
    },
    "ocf_to_current_liabilities": {
        "direction": "higher_is_better",
        "format": "percent",
        "diagnostic_by_status": {
            "Verde": "El flujo operativo cubre una proporción saludable del pasivo corriente.",
            "Amarillo": "La cobertura del pasivo corriente con flujo operativo es moderada.",
            "Rojo": "La cobertura del pasivo corriente con flujo operativo es baja.",
        },
        "action_suggested": "Mejorar conversión de resultados en caja operativa y revisar vencimientos de corto plazo.",
    },
    "debt_index": {
        "direction": "lower_is_better",
        "format": "ratio",
        "diagnostic_by_status": {
            "Verde": "La deuda en relación con patrimonio se mantiene controlada.",
            "Amarillo": "El endeudamiento patrimonial es moderado.",
            "Rojo": "El endeudamiento patrimonial es elevado.",
        },
        "action_suggested": "Revisar estructura de financiamiento, deuda financiera y patrimonio.",
    },
    "interest_coverage": {
        "direction": "higher_is_better",
        "format": "ratio",
        "diagnostic_by_status": {
            "Verde": "La empresa cubre cómodamente sus gastos financieros.",
            "Amarillo": "La cobertura de gastos financieros es moderada.",
            "Rojo": "La cobertura de gastos financieros es baja.",
        },
        "action_suggested": "Evaluar costo financiero, refinanciación y mejora de resultado operativo.",
    },
    "debt_to_ebitda": {
        "direction": "lower_is_better",
        "format": "ratio",
        "diagnostic_by_status": {
            "Verde": "La deuda en relación con EBITDA se encuentra en rango razonable.",
            "Amarillo": "La deuda sobre EBITDA requiere seguimiento.",
            "Rojo": "La deuda sobre EBITDA es elevada.",
        },
        "action_suggested": "Monitorear deuda financiera, EBITDA y capacidad real de repago.",
    },
}

for _kpi in KPI_CATALOG:
    _metadata = KPI_EXTENDED_METADATA.get(_kpi.get("code"), {})
    _kpi.update(_metadata)

