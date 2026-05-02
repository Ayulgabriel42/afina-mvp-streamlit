from datetime import datetime


DIMENSION_ORDER = [
    "Estructura de inversión",
    "Capital de trabajo",
    "Rentabilidad",
    "Fluidez financiera",
    "Equilibrio financiero",
]


def safe_text(value, default="N/D"):
    if value is None:
        return default

    value = str(value).strip()

    if value == "":
        return default

    return value


def markdown_escape(value):
    value = safe_text(value)
    return value.replace("|", "\\|").replace("\n", " ")


def semaforo_icon(status):
    status = safe_text(status, "").lower()

    if status == "verde":
        return "🟢 Verde"

    if status == "amarillo":
        return "🟡 Amarillo"

    if status == "rojo":
        return "🔴 Rojo"

    if status == "sin datos":
        return "🔵 Sin datos"

    return safe_text(status)


def dimension_risk_reading(dimension):
    name = dimension.get("dimension", "")
    score = dimension.get("score", 0)
    status = dimension.get("estado_dimension", "N/D")
    red = dimension.get("rojos", 0)
    yellow = dimension.get("amarillos", 0)
    no_data = dimension.get("sin_datos", 0)

    if score >= 75:
        base = f"La dimensión {name} presenta una condición sólida, con predominio de indicadores saludables."
    elif score >= 50:
        base = f"La dimensión {name} muestra una condición moderada, con señales favorables pero también indicadores que requieren seguimiento."
    elif score >= 30:
        base = f"La dimensión {name} se encuentra bajo observación, con riesgos que pueden afectar la gestión financiera si no se monitorean."
    else:
        base = f"La dimensión {name} presenta una condición crítica dentro del análisis FP&A, con indicadores que requieren revisión prioritaria."

    detail = f" Score de dimensión: {score}%. Estado: {status}."

    if red > 0:
        detail += f" Se identifican {red} indicador(es) en rojo."

    if yellow > 0:
        detail += f" Hay {yellow} indicador(es) en amarillo que requieren seguimiento."

    if no_data > 0:
        detail += f" Además, existen {no_data} indicador(es) sin datos suficientes."

    return base + detail


def dimension_recommendation(dimension):
    name = dimension.get("dimension", "")

    recommendations = {
        "Estructura de inversión": (
            "Revisar la evolución de pasivos, patrimonio y deuda financiera para asegurar que el crecimiento "
            "del negocio no dependa excesivamente de financiamiento externo."
        ),
        "Capital de trabajo": (
            "Priorizar acciones sobre inventarios, cuentas por cobrar y ciclo de caja. La reducción de días "
            "inmovilizados puede liberar liquidez operativa sin necesidad de aumentar deuda."
        ),
        "Rentabilidad": (
            "Analizar margen operativo, eficiencia de activos y retorno sobre patrimonio. La mejora de rentabilidad "
            "debe combinar gestión de costos, productividad comercial y uso eficiente de activos."
        ),
        "Fluidez financiera": (
            "Complementar el análisis de liquidez estática con generación real de flujo operativo. Una empresa puede "
            "mostrar ratios de liquidez favorables y, aun así, presentar presión de caja si el flujo operativo es débil."
        ),
        "Equilibrio financiero": (
            "Monitorear deuda, EBITDA y cobertura de gastos financieros. El objetivo es sostener capacidad de pago "
            "sin comprometer flexibilidad financiera futura."
        ),
    }

    return recommendations.get(
        name,
        "Revisar los indicadores principales de la dimensión y validar su impacto sobre la gestión financiera."
    )


def build_traceability_text(kpis):
    sources = []
    sheets = []
    accounts = []

    for kpi in kpis:
        trace = kpi.get("trazabilidad", {}) or {}

        for key in ["fuente_numerador", "fuente_denominador"]:
            value = trace.get(key)
            if value and value not in sources:
                sources.append(value)

        for key in ["hoja_numerador", "hoja_denominador"]:
            value = trace.get(key)
            if value and value not in sheets:
                sheets.append(value)

        for key in ["cuenta_numerador", "cuenta_denominador"]:
            value = trace.get(key)
            if value and value not in accounts:
                accounts.append(value)

    sources_text = ", ".join(sources) if sources else "N/D"
    sheets_text = ", ".join(sheets) if sheets else "N/D"
    accounts_text = ", ".join(accounts[:8]) if accounts else "N/D"

    if len(accounts) > 8:
        accounts_text += ", entre otras"

    return {
        "sources": sources_text,
        "sheets": sheets_text,
        "accounts": accounts_text,
    }


