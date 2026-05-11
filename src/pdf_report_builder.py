import io
import re
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Flowable,
)


AFINA_NAVY = colors.HexColor("#0B1F3A")
AFINA_BLUE = colors.HexColor("#2563EB")
AFINA_CYAN = colors.HexColor("#38BDF8")
AFINA_LIGHT = colors.HexColor("#F8FAFC")
AFINA_SOFT_BLUE = colors.HexColor("#EAF2FF")
AFINA_BORDER = colors.HexColor("#CBD5E1")
AFINA_TEXT = colors.HexColor("#0F172A")
AFINA_MUTED = colors.HexColor("#475569")

AFINA_GREEN = colors.HexColor("#22C55E")
AFINA_YELLOW = colors.HexColor("#F59E0B")
AFINA_RED = colors.HexColor("#EF4444")
AFINA_GRAY = colors.HexColor("#94A3B8")

WHITE = colors.white


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

    text = str(value).strip()

    if not text:
        return default

    replacements = {
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "•": "-",
        "→": "->",
        "×": "x",
        "≥": ">=",
        "≤": "<=",
        "∞": "infinito",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r"[\U0001F300-\U0001FAFF\U00002700-\U000027BF]",
        "",
        text,
        flags=re.UNICODE,
    )

    text = " ".join(text.split())

    try:
        text.encode("latin-1")
    except UnicodeEncodeError:
        text = text.encode("latin-1", errors="ignore").decode("latin-1")

    return text or default


