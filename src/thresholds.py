"""
Thresholds oficiales iniciales para AFINA.

Este módulo centraliza la evaluación de semáforos por KPI e industria.
Mantiene la misma salida que esperaba kpi_engine.py:
{
    "estado": "Verde" | "Amarillo" | "Rojo" | "Sin datos" | "Sin umbral",
    "color": "green" | "yellow" | "red" | "gray" | "blue",
    "lectura": "...",
}

Los umbrales son parametrizables y pueden ajustarse luego desde un panel admin.
"""

from copy import deepcopy


DEFAULT_INDUSTRY = "Sector Químico"

AVAILABLE_INDUSTRIES = [
    "General",
    "Sector Químico",
    "Manufactura",
    "Retail/Comercio",
    "SaaS/Tecnología",
    "Servicios Financieros",
    "Salud/Farmacia",
]

INDUSTRY_ALIASES = {
    "general": "General",
    "sector quimico": "Sector Químico",
    "sector químico": "Sector Químico",
    "quimico": "Sector Químico",
    "químico": "Sector Químico",
    "manufactura": "Manufactura",
    "retail": "Retail/Comercio",
    "retail/comercio": "Retail/Comercio",
    "retail / comercio": "Retail/Comercio",
    "saas / tecnologia": "SaaS/Tecnología",
    "saas / tecnología": "SaaS/Tecnología",
    "salud / farmacia": "Salud/Farmacia",
    "comercio": "Retail/Comercio",
    "saas": "SaaS/Tecnología",
    "saas/tecnologia": "SaaS/Tecnología",
    "saas/tecnología": "SaaS/Tecnología",
    "tecnologia": "SaaS/Tecnología",
    "tecnología": "SaaS/Tecnología",
    "servicios financieros": "Servicios Financieros",
    "financiero": "Servicios Financieros",
    "salud": "Salud/Farmacia",
    "salud/farmacia": "Salud/Farmacia",
    "farmacia": "Salud/Farmacia",
}