def build_scorecard_table(kpis):
    lines = []
    lines.append("| Indicador | Valor actual | Histórico | Tendencia | Semáforo | Diagnóstico automatizado |")
    lines.append("|---|---:|---:|---|---|---|")

    for kpi in kpis:
        name = markdown_escape(kpi.get("nombre"))
        value = markdown_escape(kpi.get("valor_formateado"))
        status = markdown_escape(semaforo_icon(kpi.get("estado")))
        reading = markdown_escape(kpi.get("lectura"))

        # Por ahora no usamos histórico real hasta implementar series multi-período.
        historical = "N/D"
        trend = "Pendiente serie histórica"

        if kpi.get("codigo_kpi") == "cash_conversion_cycle":
            trend = "Validar metodología"

        lines.append(
            f"| {name} | {value} | {historical} | {trend} | {status} | {reading} |"
        )

    return "\n".join(lines)


def build_alerts_table(alerts):
    if not alerts:
        return "No se identificaron alertas críticas en el snapshot financiero."

    lines = []
    lines.append("| Prioridad | Dimensión | KPI | Valor | Impacto / mensaje |")
    lines.append("|---|---|---|---:|---|")

    for alert in alerts:
        severity = markdown_escape(alert.get("severidad"))
        dimension = markdown_escape(alert.get("dimension"))
        kpi = markdown_escape(alert.get("kpi"))
        value = markdown_escape(alert.get("valor"))
        message = markdown_escape(alert.get("mensaje"))

        lines.append(f"| {severity} | {dimension} | {kpi} | {value} | {message} |")

    return "\n".join(lines)


def build_data_quality_section(snapshot):
    warnings = snapshot.get("data_quality_warnings", []) or []
    financial_items = snapshot.get("financial_items", {}) or {}
    pending_items = financial_items.get("pendientes", []) or []

    lines = []

    if pending_items:
        lines.append("### Partidas pendientes")
        lines.append("")
        lines.append("| Código interno | Partida | Impacto |")
        lines.append("|---|---|---|")

        for item in pending_items:
            code = markdown_escape(item.get("Código interno"))
            partida = markdown_escape(item.get("Partida FP&A"))
            impact = "Puede impedir el cálculo de KPIs asociados o limitar la interpretación financiera."
            lines.append(f"| {code} | {partida} | {impact} |")

        lines.append("")

    if warnings:
        lines.append("### Advertencias de calidad de datos")
        lines.append("")
        lines.append("| Tipo | Severidad | Elemento | Mensaje |")
        lines.append("|---|---|---|---|")

        for warning in warnings:
            warning_type = markdown_escape(warning.get("tipo"))
            severity = markdown_escape(warning.get("severidad"))
            element = markdown_escape(
                warning.get("codigo_interno")
                or warning.get("codigo_kpi")
                or warning.get("kpi")
                or warning.get("partida")
            )
            message = markdown_escape(warning.get("mensaje"))

            lines.append(f"| {warning_type} | {severity} | {element} | {message} |")

        lines.append("")

    if not lines:
        lines.append("No se identificaron advertencias relevantes de calidad de datos.")

    return "\n".join(lines)


def build_executive_summary(snapshot):
    context = snapshot.get("analysis_context", {}) or {}
    health = snapshot.get("health_score", {}) or {}
    kpi_summary = snapshot.get("kpi_summary", {}) or {}

    company = safe_text(context.get("company_name"), "Empresa analizada")
    period = safe_text(context.get("period"), "Período no especificado")
    industry = safe_text(context.get("industry"), "Industria no especificada")
    score = safe_text(health.get("score"))
    label = safe_text(health.get("label"))

    total = kpi_summary.get("total", 0)
    calculated = kpi_summary.get("calculados", 0)
    pending = kpi_summary.get("pendientes", 0)

    return (
        f"El presente informe analiza la situación financiera de **{company}** para el período **{period}**, "
        f"correspondiente a la industria **{industry}**, utilizando la metodología FP&A de AFINA.\n\n"
        f"El score financiero general obtenido es **{score}%**, clasificado como **{label}**. "
        f"El motor determinístico calculó **{calculated} de {total} KPIs**, quedando **{pending} indicador(es)** "
        f"pendiente(s) por falta de información suficiente o trazabilidad confiable.\n\n"
        "La lectura global debe interpretarse como una combinación entre liquidez, rentabilidad, capital de trabajo, "
        "estructura financiera y equilibrio de deuda. AFINA no reemplaza la revisión profesional, pero permite "
        "identificar de manera automatizada focos de atención, riesgos y oportunidades de mejora."
    )