def escape_html(value):
    text = safe_text(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def short_text(value, limit=120):
    text = safe_text(value)

    if len(text) <= limit:
        return text

    return text[: limit - 3].rstrip() + "..."


def status_color(status):
    status = safe_text(status, "").lower()

    if status == "verde":
        return AFINA_GREEN

    if status == "amarillo":
        return AFINA_YELLOW

    if status == "rojo":
        return AFINA_RED

    if status in ["sin datos", "sin umbral"]:
        return AFINA_GRAY

    return AFINA_BLUE


def score_color(score):
    try:
        score = float(score)
    except Exception:
        return AFINA_GRAY

    if score >= 75:
        return AFINA_GREEN

    if score >= 50:
        return AFINA_YELLOW

    return AFINA_RED


class SemaforoCircle(Flowable):
    def __init__(self, status, width=2.45 * cm, height=0.42 * cm):
        super().__init__()
        self.status = safe_text(status)
        self.width = width
        self.height = height

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        color = status_color(self.status)
        label = safe_text(self.status).upper()

        self.canv.setFillColor(color)
        self.canv.circle(0.15 * cm, 0.14 * cm, 0.095 * cm, stroke=0, fill=1)

        self.canv.setFillColor(AFINA_TEXT)
        self.canv.setFont("Helvetica-Bold", 6.4)
        self.canv.drawString(0.33 * cm, 0.04 * cm, label)


def make_styles():
    base = getSampleStyleSheet()

    return {
        "cover_title": ParagraphStyle(
            "AFINA Cover Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=31,
            textColor=WHITE,
            alignment=TA_LEFT,
            spaceAfter=14,
        ),
        "cover_subtitle": ParagraphStyle(
            "AFINA Cover Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            textColor=colors.HexColor("#DCEAFE"),
            alignment=TA_LEFT,
        ),
        "h1": ParagraphStyle(
            "AFINA H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=21,
            textColor=AFINA_NAVY,
            spaceBefore=12,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "AFINA H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=16,
            textColor=AFINA_BLUE,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "h3": ParagraphStyle(
            "AFINA H3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            textColor=AFINA_NAVY,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "AFINA Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=AFINA_TEXT,
            spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "AFINA Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.4,
            leading=10,
            textColor=AFINA_MUTED,
        ),
        "table_header": ParagraphStyle(
            "AFINA Table Header",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=6.9,
            leading=8.4,
            textColor=WHITE,
            alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "AFINA Table Cell",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=6.9,
            leading=8.7,
            textColor=AFINA_TEXT,
        ),
        "table_cell_center": ParagraphStyle(
            "AFINA Table Cell Center",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=6.9,
            leading=8.7,
            textColor=AFINA_TEXT,
            alignment=TA_CENTER,
        ),
        "card_title": ParagraphStyle(
            "AFINA Card Title",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=AFINA_MUTED,
            alignment=TA_LEFT,
        ),
        "card_value": ParagraphStyle(
            "AFINA Card Value",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=21,
            textColor=AFINA_NAVY,
            alignment=TA_LEFT,
        ),
        "card_detail": ParagraphStyle(
            "AFINA Card Detail",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.2,
            leading=9,
            textColor=AFINA_MUTED,
            alignment=TA_LEFT,
        ),
        "white_small": ParagraphStyle(
            "AFINA White Small",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.2,
            leading=9,
            textColor=WHITE,
            alignment=TA_CENTER,
        ),
    }


def p(text, style):
    return Paragraph(escape_html(text), style)


def p_html(text, style):
    text = safe_text(text)
    text = escape_html(text)
    text = text.replace("\n", "<br/>")
    return Paragraph(text, style)


def build_header_footer(canvas, doc):
    canvas.saveState()

    width, height = A4

    canvas.setFillColor(AFINA_NAVY)
    canvas.rect(0, height - 1.0 * cm, width, 1.0 * cm, fill=1, stroke=0)

    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawString(1.35 * cm, height - 0.62 * cm, "AFINA | Analista Financiero Inteligente")

    canvas.setFont("Helvetica", 7.2)
    canvas.drawRightString(width - 1.35 * cm, height - 0.62 * cm, "Informe financiero FP&A")

    canvas.setStrokeColor(AFINA_BORDER)
    canvas.setLineWidth(0.4)
    canvas.line(1.35 * cm, 1.15 * cm, width - 1.35 * cm, 1.15 * cm)

    canvas.setFillColor(AFINA_MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(
        1.35 * cm,
        0.75 * cm,
        "Documento generado automaticamente por AFINA. Requiere validacion profesional.",
    )
    canvas.drawRightString(width - 1.35 * cm, 0.75 * cm, f"Pagina {doc.page}")

    canvas.restoreState()


def cover(snapshot, styles):
    context = snapshot.get("analysis_context", {}) or {}
    health = snapshot.get("health_score", {}) or {}
    kpi_summary = snapshot.get("kpi_summary", {}) or {}

    company = safe_text(context.get("company_name"), "Empresa analizada")
    industry = safe_text(context.get("industry"), "Industria no especificada")
    period = safe_text(context.get("period"), "Periodo no especificado")
    analysis_type = safe_text(context.get("analysis_type"), "No especificado")
    source_file = safe_text(context.get("source_file"), "Archivo no especificado")
    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M")

    score = safe_text(health.get("score"), "0")
    label = safe_text(health.get("label"), "Sin clasificacion")
    score_bg = score_color(health.get("score"))

    left = Table(
        [
            [Paragraph("Informe financiero FP&A", styles["cover_title"])],
            [
                Paragraph(
                    f"{escape_html(company)}<br/>Diagnostico financiero automatizado con metodologia AFINA",
                    styles["cover_subtitle"],
                )
            ],
            [Spacer(1, 0.35 * cm)],
            [
                Paragraph(
                    f"<b>Industria:</b> {escape_html(industry)}<br/>"
                    f"<b>Periodo:</b> {escape_html(period)}<br/>"
                    f"<b>Tipo de analisis:</b> {escape_html(analysis_type)}<br/>"
                    f"<b>Archivo fuente:</b> {escape_html(source_file)}<br/>"
                    f"<b>Fecha de generacion:</b> {escape_html(generated_at)}",
                    styles["cover_subtitle"],
                )
            ],
        ],
        colWidths=[10.15 * cm],
    )

    score_box = Table(
        [
            [Paragraph("SCORE FINANCIERO", styles["white_small"])],
            [
                Paragraph(
                    f"{escape_html(score)}%",
                    ParagraphStyle(
                        "ScoreBig",
                        fontName="Helvetica-Bold",
                        fontSize=31,
                        leading=36,
                        textColor=WHITE,
                        alignment=TA_CENTER,
                    ),
                )
            ],
            [
                Paragraph(
                    escape_html(label),
                    ParagraphStyle(
                        "ScoreLabel",
                        fontName="Helvetica-Bold",
                        fontSize=8.6,
                        leading=11,
                        textColor=WHITE,
                        alignment=TA_CENTER,
                    ),
                )
            ],
            [
                Paragraph(
                    f"KPIs calculados: {safe_text(kpi_summary.get('calculados'))} de {safe_text(kpi_summary.get('total'))}",
                    styles["white_small"],
                )
            ],
        ],
        colWidths=[5.0 * cm],
        rowHeights=[0.7 * cm, 1.35 * cm, 0.95 * cm, 0.75 * cm],
    )

    score_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), score_bg),
                ("BOX", (0, 0), (-1, -1), 0.5, score_bg),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    wrapper = Table(
        [[left, score_box]],
        colWidths=[10.8 * cm, 5.3 * cm],
    )

    wrapper.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), AFINA_NAVY),
                ("BOX", (0, 0), (-1, -1), 0, AFINA_NAVY),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 18),
                ("RIGHTPADDING", (0, 0), (-1, -1), 18),
                ("TOPPADDING", (0, 0), (-1, -1), 24),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 24),
            ]
        )
    )

    return wrapper