BASE_THRESHOLDS = {
    # 1. Estructura de inversión
    "debt_ratio": {
        "direction": "lower_is_better",
        "green_max": 0.50,
        "yellow_max": 0.65,
        "readings": {
            "Verde": "El endeudamiento sobre activos se mantiene en un rango saludable.",
            "Amarillo": "El endeudamiento sobre activos es moderado y requiere seguimiento.",
            "Rojo": "El endeudamiento sobre activos es elevado y puede limitar flexibilidad financiera.",
        },
        "action": "Revisar composición de pasivos, estructura de deuda y capacidad de generación de caja.",
    },
    "debt_to_equity": {
        "direction": "lower_is_better",
        "green_max": 1.50,
        "yellow_max": 2.50,
        "readings": {
            "Verde": "La relación deuda/patrimonio se mantiene controlada.",
            "Amarillo": "La relación deuda/patrimonio es moderada y requiere monitoreo.",
            "Rojo": "La relación deuda/patrimonio es elevada y puede indicar dependencia de financiamiento externo.",
        },
        "action": "Evaluar capitalización, refinanciación y equilibrio entre deuda y patrimonio.",
    },
    "equity_multiplier": {
        "direction": "lower_is_better",
        "green_max": 3.50,
        "yellow_max": 4.50,
        "readings": {
            "Verde": "El apalancamiento financiero se encuentra dentro de un rango razonable.",
            "Amarillo": "El apalancamiento financiero requiere seguimiento.",
            "Rojo": "El apalancamiento financiero es elevado y aumenta la sensibilidad ante caídas de rentabilidad.",
        },
        "action": "Analizar si el crecimiento de activos se sostiene con una estructura patrimonial adecuada.",
    },

    # 2. Capital de trabajo
    "inventory_days": {
        "direction": "lower_is_better",
        "green_max": 90,
        "yellow_max": 120,
        "readings": {
            "Verde": "La permanencia de inventarios es razonable.",
            "Amarillo": "La permanencia de inventarios es moderada y puede afectar capital de trabajo.",
            "Rojo": "La permanencia de inventarios es elevada y puede inmovilizar caja operativa.",
        },
        "action": "Revisar rotación de stock, obsolescencia, niveles mínimos y planificación de compras.",
    },
    "receivables_days": {
        "direction": "lower_is_better",
        "green_max": 65,
        "yellow_max": 90,
        "readings": {
            "Verde": "El plazo promedio de cobro es saludable.",
            "Amarillo": "El plazo promedio de cobro requiere seguimiento.",
            "Rojo": "El plazo promedio de cobro es elevado y puede presionar la liquidez.",
        },
        "action": "Fortalecer gestión de cobranzas, política de crédito y seguimiento de vencimientos.",
    },
    "payables_days": {
        "direction": "higher_is_better",
        "green_min": 65,
        "yellow_min": 45,
        "readings": {
            "Verde": "El plazo promedio de pago favorece la gestión de caja.",
            "Amarillo": "El plazo promedio de pago es aceptable, pero podría optimizarse.",
            "Rojo": "El plazo promedio de pago es bajo y puede presionar la caja.",
        },
        "action": "Negociar mejores plazos con proveedores sin deteriorar relaciones comerciales.",
    },
    "cash_conversion_cycle": {
        "direction": "lower_is_better",
        "green_max": 90,
        "yellow_max": 120,
        "readings": {
            "Verde": "El ciclo de caja es razonable para la operación.",
            "Amarillo": "El ciclo de caja es moderado y puede presionar el capital de trabajo.",
            "Rojo": "El ciclo de caja es elevado y puede tensionar la liquidez operativa.",
        },
        "action": "Reducir días de inventario y cobranza, y optimizar plazos de pago.",
    },

    # 3. Rentabilidad
    "operating_margin": {
        "direction": "higher_is_better",
        "green_min": 0.12,
        "yellow_min": 0.05,
        "readings": {
            "Verde": "El margen operativo muestra una rentabilidad operativa saludable.",
            "Amarillo": "El margen operativo es positivo, pero requiere mejora.",
            "Rojo": "El margen operativo es bajo o insuficiente para sostener la operación con holgura.",
        },
        "action": "Revisar precios, mix de ventas, costos directos, gastos operativos y productividad.",
    },
    "asset_turnover": {
        "direction": "higher_is_better",
        "green_min": 1.25,
        "yellow_min": 0.75,
        "readings": {
            "Verde": "La empresa genera ventas relevantes en relación con sus activos.",
            "Amarillo": "La rotación de activos es moderada.",
            "Rojo": "La rotación de activos es baja y puede indicar activos subutilizados.",
        },
        "action": "Analizar productividad de activos, capacidad ociosa y eficiencia comercial.",
    },
    "roi": {
        "direction": "higher_is_better",
        "green_min": 0.113,
        "yellow_min": 0.05,
        "readings": {
            "Verde": "El retorno sobre la inversión supera el umbral objetivo.",
            "Amarillo": "El retorno sobre la inversión es moderado.",
            "Rojo": "El retorno sobre la inversión es bajo y requiere revisión de rentabilidad.",
        },
        "action": "Evaluar retorno por unidad de negocio, proyectos, activos e inversión comprometida.",
    },
    "roa": {
        "direction": "higher_is_better",
        "green_min": 0.075,
        "yellow_min": 0.03,
        "readings": {
            "Verde": "La rentabilidad sobre activos es saludable.",
            "Amarillo": "La rentabilidad sobre activos es moderada.",
            "Rojo": "La rentabilidad sobre activos es baja y puede indicar baja eficiencia operativa.",
        },
        "action": "Mejorar margen neto y rotación de activos.",
    },
    "roe": {
        "direction": "higher_is_better",
        "green_min": 0.27,
        "yellow_min": 0.10,
        "readings": {
            "Verde": "La rentabilidad sobre patrimonio supera el umbral objetivo.",
            "Amarillo": "La rentabilidad patrimonial es moderada.",
            "Rojo": "La rentabilidad patrimonial es baja y requiere análisis bajo enfoque DuPont.",
        },
        "action": "Analizar margen neto, rotación de activos y apalancamiento financiero.",
    },

    # 4. Fluidez financiera
    "current_ratio": {
        "direction": "higher_is_better",
        "green_min": 1.50,
        "yellow_min": 1.00,
        "readings": {
            "Verde": "La liquidez corriente muestra capacidad de cubrir obligaciones de corto plazo.",
            "Amarillo": "La liquidez corriente es aceptable, pero requiere seguimiento.",
            "Rojo": "La liquidez corriente es baja y puede indicar tensión de corto plazo.",
        },
        "action": "Revisar caja, cobranzas, vencimientos de pasivos y capital de trabajo.",
    },
    "quick_ratio": {
        "direction": "higher_is_better",
        "green_min": 1.00,
        "yellow_min": 0.70,
        "readings": {
            "Verde": "La prueba ácida indica buena liquidez sin depender de inventarios.",
            "Amarillo": "La prueba ácida es moderada.",
            "Rojo": "La prueba ácida es baja y evidencia dependencia de inventarios para cubrir pasivos.",
        },
        "action": "Fortalecer caja y cuentas por cobrar, reduciendo dependencia de inventarios.",
    },
    "cash_ratio": {
        "direction": "higher_is_better",
        "green_min": 0.20,
        "yellow_min": 0.10,
        "readings": {
            "Verde": "La cobertura inmediata con efectivo es adecuada.",
            "Amarillo": "La cobertura inmediata con efectivo es limitada.",
            "Rojo": "La cobertura inmediata con efectivo es baja.",
        },
        "action": "Definir caja mínima operativa y política de liquidez inmediata.",
    },
    "ocf_to_current_liabilities": {
        "direction": "higher_is_better",
        "green_min": 0.40,
        "yellow_min": 0.15,
        "readings": {
            "Verde": "El flujo operativo cubre una proporción saludable del pasivo corriente.",
            "Amarillo": "La cobertura del pasivo corriente con flujo operativo es moderada.",
            "Rojo": "La cobertura del pasivo corriente con flujo operativo es baja.",
        },
        "action": "Mejorar conversión de resultados en caja operativa y revisar vencimientos de corto plazo.",
    },

    # 5. Equilibrio financiero
    "debt_index": {
        "direction": "lower_is_better",
        "green_max": 1.50,
        "yellow_max": 2.50,
        "readings": {
            "Verde": "La deuda en relación con patrimonio se mantiene controlada.",
            "Amarillo": "El endeudamiento patrimonial es moderado.",
            "Rojo": "El endeudamiento patrimonial es elevado.",
        },
        "action": "Revisar estructura de financiamiento, deuda financiera y patrimonio.",
    },
    "interest_coverage": {
        "direction": "higher_is_better",
        "green_min": 4.50,
        "yellow_min": 2.00,
        "readings": {
            "Verde": "La empresa cubre cómodamente sus gastos financieros con resultado operativo.",
            "Amarillo": "La cobertura de gastos financieros es moderada.",
            "Rojo": "La cobertura de gastos financieros es baja y expone riesgo financiero.",
        },
        "action": "Evaluar costo financiero, refinanciación y mejora de resultado operativo.",
    },
    "debt_to_ebitda": {
        "direction": "lower_is_better",
        "green_max": 3.00,
        "yellow_max": 4.00,
        "readings": {
            "Verde": "La deuda en relación con EBITDA se encuentra en rango razonable.",
            "Amarillo": "La deuda sobre EBITDA requiere seguimiento.",
            "Rojo": "La deuda sobre EBITDA es elevada o el EBITDA no sostiene adecuadamente la deuda.",
        },
        "action": "Monitorear deuda financiera, EBITDA y capacidad real de repago.",
    },
}