def build_recommendations(snapshot):
    dimensions = snapshot.get("dimensions_fpa", []) or []
    alerts = snapshot.get("alerts", []) or []

    lines = []
    lines.append("1. **Priorizar la gestión del capital de trabajo:** revisar inventarios, cuentas por cobrar y ciclo de caja para liberar liquidez operativa.")
    lines.append("2. **Validar la calidad de datos contables:** completar partidas pendientes y revisar partidas detectadas sin valor numérico.")
    lines.append("3. **Analizar rentabilidad por línea o unidad de negocio:** profundizar margen, rotación de activos y retorno sobre patrimonio.")
    lines.append("4. **Separar liquidez estática de generación real de caja:** complementar ratios de liquidez con flujo operativo recurrente.")
    lines.append("5. **Monitorear endeudamiento y EBITDA:** controlar la evolución de deuda financiera relativa a capacidad de generación operativa.")

    critical_dimensions = [
        dim.get("dimension")
        for dim in dimensions
        if dim.get("score", 0) < 50
    ]

    if critical_dimensions:
        joined = ", ".join(critical_dimensions)
        lines.append(f"6. **Crear plan de acción por dimensión crítica:** enfocar seguimiento ejecutivo en {joined}.")

    if alerts:
        lines.append("7. **Implementar seguimiento periódico de alertas:** convertir los KPIs rojos en tablero de control mensual.")

    return "\n".join(lines)



def compact_ai_commentary_for_report(ai_insights, max_words=380):
    """
    Limpia y limita el bloque IA para que funcione como comentario consultivo,
    no como informe paralelo completo. Si el texto viene cortado, conserva
    solo hasta la última oración completa.
    """
    if not ai_insights:
        return ""

    text = str(ai_insights).strip()

    words = text.split()
    if len(words) > max_words:
        text = " ".join(words[:max_words]).rstrip()

    # Si el texto no termina en puntuación final, cortamos en la última oración completa.
    if text and text[-1] not in ".!?":
        last_dot = max(text.rfind("."), text.rfind("!"), text.rfind("?"))
        if last_dot > 120:
            text = text[:last_dot + 1]
        else:
            text = text.rstrip() + "."

    return text

