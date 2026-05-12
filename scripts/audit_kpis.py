from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.kpi_catalog import KPI_CATALOG, DIMENSION_ORDER
from src.thresholds import (
    get_available_industries,
    get_threshold_config,
    evaluate_kpi_status,
)


REQUIRED_KPI_FIELDS = [
    "srs_code",
    "code",
    "name",
    "dimension",
    "formula",
    "unit",
    "required_items",
    "order",
    "direction",
    "format",
    "diagnostic_by_status",
    "action_suggested",
]


EXPECTED_SRS_CODES = {f"K-{i:02d}" for i in range(1, 20)}


def audit_catalog():
    issues = []

    codes = [kpi.get("code") for kpi in KPI_CATALOG]
    srs_codes = {kpi.get("srs_code") for kpi in KPI_CATALOG}

    if len(KPI_CATALOG) != 19:
        issues.append(f"Se esperaban 19 KPIs núcleo, pero hay {len(KPI_CATALOG)}.")

    missing_srs = sorted(EXPECTED_SRS_CODES - srs_codes)
    extra_srs = sorted(srs_codes - EXPECTED_SRS_CODES)

    if missing_srs:
        issues.append(f"Faltan códigos SRS: {', '.join(missing_srs)}.")

    if extra_srs:
        issues.append(f"Códigos SRS no esperados en núcleo K-01 a K-19: {', '.join(extra_srs)}.")

    if len(codes) != len(set(codes)):
        issues.append("Hay códigos KPI duplicados.")

    for kpi in KPI_CATALOG:
        code = kpi.get("code", "SIN_CODIGO")

        for field in REQUIRED_KPI_FIELDS:
            value = kpi.get(field)
            if value in [None, "", [], {}]:
                issues.append(f"{code}: falta campo obligatorio '{field}'.")

        if kpi.get("dimension") not in DIMENSION_ORDER:
            issues.append(f"{code}: dimensión no reconocida: {kpi.get('dimension')}.")

        if kpi.get("unit") not in ["percentage", "ratio", "days"]:
            issues.append(f"{code}: unidad no estándar: {kpi.get('unit')}.")

        if kpi.get("direction") not in ["higher_is_better", "lower_is_better"]:
            issues.append(f"{code}: direction inválida: {kpi.get('direction')}.")

        diagnostics = kpi.get("diagnostic_by_status", {})
        for status in ["Verde", "Amarillo", "Rojo"]:
            if not diagnostics.get(status):
                issues.append(f"{code}: falta diagnóstico para estado {status}.")

    return issues


def audit_thresholds():
    issues = []
    industries = get_available_industries()

    for industry in industries:
        for kpi in KPI_CATALOG:
            code = kpi["code"]
            config = get_threshold_config(code, industry=industry)

            if not config:
                issues.append(f"{industry} / {code}: falta threshold.")
                continue

            direction = config.get("direction")

            if direction == "lower_is_better":
                if "green_max" not in config or "yellow_max" not in config:
                    issues.append(f"{industry} / {code}: faltan green_max/yellow_max.")
                elif config["green_max"] > config["yellow_max"]:
                    issues.append(f"{industry} / {code}: green_max no puede ser mayor a yellow_max.")

                sample_green = config.get("green_max")
                sample_yellow = config.get("yellow_max")
                sample_red = config.get("yellow_max", 0) + 999

            elif direction == "higher_is_better":
                if "green_min" not in config or "yellow_min" not in config:
                    issues.append(f"{industry} / {code}: faltan green_min/yellow_min.")
                elif config["green_min"] < config["yellow_min"]:
                    issues.append(f"{industry} / {code}: green_min no puede ser menor a yellow_min.")

                sample_green = config.get("green_min")
                sample_yellow = config.get("yellow_min")
                sample_red = config.get("yellow_min", 0) - 999

            else:
                issues.append(f"{industry} / {code}: direction inválida o faltante.")
                continue

            for sample in [sample_green, sample_yellow, sample_red]:
                result = evaluate_kpi_status(code, sample, industry=industry)
                if not isinstance(result, dict):
                    issues.append(f"{industry} / {code}: evaluate_kpi_status no devuelve dict.")
                    continue

                for field in ["estado", "color", "lectura"]:
                    if field not in result:
                        issues.append(f"{industry} / {code}: respuesta sin campo '{field}'.")

    return issues


def main():
    catalog_issues = audit_catalog()
    threshold_issues = audit_thresholds()
    issues = catalog_issues + threshold_issues

    print("\nAFINA KPI AUDIT")
    print("=" * 60)
    print(f"KPIs núcleo detectados: {len(KPI_CATALOG)}")
    print(f"Industrias configuradas: {len(get_available_industries())}")
    print(f"Campos obligatorios auditados: {len(REQUIRED_KPI_FIELDS)}")
    print(f"Issues encontrados: {len(issues)}")
    print("=" * 60)

    if issues:
        print("\nDETALLE DE OBSERVACIONES:")
        for issue in issues:
            print(f"- {issue}")
        sys.exit(1)

    print("\nOK: Catálogo KPI y thresholds por industria completos.")
    print("El motor financiero queda listo para alimentar dashboard, PDF, Word, insights y chatbot.\n")


if __name__ == "__main__":
    main()