def metric_card(title, value, detail, color, styles):
    table = Table(
        [
            [Paragraph(escape_html(title), styles["card_title"])],
            [Paragraph(escape_html(value), styles["card_value"])],
            [Paragraph(escape_html(detail), styles["card_detail"])],
        ],
        colWidths=[3.75 * cm],
        rowHeights=[0.43 * cm, 0.72 * cm, 0.48 * cm],
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), WHITE),
                ("BOX", (0, 0), (-1, -1), 0.5, AFINA_BORDER),
                ("LINEBEFORE", (0, 0), (0, -1), 4, color),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    return table


def executive_summary(snapshot, styles):
    context = snapshot.get("analysis_context", {}) or {}
    health = snapshot.get("health_score", {}) or {}
    kpi_summary = snapshot.get("kpi_summary", {}) or {}

    company = safe_text(context.get("company_name"), "Empresa analizada")
    period = safe_text(context.get("period"), "Periodo no especificado")
    industry = safe_text(context.get("industry"), "Industria no especificada")
    score = safe_text(health.get("score"))
    label = safe_text(health.get("label"))
    total = safe_text(kpi_summary.get("total"), "0")
    calculated = safe_text(kpi_summary.get("calculados"), "0")
    pending = safe_text(kpi_summary.get("pendientes"), "0")

    return (
        f"El presente informe analiza la situacion financiera de {company} para el periodo {period}, "
        f"correspondiente a la industria {industry}, utilizando la metodologia FP&A de AFINA. "
        f"El score financiero general obtenido es {score}%, clasificado como {label}. "
        f"El motor deterministico calculo {calculated} de {total} KPIs, quedando {pending} indicador(es) "
        f"pendiente(s) por falta de informacion suficiente o trazabilidad confiable. "
        "La lectura global debe interpretarse como una combinacion entre liquidez, rentabilidad, capital de trabajo, "
        "estructura financiera y equilibrio de deuda."
    )


def dimension_reading(dimension):
    name = safe_text(dimension.get("dimension"))
    score = dimension.get("score", 0)
    status = safe_text(dimension.get("estado_dimension"))
    red = dimension.get("rojos", 0)
    yellow = dimension.get("amarillos", 0)
    no_data = dimension.get("sin_datos", 0)

    try:
        score_float = float(score)
    except Exception:
        score_float = 0

    if score_float >= 75:
        base = f"La dimension {name} presenta una condicion solida, con predominio de indicadores saludables."
    elif score_float >= 50:
        base = f"La dimension {name} muestra una condicion moderada, con senales favorables pero tambien indicadores que requieren seguimiento."
    elif score_float >= 30:
        base = f"La dimension {name} se encuentra bajo observacion, con riesgos que pueden afectar la gestion financiera si no se monitorean."
    else:
        base = f"La dimension {name} presenta una condicion critica dentro del analisis FP&A, con indicadores que requieren revision prioritaria."

    detail = f" Score de dimension: {score_float}%. Estado: {status}."

    if red:
        detail += f" Se identifican {red} indicador(es) en rojo."

    if yellow:
        detail += f" Hay {yellow} indicador(es) en amarillo que requieren seguimiento."

    if no_data:
        detail += f" Existen {no_data} indicador(es) sin datos suficientes."

    return base + detail