def build_fpa_report_markdown(snapshot, ai_insights=None):
    """
    Construye un informe FP&A completo en Markdown.
    Este template es parametrizable y reutilizable por cliente, industria y período.
    """
    context = snapshot.get("analysis_context", {}) or {}
    health = snapshot.get("health_score", {}) or {}
    kpi_summary = snapshot.get("kpi_summary", {}) or {}
    dimensions = snapshot.get("dimensions_fpa", []) or []
    alerts = snapshot.get("alerts", []) or []

    company = safe_text(context.get("company_name"), "Empresa analizada")
    source_file = safe_text(context.get("source_file"), "Archivo no especificado")
    industry = safe_text(context.get("industry"), "Industria no especificada")
    period = safe_text(context.get("period"), "Período no especificado")
    analysis_type = safe_text(context.get("analysis_type"), "No especificado")
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = []

    # Portada
    lines.append(f"# Informe financiero FP&A — {company}")
    lines.append("")
    lines.append("## Portada")
    lines.append("")
    lines.append(f"**Cliente:** {company}  ")
    lines.append(f"**Industria:** {industry}  ")
    lines.append(f"**Período analizado:** {period}  ")
    lines.append(f"**Tipo de análisis:** {analysis_type}  ")
    lines.append(f"**Archivo fuente:** {source_file}  ")
    lines.append(f"**Fecha de generación:** {generated_at}  ")
    lines.append("")
    lines.append("**Propósito del informe:** presentar un diagnóstico financiero ejecutivo basado en metodología FP&A, "
                 "integrando KPIs calculados automáticamente, trazabilidad de datos, semáforos de desempeño y recomendaciones estratégicas.")
    lines.append("")
    lines.append("**Metodología:** AFINA procesa estados financieros, detecta partidas clave, calcula indicadores FP&A y genera "
                 "diagnósticos automatizados basados en reglas y asistencia de IA.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Resumen ejecutivo
    lines.append("## 1. Resumen ejecutivo")
    lines.append("")
    lines.append(build_executive_summary(snapshot))
    lines.append("")

    lines.append("### Score financiero general")
    lines.append("")
    lines.append("| Métrica | Resultado |")
    lines.append("|---|---:|")
    lines.append(f"| Score financiero | {safe_text(health.get('score'))}% |")
    lines.append(f"| Estado general | {safe_text(health.get('label'))} |")
    lines.append(f"| KPIs totales | {safe_text(kpi_summary.get('total'))} |")
    lines.append(f"| KPIs calculados | {safe_text(kpi_summary.get('calculados'))} |")
    lines.append(f"| KPIs pendientes | {safe_text(kpi_summary.get('pendientes'))} |")
    lines.append(f"| Cobertura del catálogo | {safe_text(kpi_summary.get('cobertura'))}% |")
    lines.append("")

    # Diagnóstico por dimensiones
    lines.append("## 2. Diagnóstico financiero por dimensiones FP&A")
    lines.append("")

    sorted_dimensions = sorted(
        dimensions,
        key=lambda d: DIMENSION_ORDER.index(d.get("dimension")) if d.get("dimension") in DIMENSION_ORDER else 99
    )

    for index, dimension in enumerate(sorted_dimensions, start=1):
        name = safe_text(dimension.get("dimension"))
        score = safe_text(dimension.get("score"))
        status = safe_text(dimension.get("estado_dimension"))
        kpis = dimension.get("kpis", []) or []
        trace = build_traceability_text(kpis)

        lines.append(f"### 2.{index}. {name}")
        lines.append("")
        lines.append(f"**Score de dimensión:** {score}%  ")
        lines.append(f"**Estado:** {status}  ")
        lines.append(f"**KPIs calculados:** {safe_text(dimension.get('kpis_calculados'))} de {safe_text(dimension.get('total_kpis'))}  ")
        lines.append("")

        lines.append("#### Trazabilidad del dato")
        lines.append("")
        lines.append(f"- **Fuentes contables utilizadas:** {trace['sources']}")
        lines.append(f"- **Hojas utilizadas:** {trace['sheets']}")
        lines.append(f"- **Cuentas detectadas principales:** {trace['accounts']}")
        lines.append("")

        lines.append("#### Scorecard de indicadores")
        lines.append("")
        lines.append(build_scorecard_table(kpis))
        lines.append("")

        lines.append("#### Diagnóstico automatizado")
        lines.append("")
        lines.append(dimension_risk_reading(dimension))
        lines.append("")

        lines.append("#### Comentario analítico consultivo")
        lines.append("")
        lines.append(dimension_recommendation(dimension))
        lines.append("")

    # Alertas
    lines.append("## 3. Alertas prioritarias")
    lines.append("")
    lines.append(build_alerts_table(alerts))
    lines.append("")

    # IA complementaria breve
    if ai_insights:
        lines.append("## 4. Síntesis consultiva generada por IA")
        lines.append("")
        lines.append(
            "Este bloque complementa el informe estructurado de AFINA con una lectura ejecutiva breve generada "
            "por IA a partir del JSON financiero estándar. La IA no recalcula KPIs; solo interpreta resultados "
            "ya calculados y trazables."
        )
        lines.append("")
        lines.append(compact_ai_commentary_for_report(ai_insights))
        lines.append("")
        conclusion_number = 5
    else:
        conclusion_number = 4

    # Conclusiones
    lines.append(f"## {conclusion_number}. Conclusiones")
    lines.append("")
    lines.append(
        "El análisis permite identificar una visión integrada de la salud financiera de la empresa. "
        "Las dimensiones con mejor desempeño deben preservarse mediante seguimiento periódico, mientras que "
        "las dimensiones críticas deben transformarse en planes de acción medibles."
    )
    lines.append("")
    lines.append(
        "El valor diferencial de AFINA reside en combinar cálculo determinístico, trazabilidad de datos, semáforos "
        "de desempeño y generación automatizada de comentarios ejecutivos."
    )
    lines.append("")

    # Recomendaciones
    lines.append(f"## {conclusion_number + 1}. Recomendaciones estratégicas")
    lines.append("")
    lines.append(build_recommendations(snapshot))
    lines.append("")

    # Limitaciones
    lines.append(f"## {conclusion_number + 2}. Limitaciones metodológicas y calidad de datos")
    lines.append("")
    lines.append(build_data_quality_section(snapshot))
    lines.append("")

    notes = snapshot.get("methodological_notes", []) or []
    if notes:
        lines.append("### Notas metodológicas")
        lines.append("")
        for note in notes:
            lines.append(f"- {safe_text(note)}")
        lines.append("")

    # Próximos pasos
    lines.append(f"## {conclusion_number + 3}. Próximos pasos sugeridos")
    lines.append("")
    lines.append("1. Validar las partidas detectadas con el equipo contable o financiero.")
    lines.append("2. Incorporar análisis histórico para completar columnas de tendencia.")
    lines.append("3. Definir thresholds por industria para mejorar precisión del semáforo.")
    lines.append("4. Integrar generación de PDF y Word desde este template Markdown.")
    lines.append("5. Incorporar chatbot contextual sobre el informe y el JSON financiero.")
    lines.append("6. Preparar escenarios y proyecciones financieras automatizadas.")
    lines.append("")

    # Disclaimer
    lines.append("---")
    lines.append("")
    lines.append("## Disclaimer")
    lines.append("")
    lines.append(safe_text(snapshot.get("disclaimer")))
    lines.append("")

    return "\n".join(lines)