INDUSTRY_OVERRIDES = {
    "Sector Químico": {
        "inventory_days": {"green_max": 105, "yellow_max": 140},
        "receivables_days": {"green_max": 70, "yellow_max": 95},
        "cash_conversion_cycle": {"green_max": 105, "yellow_max": 140},
        "operating_margin": {"green_min": 0.12, "yellow_min": 0.06},
        "asset_turnover": {"green_min": 1.10, "yellow_min": 0.70},
    },
    "Manufactura": {
        "inventory_days": {"green_max": 95, "yellow_max": 130},
        "receivables_days": {"green_max": 70, "yellow_max": 95},
        "cash_conversion_cycle": {"green_max": 100, "yellow_max": 135},
        "asset_turnover": {"green_min": 1.00, "yellow_min": 0.65},
        "operating_margin": {"green_min": 0.10, "yellow_min": 0.05},
    },
    "Retail/Comercio": {
        "inventory_days": {"green_max": 60, "yellow_max": 90},
        "receivables_days": {"green_max": 45, "yellow_max": 70},
        "payables_days": {"green_min": 55, "yellow_min": 35},
        "cash_conversion_cycle": {"green_max": 60, "yellow_max": 90},
        "asset_turnover": {"green_min": 1.80, "yellow_min": 1.10},
        "operating_margin": {"green_min": 0.08, "yellow_min": 0.03},
    },
    "SaaS/Tecnología": {
        "debt_ratio": {"green_max": 0.40, "yellow_max": 0.60},
        "debt_to_equity": {"green_max": 1.00, "yellow_max": 2.00},
        "debt_index": {"green_max": 1.00, "yellow_max": 2.00},
        "inventory_days": {"green_max": 30, "yellow_max": 60},
        "receivables_days": {"green_max": 60, "yellow_max": 85},
        "cash_conversion_cycle": {"green_max": 60, "yellow_max": 90},
        "operating_margin": {"green_min": 0.10, "yellow_min": 0.00},
        "asset_turnover": {"green_min": 0.70, "yellow_min": 0.35},
        "current_ratio": {"green_min": 1.30, "yellow_min": 0.90},
    },
    "Servicios Financieros": {
        "debt_ratio": {"green_max": 0.75, "yellow_max": 0.88},
        "debt_to_equity": {"green_max": 4.00, "yellow_max": 7.00},
        "debt_index": {"green_max": 4.00, "yellow_max": 7.00},
        "equity_multiplier": {"green_max": 8.00, "yellow_max": 12.00},
        "operating_margin": {"green_min": 0.18, "yellow_min": 0.08},
        "roe": {"green_min": 0.18, "yellow_min": 0.08},
        "roa": {"green_min": 0.015, "yellow_min": 0.005},
        "current_ratio": {"green_min": 1.10, "yellow_min": 0.90},
    },
    "Salud/Farmacia": {
        "inventory_days": {"green_max": 75, "yellow_max": 105},
        "receivables_days": {"green_max": 75, "yellow_max": 105},
        "cash_conversion_cycle": {"green_max": 95, "yellow_max": 130},
        "operating_margin": {"green_min": 0.10, "yellow_min": 0.04},
        "asset_turnover": {"green_min": 1.10, "yellow_min": 0.70},
        "current_ratio": {"green_min": 1.40, "yellow_min": 1.00},
    },
}