def dimension_recommendation(dimension):
    name = safe_text(dimension.get("dimension"))

    recommendations = {
        "Estructura de inversión": (
            "Revisar la evolucion de pasivos, patrimonio y deuda financiera para asegurar que el crecimiento "
            "del negocio no dependa excesivamente de financiamiento externo."
        ),
        "Capital de trabajo": (
            "Priorizar acciones sobre inventarios, cuentas por cobrar y ciclo de caja. "
            "La reduccion de dias inmovilizados puede liberar liquidez operativa sin necesidad de aumentar deuda."
        ),
        "Rentabilidad": (
            "Analizar margen operativo, eficiencia de activos y retorno sobre patrimonio. "
            "La mejora de rentabilidad debe combinar gestion de costos, productividad comercial y uso eficiente de activos."
        ),
        "Fluidez financiera": (
            "Complementar el analisis de liquidez estatica con generacion real de flujo operativo. "
            "Una empresa puede mostrar ratios de liquidez favorables y, aun asi, presentar presion de caja si el flujo operativo es debil."
        ),
        "Equilibrio financiero": (
            "Monitorear deuda, EBITDA y cobertura de gastos financieros. "
            "El objetivo es sostener capacidad de pago sin comprometer flexibilidad financiera futura."
        ),
    }

    return recommendations.get(
        name,
        "Revisar los indicadores principales de la dimension y validar su impacto sobre la gestion financiera.",
    )


def dimension_header(dimension, styles):
    name = safe_text(dimension.get("dimension"))
    score = safe_text(dimension.get("score"), "0")
    status = safe_text(dimension.get("estado_dimension"))
    calculated = safe_text(dimension.get("kpis_calculados"))
    total = safe_text(dimension.get("total_kpis"))
    color = score_color(dimension.get("score"))

    table = Table(
        [
            [
                Paragraph(
                    f"<b>{escape_html(name)}</b><br/>"
                    f"Score: {escape_html(score)}% | Estado: {escape_html(status)} | KPIs: {escape_html(calculated)} de {escape_html(total)}",
                    ParagraphStyle(
                        "DimensionHeaderText",
                        fontName="Helvetica-Bold",
                        fontSize=9.3,
                        leading=12,
                        textColor=WHITE,
                    ),
                )
            ]
        ],
        colWidths=[15.8 * cm],
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), color),
                ("BOX", (0, 0), (-1, -1), 0.4, color),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    return table


def scorecard_table(kpis, styles):
    rows = [
        [
            p("Indicador", styles["table_header"]),
            p("Valor actual", styles["table_header"]),
            p("Historico", styles["table_header"]),
            p("Tendencia", styles["table_header"]),
            p("Semaforo", styles["table_header"]),
            p("Diagnostico automatizado", styles["table_header"]),
        ]
    ]

    for kpi in kpis:
        code = safe_text(kpi.get("codigo_kpi"), "")
        trend = "Pendiente serie historica"

        if code == "cash_conversion_cycle":
            trend = "Validar metodologia"

        rows.append(
            [
                p(short_text(kpi.get("nombre"), 48), styles["table_cell"]),
                p(short_text(kpi.get("valor_formateado"), 26), styles["table_cell_center"]),
                p("N/D", styles["table_cell_center"]),
                p(short_text(trend, 34), styles["table_cell"]),
                SemaforoCircle(kpi.get("estado")),
                p(short_text(kpi.get("lectura"), 120), styles["table_cell"]),
            ]
        )

    table = Table(
        rows,
        colWidths=[3.35 * cm, 2.05 * cm, 1.55 * cm, 2.55 * cm, 2.45 * cm, 3.85 * cm],
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), AFINA_NAVY),
                ("GRID", (0, 0), (-1, -1), 0.25, AFINA_BORDER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, AFINA_LIGHT]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    return table


def traceability_summary_table(kpis, styles):
    rows = [
        [
            p("KPI", styles["table_header"]),
            p("Fuente", styles["table_header"]),
            p("Hoja", styles["table_header"]),
            p("Cuenta", styles["table_header"]),
        ]
    ]

    for kpi in kpis[:8]:
        trace = kpi.get("trazabilidad", {}) or {}

        source = trace.get("fuente_numerador") or trace.get("fuente_denominador") or "N/D"
        sheet = trace.get("hoja_numerador") or trace.get("hoja_denominador") or "N/D"
        account = trace.get("cuenta_numerador") or trace.get("cuenta_denominador") or "N/D"

        rows.append(
            [
                p(short_text(kpi.get("nombre"), 44), styles["table_cell"]),
                p(short_text(source, 38), styles["table_cell"]),
                p(short_text(sheet, 32), styles["table_cell"]),
                p(short_text(account, 48), styles["table_cell"]),
            ]
        )

    table = Table(
        rows,
        colWidths=[4.2 * cm, 3.7 * cm, 3.0 * cm, 4.9 * cm],
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), AFINA_BLUE),
                ("GRID", (0, 0), (-1, -1), 0.25, AFINA_BORDER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, AFINA_LIGHT]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    return table


def alerts_table(alerts, styles):
    if not alerts:
        return p("No se identificaron alertas criticas en el snapshot financiero.", styles["body"])

    rows = [
        [
            p("Prioridad", styles["table_header"]),
            p("Dimension", styles["table_header"]),
            p("KPI", styles["table_header"]),
            p("Valor", styles["table_header"]),
            p("Impacto / mensaje", styles["table_header"]),
        ]
    ]

    for alert in alerts:
        rows.append(
            [
                p(safe_text(alert.get("severidad")), styles["table_cell_center"]),
                p(short_text(alert.get("dimension"), 34), styles["table_cell"]),
                p(short_text(alert.get("kpi"), 38), styles["table_cell"]),
                p(short_text(alert.get("valor"), 24), styles["table_cell_center"]),
                p(short_text(alert.get("mensaje"), 105), styles["table_cell"]),
            ]
        )

    table = Table(
        rows,
        colWidths=[2.05 * cm, 3.1 * cm, 3.1 * cm, 2.0 * cm, 5.55 * cm],
        repeatRows=1,
        hAlign="LEFT",
    )

    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), AFINA_NAVY),
            ("GRID", (0, 0), (-1, -1), 0.25, AFINA_BORDER),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, AFINA_LIGHT]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
    )

    for idx, alert in enumerate(alerts, start=1):
        severity = safe_text(alert.get("severidad"), "").lower()

        if severity == "alta":
            color = AFINA_RED
        elif severity == "media":
            color = AFINA_YELLOW
        else:
            color = AFINA_GRAY

        style.add("BACKGROUND", (0, idx), (0, idx), color)
        style.add("TEXTCOLOR", (0, idx), (0, idx), WHITE)

    table.setStyle(style)

    return table