def normalize_industry(industry):
    raw = str(industry or DEFAULT_INDUSTRY).strip()

    # Normalización tolerante para nombres provenientes del selector de Streamlit.
    # Ejemplos:
    # "Retail / Comercio" -> "Retail/Comercio"
    # "SaaS / Tecnología" -> "SaaS/Tecnología"
    # "Salud / Farmacia" -> "Salud/Farmacia"
    compact = " ".join(raw.split())
    compact = compact.replace(" / ", "/").replace(" /", "/").replace("/ ", "/")

    key = compact.lower()

    return INDUSTRY_ALIASES.get(
        key,
        compact if compact in AVAILABLE_INDUSTRIES else DEFAULT_INDUSTRY
    )


def get_available_industries():
    return list(AVAILABLE_INDUSTRIES)


def _merge_config(base, override):
    config = deepcopy(base or {})
    config.update(override or {})
    return config


def get_threshold_config(kpi_code, industry=DEFAULT_INDUSTRY):
    normalized = normalize_industry(industry)
    base = BASE_THRESHOLDS.get(kpi_code)

    if not base:
        return None

    override = INDUSTRY_OVERRIDES.get(normalized, {}).get(kpi_code, {})
    return _merge_config(base, override)


def _status_payload(status, config, industry):
    color_by_status = {
        "Verde": "green",
        "Amarillo": "yellow",
        "Rojo": "red",
        "Sin datos": "gray",
        "Sin umbral": "blue",
    }

    readings = config.get("readings", {}) if config else {}

    return {
        "estado": status,
        "color": color_by_status.get(status, "blue"),
        "lectura": readings.get(status, "Indicador calculado sin lectura específica configurada."),
        "accion_sugerida": config.get("action", "") if config else "",
        "threshold_industry": normalize_industry(industry),
        "threshold_direction": config.get("direction", "") if config else "",
    }


def evaluate_kpi_status(kpi_code, value, industry=DEFAULT_INDUSTRY):
    if value is None:
        return {
            "estado": "Sin datos",
            "color": "gray",
            "lectura": "No se pudo calcular el indicador con las partidas disponibles.",
            "accion_sugerida": "Validar extracción de partidas contables requeridas.",
            "threshold_industry": normalize_industry(industry),
            "threshold_direction": "",
        }

    config = get_threshold_config(kpi_code, industry=industry)

    if not config:
        return {
            "estado": "Sin umbral",
            "color": "blue",
            "lectura": "Indicador calculado sin umbral específico configurado.",
            "accion_sugerida": "Definir threshold financiero para este KPI.",
            "threshold_industry": normalize_industry(industry),
            "threshold_direction": "",
        }

    direction = config.get("direction")

    # Caso especial: Deuda/EBITDA negativo suele indicar EBITDA negativo o proxy no interpretable.
    if kpi_code == "debt_to_ebitda" and value < 0:
        return _status_payload("Rojo", config, industry)

    if direction == "lower_is_better":
        if value <= config["green_max"]:
            return _status_payload("Verde", config, industry)
        if value <= config["yellow_max"]:
            return _status_payload("Amarillo", config, industry)
        return _status_payload("Rojo", config, industry)

    if direction == "higher_is_better":
        if value >= config["green_min"]:
            return _status_payload("Verde", config, industry)
        if value >= config["yellow_min"]:
            return _status_payload("Amarillo", config, industry)
        return _status_payload("Rojo", config, industry)

    return {
        "estado": "Sin umbral",
        "color": "blue",
        "lectura": "Indicador calculado, pero la dirección del threshold no está configurada.",
        "accion_sugerida": "Revisar configuración del threshold.",
        "threshold_industry": normalize_industry(industry),
        "threshold_direction": direction or "",
    }