def quality_data_section(snapshot, styles):
    warnings = snapshot.get("data_quality_warnings", []) or []
    financial_items = snapshot.get("financial_items", {}) or {}
    pending_items = financial_items.get("pendientes", []) or []

    story = []

    if pending_items:
        story.append(p("Partidas pendientes", styles["h2"]))

        rows = [
            [
                p("Codigo interno", styles["table_header"]),
                p("Partida", styles["table_header"]),
                p("Impacto", styles["table_header"]),
            ]
        ]

        for item in pending_items:
            rows.append(
                [
                    p(short_text(item.get("Código interno"), 28), styles["table_cell"]),
                    p(short_text(item.get("Partida FP&A"), 60), styles["table_cell"]),
                    p(
                        "Puede impedir el calculo de KPIs asociados o limitar la interpretacion financiera.",
                        styles["table_cell"],
                    ),
                ]
            )

        table = Table(
            rows,
            colWidths=[3.1 * cm, 5.7 * cm, 7.0 * cm],
            repeatRows=1,
            hAlign="LEFT",
        )

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), AFINA_BLUE),
                    ("GRID", (0, 0), (-1, -1), 0.25, AFINA_BORDER),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, AFINA_LIGHT]),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        story.append(table)
        story.append(Spacer(1, 0.22 * cm))

    if warnings:
        story.append(p("Advertencias de calidad de datos", styles["h2"]))

        rows = [
            [
                p("Tipo", styles["table_header"]),
                p("Severidad", styles["table_header"]),
                p("Elemento", styles["table_header"]),
                p("Mensaje", styles["table_header"]),
            ]
        ]

        for warning in warnings:
            element = (
                warning.get("codigo_interno")
                or warning.get("codigo_kpi")
                or warning.get("kpi")
                or warning.get("partida")
                or "N/D"
            )

            rows.append(
                [
                    p(short_text(warning.get("tipo"), 32), styles["table_cell"]),
                    p(short_text(warning.get("severidad"), 28), styles["table_cell_center"]),
                    p(short_text(element, 40), styles["table_cell"]),
                    p(short_text(warning.get("mensaje"), 100), styles["table_cell"]),
                ]
            )

        table = Table(
            rows,
            colWidths=[3.2 * cm, 2.2 * cm, 3.8 * cm, 6.6 * cm],
            repeatRows=1,
            hAlign="LEFT",
        )

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), AFINA_BLUE),
                    ("GRID", (0, 0), (-1, -1), 0.25, AFINA_BORDER),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, AFINA_LIGHT]),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        story.append(table)

    if not story:
        story.append(p("No se identificaron advertencias relevantes de calidad de datos.", styles["body"]))

    return story


def recommendations(snapshot):
    dimensions = snapshot.get("dimensions_fpa", []) or []
    alerts = snapshot.get("alerts", []) or []

    lines = [
        "Priorizar la gestion del capital de trabajo: revisar inventarios, cuentas por cobrar y ciclo de caja para liberar liquidez operativa.",
        "Validar la calidad de datos contables: completar partidas pendientes y revisar partidas detectadas sin valor numerico.",
        "Analizar rentabilidad por linea o unidad de negocio: profundizar margen, rotacion de activos y retorno sobre patrimonio.",
        "Separar liquidez estatica de generacion real de caja: complementar ratios de liquidez con flujo operativo recurrente.",
        "Monitorear endeudamiento y EBITDA: controlar la evolucion de deuda financiera relativa a capacidad de generacion operativa.",
    ]

    critical_dimensions = [
        safe_text(dim.get("dimension"))
        for dim in dimensions
        if float(dim.get("score") or 0) < 50
    ]

    if critical_dimensions:
        lines.append(
            "Crear plan de accion por dimension critica: enfocar seguimiento ejecutivo en "
            + ", ".join(critical_dimensions)
            + "."
        )

    if alerts:
        lines.append(
            "Implementar seguimiento periodico de alertas: convertir los KPIs rojos en tablero de control mensual."
        )

    return lines


def sort_dimensions(dimensions):
    return sorted(
        dimensions,
        key=lambda d: DIMENSION_ORDER.index(d.get("dimension"))
        if d.get("dimension") in DIMENSION_ORDER
        else 99,
    )


def build_fpa_report_pdf(snapshot, ai_insights=None, report_markdown=None):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.35 * cm,
        leftMargin=1.35 * cm,
        topMargin=1.65 * cm,
        bottomMargin=1.45 * cm,
        title="Informe financiero FP&A - AFINA",
        author="AFINA - GOBLEXA",
    )

    styles = make_styles()
    story = []

    health = snapshot.get("health_score", {}) or {}
    kpi_summary = snapshot.get("kpi_summary", {}) or {}
    dimensions = sort_dimensions(snapshot.get("dimensions_fpa", []) or [])
    alerts = snapshot.get("alerts", []) or []

    score = safe_text(health.get("score"), "0")
    label = safe_text(health.get("label"), "Sin clasificacion")

    story.append(cover(snapshot, styles))
    story.append(Spacer(1, 0.5 * cm))

    metric_color = score_color(health.get("score"))

    cards = Table(
        [
            [
                metric_card("Score salud financiera", f"{score}%", label, metric_color, styles),
                metric_card(
                    "KPIs calculados",
                    safe_text(kpi_summary.get("calculados"), "0"),
                    f"de {safe_text(kpi_summary.get('total'), '0')} KPIs",
                    AFINA_GREEN,
                    styles,
                ),
                metric_card(
                    "KPIs pendientes",
                    safe_text(kpi_summary.get("pendientes"), "0"),
                    "Sin datos suficientes",
                    AFINA_YELLOW if int(kpi_summary.get("pendientes") or 0) > 0 else AFINA_GREEN,
                    styles,
                ),
                metric_card(
                    "Cobertura catalogo",
                    f"{safe_text(kpi_summary.get('cobertura'), '0')}%",
                    "Catalogo FP&A",
                    AFINA_BLUE,
                    styles,
                ),
            ]
        ],
        colWidths=[3.95 * cm, 3.95 * cm, 3.95 * cm, 3.95 * cm],
    )

    cards.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(cards)
    story.append(PageBreak())

    story.append(p("1. Resumen ejecutivo", styles["h1"]))
    story.append(p_html(executive_summary(snapshot, styles), styles["body"]))

    story.append(p("2. Scorecard FP&A por dimension", styles["h1"]))

    for index, dimension in enumerate(dimensions, start=1):
        kpis = dimension.get("kpis", []) or []

        story.append(dimension_header(dimension, styles))
        story.append(Spacer(1, 0.16 * cm))
        story.append(p_html(dimension_reading(dimension), styles["body"]))

        if kpis:
            story.append(scorecard_table(kpis, styles))
            story.append(Spacer(1, 0.14 * cm))
            story.append(p("Trazabilidad resumida", styles["h3"]))
            story.append(traceability_summary_table(kpis, styles))
            story.append(Spacer(1, 0.12 * cm))

        story.append(p("Recomendacion especifica", styles["h3"]))
        story.append(p_html(dimension_recommendation(dimension), styles["body"]))

        if index < len(dimensions):
            story.append(Spacer(1, 0.22 * cm))

    story.append(PageBreak())

    story.append(p("3. Alertas prioritarias", styles["h1"]))
    story.append(alerts_table(alerts, styles))

    story.append(p("4. Trazabilidad y calidad de datos", styles["h1"]))
    story.extend(quality_data_section(snapshot, styles))

    if ai_insights:
        story.append(p("5. Sintesis consultiva generada por IA", styles["h1"]))
        words = safe_text(ai_insights).split()
        compact = " ".join(words[:420])
        story.append(
            p_html(
                "Este bloque complementa el informe estructurado de AFINA con una lectura ejecutiva generada desde el snapshot financiero. "
                "La IA interpreta los KPIs calculados, pero no reemplaza el motor deterministico ni la validacion profesional.",
                styles["body"],
            )
        )
        story.append(p_html(compact, styles["body"]))
        next_section = 6
    else:
        next_section = 5

    story.append(p(f"{next_section}. Recomendaciones estrategicas", styles["h1"]))

    for idx, recommendation in enumerate(recommendations(snapshot), start=1):
        story.append(p_html(f"{idx}. {recommendation}", styles["body"]))

    story.append(p(f"{next_section + 1}. Disclaimer", styles["h1"]))
    story.append(p_html(snapshot.get("disclaimer"), styles["body"]))

    doc.build(
        story,
        onFirstPage=build_header_footer,
        onLaterPages=build_header_footer,
    )

    pdf = buffer.getvalue()
    buffer.close()

    return pdf
