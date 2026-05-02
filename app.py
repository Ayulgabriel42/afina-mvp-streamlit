import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.loader import get_excel_sheets, load_financial_file
from src.analyzer import analyze_financial_dataframe
from src.normalizer import normalize_financial_dataframe
from src.extractor import extract_financial_items
from src.kpi_engine import calculate_kpis
from src.kpi_visuals import (
    prepare_kpi_visual_dataframe,
    build_health_gauge,
    build_status_donut,
    build_percentage_kpis_chart,
    build_ratio_kpis_chart,
    build_cash_cycle_chart,
    build_kpi_radar_chart,
    build_health_score
)
from src.statement_mapper import (
    NO_USAR,
    STATEMENT_ROLES,
    suggest_sheet_mapping,
    calculate_mapping_completeness,
)
from src.financial_snapshot import build_financial_snapshot, snapshot_to_json
from src.ai_insights import generate_ai_insights
from src.report_builder import build_fpa_report_markdown

# =========================
# Configuración general
# =========================
st.set_page_config(
    page_title="AFINA MVP - GOBLEXA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# Estilos visuales
# =========================
st.markdown(
    """
    <style>
        header[data-testid="stHeader"] {
            background: rgba(248, 250, 252, 0.92);
            backdrop-filter: blur(10px);
            height: 2.75rem;
        }

        div[data-testid="stToolbar"] {
            top: 0.5rem;
        }

        .block-container {
            padding-top: 4rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
        }

        [data-testid="stSidebar"] > div:first-child {
            background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
        }

        [data-testid="stSidebar"] * {
            color: #E5E7EB;
        }

        .afina-logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1.8rem;
        }

        .afina-logo-icon {
            width: 44px;
            height: 44px;
            background: #2563EB;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.45rem;
            box-shadow: 0 12px 25px rgba(37, 99, 235, 0.35);
        }

        .afina-logo-title {
            font-size: 1.35rem;
            font-weight: 850;
            color: white;
            line-height: 1.1;
        }

        .afina-logo-subtitle {
            font-size: 0.82rem;
            color: #CBD5E1;
        }

        .hero-card {
            background: linear-gradient(135deg, #1D4ED8 0%, #4338CA 55%, #6D28D9 100%);
            border-radius: 22px;
            padding: 2rem 2.2rem;
            color: white;
            box-shadow: 0 18px 40px rgba(37, 99, 235, 0.22);
            margin-bottom: 1.8rem;
        }

        .hero-title {
            font-size: 2.05rem;
            font-weight: 850;
            margin-bottom: 0.3rem;
            letter-spacing: -0.04em;
        }

        .hero-subtitle {
            font-size: 1.02rem;
            color: #DBEAFE;
        }

        .section-title {
            font-size: 1.45rem;
            font-weight: 800;
            color: #0F172A;
            margin-bottom: 0.2rem;
        }

        .section-subtitle {
            color: #64748B;
            margin-bottom: 1.2rem;
            font-size: 1rem;
        }

        .kpi-card {
            background: white;
            border-radius: 20px;
            padding: 1.25rem;
            border: 1px solid #E2E8F0;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
            min-height: 150px;
            position: relative;
            margin-bottom: 1rem;
        }

        .kpi-card-red {
            background: #FFF1F2;
            border: 1px solid #FDA4AF;
        }

        .kpi-card-green {
            background: #ECFDF5;
            border: 1px solid #86EFAC;
        }

        .kpi-card-blue {
            background: #EFF6FF;
            border: 1px solid #93C5FD;
        }

        .kpi-card-yellow {
            background: #FFFBEB;
            border: 1px solid #FDE68A;
        }

        .kpi-title {
            color: #334155;
            font-size: 0.95rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
        }

        .kpi-value {
            color: #0F172A;
            font-size: 1.85rem;
            font-weight: 850;
            margin-bottom: 0.35rem;
            word-break: break-word;
        }

        .kpi-detail {
            color: #64748B;
            font-size: 0.86rem;
        }

        .status-dot {
            position: absolute;
            top: 1.2rem;
            right: 1.2rem;
            width: 16px;
            height: 16px;
            border-radius: 999px;
        }

        .dot-red {
            background: #E11D48;
            box-shadow: 0 0 14px rgba(225, 29, 72, 0.5);
        }

        .dot-green {
            background: #22C55E;
            box-shadow: 0 0 14px rgba(34, 197, 94, 0.5);
        }

        .dot-yellow {
            background: #F59E0B;
            box-shadow: 0 0 14px rgba(245, 158, 11, 0.5);
        }

        .dot-blue {
            background: #2563EB;
            box-shadow: 0 0 14px rgba(37, 99, 235, 0.5);
        }

        .action-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 20px;
            padding: 1.3rem;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
            min-height: 145px;
            margin-bottom: 1rem;
        }

        .action-icon {
            font-size: 1.8rem;
            margin-bottom: 0.6rem;
        }

        .action-title {
            font-weight: 800;
            color: #0F172A;
            margin-bottom: 0.3rem;
            font-size: 1.05rem;
        }

        .action-text {
            color: #64748B;
            font-size: 0.9rem;
        }

        .info-box {
            background: #EFF6FF;
            border: 1px solid #BFDBFE;
            color: #1E3A8A;
            padding: 1.1rem 1.2rem;
            border-radius: 18px;
            margin-bottom: 1rem;
        }

        .warning-box {
            background: #FFFBEB;
            border: 1px solid #FDE68A;
            color: #92400E;
            padding: 1.1rem 1.2rem;
            border-radius: 18px;
            margin-bottom: 1rem;
        }

        .success-box {
            background: #ECFDF5;
            border: 1px solid #A7F3D0;
            color: #065F46;
            padding: 1.1rem 1.2rem;
            border-radius: 18px;
            margin-bottom: 1rem;
        }

        .workflow-box {
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 22px;
            padding: 1.4rem;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
            margin-bottom: 1.2rem;
        }

        .footer {
            color: #94A3B8;
            font-size: 0.82rem;
            margin-top: 2rem;
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# Estado de sesión
# =========================
DEFAULTS = {
    "workbook_sheets": [],
    "sheet_mapping": None,
    "fpna_documents": None,
    "fpna_context": None,
    "mapping_completeness": None,
    "financial_items": None,
    "financial_items_summary": None,
    "kpis": None,
    "kpis_summary": None,
    "selected_industry": "Sector Químico",
    "analysis_period": None,
    "comparison_period": None,
    "analysis_type": None,
    "uploaded_file_name": None,
    "company_name": None,
    "ai_insights": None,
    "ai_insights_model": None,
    "analysis_ready": False,
    "current_section": "1. Nuevo análisis FP&A"
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

NAV_OPTIONS = [
    "1. Nuevo análisis FP&A",
    "2. Dashboard financiero",
    "3. KPIs",
    "4. Proyecciones",
    "5. Chatbot AFINA",
    "6. Informe",
    "7. Admin básico"
]

if st.session_state.current_section not in NAV_OPTIONS:
    st.session_state.current_section = "1. Nuevo análisis FP&A"

# =========================
# Opciones base
# =========================
INDUSTRIES = [
    "Sector Químico",
    "SaaS / Tecnología",
    "Manufactura",
    "Retail / Comercio",
    "Salud / Farmacia",
    "Servicios Financieros"
]

PERIODS = [
    "Año 2025",
    "Q4 2025",
    "Q3 2025",
    "Q2 2025",
    "Q1 2025",
    "Segundo Semestre 2025",
    "Primer Semestre 2025",
    "Año 2024",
    "Período 2023-2024",
    "Q4 2024",
    "Q3 2024",
    "Q2 2024",
    "Q1 2024",
    "Segundo Semestre 2024",
    "Primer Semestre 2024",
    "Año 2023",
    "Período 2022-2023",
    "Q4 2023",
    "Q3 2023",
    "Q2 2023",
    "Q1 2023",
    "Segundo Semestre 2023",
    "Primer Semestre 2023",
    "Año 2022",
    "Período 2021-2022",
    "Año 2021",
    "Año 2020",
    "Año 2019"
]

ANALYSIS_TYPES = [
    "Automático",
    "Único",
    "Comparativo"
]

# =========================
# Funciones visuales
# =========================
def kpi_card(title, value, detail, color="blue", dot="green"):
    st.markdown(
        f"""
        <div class="kpi-card kpi-card-{color}">
            <div class="status-dot dot-{dot}"></div>
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def action_card(icon, title, text):
    st.markdown(
        f"""
        <div class="action-card">
            <div class="action-icon">{icon}</div>
            <div class="action-title">{title}</div>
            <div class="action-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def section_header(title, subtitle):
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        <div class="section-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True
    )


def go_to(section_name):
    st.session_state.current_section = section_name


def build_bar_chart():
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=["Liquidez", "Rentabilidad", "Endeudamiento", "Rotación"],
        y=[0.75, 5.8, 18.2, 0.7],
        name="Actual",
        marker_color="#2563EB"
    ))

    fig.add_trace(go.Bar(
        x=["Liquidez", "Rentabilidad", "Endeudamiento", "Rotación"],
        y=[1.5, 12, 40, 1.2],
        name="Objetivo",
        marker_color="#22C55E"
    ))

    fig.update_layout(
        height=330,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        barmode="group"
    )

    return fig


def build_pie_chart():
    fig = go.Figure(data=[go.Pie(
        labels=["Activo corriente", "Activo no corriente", "Otros activos"],
        values=[45, 35, 20],
        hole=0.45,
        marker=dict(colors=["#2563EB", "#22C55E", "#F59E0B"])
    )])

    fig.update_layout(
        height=330,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="white"
    )

    return fig


def load_mapped_financial_documents(uploaded_file, mapping):
    documents = {}

    for role, sheet_name in mapping.items():
        if sheet_name == NO_USAR:
            continue

        df, metadata = load_financial_file(uploaded_file, sheet_name=sheet_name)
        analysis = analyze_financial_dataframe(df, metadata=metadata)
        normalization = normalize_financial_dataframe(df)

        documents[role] = {
            "role_label": STATEMENT_ROLES[role],
            "sheet_name": sheet_name,
            "dataframe": df,
            "metadata": metadata,
            "analysis": analysis,
            "normalization": normalization
        }

    return documents


def documents_summary_table(documents):
    rows = []

    if not documents:
        return pd.DataFrame()

    for role, doc in documents.items():
        metadata = doc["metadata"]
        normalization = doc["normalization"]

        rows.append({
            "Bloque FP&A": doc["role_label"],
            "Hoja seleccionada": doc["sheet_name"],
            "Filas": metadata["rows"],
            "Columnas": metadata["columns"],
            "Filas normalizadas": normalization["rows_detected"],
            "Estado técnico": normalization["status"]
        })

    return pd.DataFrame(rows)



def render_kpis_section(show_trace=False):
    if st.session_state.kpis is None or st.session_state.kpis_summary is None:
        return

    summary = st.session_state.kpis_summary
    kpis_df = st.session_state.kpis

    section_header(
        "KPIs financieros calculados",
        "Indicadores generados a partir de las partidas FP&A detectadas, con trazabilidad de cálculo."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_card(
            "Cobertura KPI",
            f"{summary['coverage']}%",
            summary["status"],
            "green" if summary["coverage"] >= 80 else "yellow",
            "green" if summary["coverage"] >= 80 else "yellow"
        )

    with col2:
        kpi_card(
            "Calculados",
            summary["calculated_kpis"],
            "Indicadores disponibles",
            "green",
            "green"
        )

    with col3:
        kpi_card(
            "Pendientes",
            summary["missing_kpis"],
            "Indicadores sin datos",
            "yellow" if summary["missing_kpis"] > 0 else "green",
            "yellow" if summary["missing_kpis"] > 0 else "green"
        )

    with col4:
        kpi_card(
            "Total KPIs",
            summary["total_kpis"],
            "KPIs base FP&A",
            "blue",
            "blue"
        )

    st.markdown(
        f"""
        <div class="info-box">
            <strong>Lectura KPI:</strong><br>
            {summary["detail"]}
        </div>
        """,
        unsafe_allow_html=True
    )

    visible_columns = [
        "KPI",
        "Valor formateado",
        "Fórmula",
        "Fuente cálculo",
        "Estado",
        "Lectura"
    ]

    st.subheader("Resumen de KPIs")
    st.dataframe(kpis_df[visible_columns], width="stretch")

    if show_trace:
        with st.expander("Trazabilidad de cálculo KPI"):
            trace_columns = [
                "KPI",
                "Numerador usado",
                "Valor numerador",
                "Fuente numerador",
                "Hoja numerador",
                "Cuenta numerador",
                "Denominador usado",
                "Valor denominador",
                "Fuente denominador",
                "Hoja denominador",
                "Cuenta denominador"
            ]
            st.dataframe(kpis_df[trace_columns], width="stretch")


def render_financial_items_section():
    if st.session_state.financial_items is None:
        return

    section_header(
        "Partidas FP&A para cálculo de KPIs",
        "Listado de partidas detectadas y pendientes antes de calcular indicadores reales."
    )

    detected_items_df = st.session_state.financial_items[
        st.session_state.financial_items["Estado"] == "Detectada"
    ]

    missing_items_df = st.session_state.financial_items[
        st.session_state.financial_items["Estado"] == "No detectada"
    ]

    summary = st.session_state.financial_items_summary

    col1, col2, col3 = st.columns(3)

    with col1:
        kpi_card(
            "Detectadas",
            len(detected_items_df),
            "Partidas listas para KPIs",
            "green",
            "green"
        )

    with col2:
        kpi_card(
            "Pendientes",
            len(missing_items_df),
            "Requieren mejora de reglas",
            "yellow" if len(missing_items_df) > 0 else "green",
            "yellow" if len(missing_items_df) > 0 else "green"
        )

    with col3:
        kpi_card(
            "Cobertura",
            f"{summary['coverage']}%",
            summary["status"],
            "green" if summary["coverage"] >= 75 else "yellow",
            "green" if summary["coverage"] >= 75 else "yellow"
        )

    st.subheader("Partidas detectadas")
    st.dataframe(detected_items_df, width="stretch")

    if not missing_items_df.empty:
        st.subheader("Partidas pendientes de detección")
        st.warning(
            "Estas partidas todavía no fueron encontradas automáticamente. "
            "Vamos a usarlas para mejorar las reglas del extractor antes de calcular KPIs reales."
        )
        st.dataframe(missing_items_df, width="stretch")
    else:
        st.success("AFINA detectó todas las partidas FP&A buscadas para esta etapa.")





def render_financial_snapshot_section():
    """
    Genera y muestra el JSON financiero estándar del análisis actual.
    Esta es la base para IA, informes PDF/Word y chatbot contextual.
    """
    if st.session_state.get("kpis") is None:
        st.warning("Todavía no hay KPIs calculados. Primero generá el análisis FP&A.")
        return

    kpis_df = st.session_state.get("kpis")
    financial_items_df = st.session_state.get("financial_items")

    source_file = (
        st.session_state.get("uploaded_file_name")
        or st.session_state.get("source_file")
        or st.session_state.get("file_name")
        or "Archivo financiero cargado"
    )

    company_name = st.session_state.get("company_name") or "Empresa analizada"

    snapshot = build_financial_snapshot(
        company_name=company_name,
        source_file=source_file,
        industry=st.session_state.get("selected_industry", "No especificada"),
        period=st.session_state.get("analysis_period", "No especificado"),
        analysis_type=st.session_state.get("analysis_type", "No especificado"),
        kpis_df=kpis_df,
        kpis_summary=st.session_state.get("kpis_summary"),
        financial_items_df=financial_items_df,
        financial_items_summary=st.session_state.get("financial_items_summary"),
    )

    st.session_state["financial_snapshot"] = snapshot

    section_header(
        "JSON financiero estándar",
        "Snapshot estructurado del análisis: base para IA, informe PDF/Word y chatbot contextual."
    )

    score = snapshot["health_score"]["score"]
    kpi_summary = snapshot["kpi_summary"]
    alerts = snapshot["alerts"]

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Score financiero",
            f"{score}%",
            snapshot["health_score"]["label"],
            "green" if score >= 75 else "yellow" if score >= 50 else "red",
            "green" if score >= 75 else "yellow" if score >= 50 else "red"
        )

    with c2:
        kpi_card(
            "KPIs calculados",
            kpi_summary["calculados"],
            f"de {kpi_summary['total']} KPIs",
            "green" if kpi_summary["pendientes"] == 0 else "yellow",
            "green" if kpi_summary["pendientes"] == 0 else "yellow"
        )

    with c3:
        kpi_card(
            "Dimensiones FPA",
            len(snapshot["dimensions_fpa"]),
            "Bloques financieros",
            "blue",
            "blue"
        )

    with c4:
        kpi_card(
            "Alertas JSON",
            len(alerts),
            "Rojas o sin datos",
            "red" if len(alerts) > 0 else "green",
            "red" if len(alerts) > 0 else "green"
        )

    st.markdown(
        """
        <div class="info-box">
            <strong>Uso previsto:</strong><br>
            Este JSON debe ser consumido por la futura capa de IA. La IA no debería recalcular KPIs:
            debe interpretar este snapshot validado por el motor financiero de AFINA.
        </div>
        """,
        unsafe_allow_html=True
    )

    json_payload = snapshot_to_json(snapshot)

    st.download_button(
        label="Descargar JSON financiero",
        data=json_payload,
        file_name="afina_financial_snapshot.json",
        mime="application/json"
    )

    with st.expander("Ver JSON financiero completo", expanded=False):
        st.json(snapshot)

    with st.expander("Alertas incluidas en el JSON", expanded=True):
        if alerts:
            st.dataframe(pd.DataFrame(alerts), width="stretch", hide_index=True)
        else:
            st.success("No se generaron alertas críticas en el snapshot.")



def render_ai_insights_section():
    """
    Genera diagnóstico ejecutivo con IA a partir del JSON financiero estándar.
    La llamada es manual para controlar costos.
    """
    snapshot = st.session_state.get("financial_snapshot")

    if not snapshot:
        st.info("Primero generá el JSON financiero estándar en esta misma sección.")
        return

    section_header(
        "Síntesis consultiva con IA",
        "Comentario ejecutivo breve generado desde el JSON financiero estándar de AFINA."
    )

    st.markdown(
        """
        <div class="warning-box">
            <strong>Control de costo:</strong><br>
            La IA se ejecuta solo al presionar el botón. El modelo inicial recomendado es <strong>gpt-5-mini</strong>.
            Más adelante se podrá cambiar a <strong>gpt-5.2</strong> para informes finales premium.
        </div>
        """,
        unsafe_allow_html=True
    )

    model = st.selectbox(
        "Modelo OpenAI",
        ["gpt-5-mini", "gpt-5-nano", "gpt-5.2"],
        index=0,
        help="Para pruebas usar gpt-5-mini o gpt-5-nano. Para informe final premium usar gpt-5.2."
    )

    col1, col2 = st.columns([1, 3])

    with col1:
        generate = st.button("Generar síntesis IA", type="primary")

    with col2:
        if st.session_state.get("ai_insights"):
            st.success(f"Insights ya generados con {st.session_state.get('ai_insights_model')}.")

    if generate:
        try:
            with st.spinner("AFINA está generando el diagnóstico ejecutivo con IA..."):
                result = generate_ai_insights(snapshot, model=model)
                st.session_state.ai_insights = result["output_text"]
                st.session_state.ai_insights_model = result["model"]
                st.session_state.ai_prompt_tokens_estimate = result["prompt_tokens_estimate"]

            st.success("Insights generados correctamente.")
        except Exception as e:
            st.error(f"No se pudieron generar insights con IA: {e}")

    if st.session_state.get("ai_insights"):
        st.subheader("Síntesis consultiva generada")
        st.markdown(st.session_state.ai_insights)

        st.caption(
            f"Modelo: {st.session_state.get('ai_insights_model')} · "
            f"Estimación prompt tokens: {st.session_state.get('ai_prompt_tokens_estimate', 'N/D')}"
        )

        st.download_button(
            label="Descargar síntesis IA en Markdown",
            data=st.session_state.ai_insights,
            file_name="afina_insights_ia.md",
            mime="text/markdown"
        )



def render_fpa_report_template_section():
    """
    Construye un informe FP&A parametrizable en Markdown desde el JSON financiero estándar.
    """
    snapshot = st.session_state.get("financial_snapshot")

    if not snapshot:
        st.info("Primero generá el JSON financiero estándar.")
        return

    section_header(
        "Template parametrizable de informe FP&A",
        "Informe estructurado y reutilizable por cliente, industria y período."
    )

    st.markdown(
        """
        <div class="info-box">
            <strong>Arquitectura del informe:</strong><br>
            AFINA controla la estructura del reporte, los KPIs, scorecards, trazabilidad, alertas,
            conclusiones y recomendaciones base. La IA se usa como insumo consultivo, no como motor de cálculo.
        </div>
        """,
        unsafe_allow_html=True
    )

    include_ai = False

    if st.session_state.get("ai_insights"):
        include_ai = st.checkbox(
            "Incluir comentario consultivo generado por IA",
            value=True,
            help="El informe mantiene estructura fija y agrega el diagnóstico IA como bloque complementario."
        )
    else:
        st.info(
            "Todavía no hay comentario IA generado. El informe puede construirse igualmente "
            "con reglas, KPIs y JSON financiero."
        )

    if st.button("Generar informe FP&A en Markdown", type="primary"):
        report_markdown = build_fpa_report_markdown(
            snapshot,
            ai_insights=st.session_state.get("ai_insights") if include_ai else None
        )

        st.session_state.fpa_report_markdown = report_markdown
        st.success("Informe FP&A generado correctamente.")

    if st.session_state.get("fpa_report_markdown"):
        st.subheader("Vista previa del informe FP&A")

        with st.expander("Ver informe completo en pantalla", expanded=True):
            st.markdown(st.session_state.fpa_report_markdown)

        st.download_button(
            label="Descargar informe FP&A en Markdown",
            data=st.session_state.fpa_report_markdown,
            file_name="informe_fpa_afina.md",
            mime="text/markdown"
        )


def render_kpis_grouped_by_dimension(kpis_df):
    """
    Renderiza el catálogo de KPIs agrupado por dimensiones FPA.
    No recalcula KPIs: solo ordena y presenta la salida del motor kpi_engine.py.
    """
    if kpis_df is None or kpis_df.empty:
        st.warning("No hay KPIs disponibles para agrupar por dimensión.")
        return

    if "Dimensión FPA" not in kpis_df.columns:
        st.info("Los KPIs todavía no tienen dimensión FPA asignada.")
        return

    dimension_order = [
        "Estructura de inversión",
        "Capital de trabajo",
        "Rentabilidad",
        "Fluidez financiera",
        "Equilibrio financiero",
    ]

    status_points = {
        "Verde": 100,
        "Amarillo": 50,
        "Rojo": 0,
        "Sin datos": 0,
        "Sin umbral": 50,
    }

    st.subheader("KPIs agrupados por dimensión FPA")

    st.markdown(
        """
        <div class="info-box">
            <strong>Lectura por dimensión:</strong><br>
            Esta vista organiza los 19 KPIs del catálogo FPA según su impacto financiero:
            estructura, capital de trabajo, rentabilidad, fluidez y equilibrio financiero.
        </div>
        """,
        unsafe_allow_html=True
    )

    for dimension in dimension_order:
        dimension_df = kpis_df[kpis_df["Dimensión FPA"] == dimension].copy()

        if dimension_df.empty:
            continue

        calculated_df = dimension_df[dimension_df["Fuente cálculo"] != "No calculado"].copy()

        total = len(dimension_df)
        calculated = len(calculated_df)
        pending = total - calculated

        green = int((dimension_df["Estado"] == "Verde").sum())
        yellow = int((dimension_df["Estado"] == "Amarillo").sum())
        red = int((dimension_df["Estado"] == "Rojo").sum())
        no_data = int((dimension_df["Estado"] == "Sin datos").sum())

        if calculated > 0:
            calculated_df["Puntaje dimensión"] = calculated_df["Estado"].map(status_points).fillna(0)
            dimension_score = round(calculated_df["Puntaje dimensión"].sum() / calculated, 1)
        else:
            dimension_score = 0

        if dimension_score >= 75:
            dimension_label = "Sólida"
            card_color = "green"
        elif dimension_score >= 50:
            dimension_label = "Moderada"
            card_color = "yellow"
        elif calculated == 0:
            dimension_label = "Sin datos"
            card_color = "blue"
        else:
            dimension_label = "Crítica"
            card_color = "red"

        with st.expander(f"{dimension} · Score {dimension_score}% · {dimension_label}", expanded=True):
            c1, c2, c3, c4, c5 = st.columns(5)

            with c1:
                kpi_card(
                    "Score dimensión",
                    f"{dimension_score}%",
                    dimension_label,
                    card_color,
                    card_color
                )

            with c2:
                kpi_card(
                    "Calculados",
                    calculated,
                    f"de {total} KPIs",
                    "green" if pending == 0 else "yellow",
                    "green" if pending == 0 else "yellow"
                )

            with c3:
                kpi_card(
                    "Verdes",
                    green,
                    "Óptimos",
                    "green",
                    "green"
                )

            with c4:
                kpi_card(
                    "Amarillos",
                    yellow,
                    "Seguimiento",
                    "yellow",
                    "yellow"
                )

            with c5:
                kpi_card(
                    "Rojos / sin datos",
                    red + no_data,
                    "Alertas o faltantes",
                    "red" if (red + no_data) > 0 else "green",
                    "red" if (red + no_data) > 0 else "green"
                )

            visible_columns = [
                "Código SRS",
                "KPI",
                "Valor formateado",
                "Fórmula",
                "Fuente cálculo",
                "Estado cálculo",
                "Estado",
                "Lectura",
                "Nota cálculo",
            ]

            available_columns = [
                col for col in visible_columns
                if col in dimension_df.columns
            ]

            st.dataframe(
                dimension_df[available_columns],
                width="stretch",
                hide_index=True
            )

            if pending > 0:
                pending_df = dimension_df[dimension_df["Fuente cálculo"] == "No calculado"].copy()

                pending_columns = [
                    "Código SRS",
                    "KPI",
                    "Partidas faltantes",
                    "Nota cálculo",
                ]

                available_pending_columns = [
                    col for col in pending_columns
                    if col in pending_df.columns
                ]

                if not pending_df.empty:
                    st.warning("KPIs pendientes de cálculo en esta dimensión:")
                    st.dataframe(
                        pending_df[available_pending_columns],
                        width="stretch",
                        hide_index=True
                    )

def render_kpi_visual_grid(show_table=True, show_trace=True):
    """
    Renderiza KPIs reales en formato visual.
    Si los KPIs no están calculados pero existen partidas FP&A, los calcula en el momento.
    """
    if st.session_state.get("kpis") is None and st.session_state.get("financial_items") is not None:
        kpis, kpis_summary = calculate_kpis(
            st.session_state.financial_items,
            industry=st.session_state.get("selected_industry", "Sector Químico")
        )
        st.session_state.kpis = kpis
        st.session_state.kpis_summary = kpis_summary

    if st.session_state.get("kpis") is None or st.session_state.get("kpis_summary") is None:
        st.warning("Todavía no hay KPIs calculados. Primero generá el análisis FP&A.")
        return

    kpis_df = st.session_state.kpis
    summary = st.session_state.kpis_summary

    section_header(
        "KPIs financieros reales",
        "Indicadores calculados desde las partidas FP&A detectadas, con semáforo y trazabilidad."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_card(
            "Cobertura KPI",
            f"{summary['coverage']}%",
            summary["status"],
            "green" if summary["coverage"] >= 80 else "yellow",
            "green" if summary["coverage"] >= 80 else "yellow"
        )

    with col2:
        kpi_card(
            "Calculados",
            summary["calculated_kpis"],
            "Indicadores disponibles",
            "green",
            "green"
        )

    with col3:
        kpi_card(
            "Pendientes",
            summary["missing_kpis"],
            "Sin datos suficientes",
            "yellow" if summary["missing_kpis"] > 0 else "green",
            "yellow" if summary["missing_kpis"] > 0 else "green"
        )

    with col4:
        kpi_card(
            "Total KPIs",
            summary["total_kpis"],
            "KPIs base FP&A",
            "blue",
            "blue"
        )

    st.markdown(
        f"""
        <div class="info-box">
            <strong>Lectura KPI:</strong><br>
            {summary["detail"]}
        </div>
        """,
        unsafe_allow_html=True
    )

    main_kpi_codes = [
        "current_ratio",
        "debt_ratio",
        "roe",
        "roa",
        "gross_margin",
        "operating_margin",
        "asset_turnover",
        "cash_conversion_cycle"
    ]

    main_kpis_df = kpis_df[kpis_df["Código KPI"].isin(main_kpi_codes)]

    st.subheader("Tablero visual de KPIs")

    for start in range(0, len(main_kpis_df), 4):
        cols = st.columns(4)
        chunk = main_kpis_df.iloc[start:start + 4]

        for idx, (_, row) in enumerate(chunk.iterrows()):
            color = row.get("Color", "blue")

            if color not in ["green", "yellow", "red", "blue"]:
                color = "blue"

            with cols[idx]:
                kpi_card(
                    row["KPI"],
                    row["Valor formateado"],
                    f'{row["Estado"]} · {row["Fuente cálculo"]}',
                    color,
                    color
                )

    if show_table:
        visible_columns = [
            "KPI",
            "Valor formateado",
            "Fórmula",
            "Fuente cálculo",
            "Estado",
            "Lectura"
        ]

        st.subheader("Resumen de KPIs calculados")
        st.dataframe(kpis_df[visible_columns], width="stretch")

    if show_trace:
        with st.expander("Trazabilidad de cálculo KPI"):
            trace_columns = [
                "KPI",
                "Numerador usado",
                "Valor numerador",
                "Fuente numerador",
                "Hoja numerador",
                "Cuenta numerador",
                "Denominador usado",
                "Valor denominador",
                "Fuente denominador",
                "Hoja denominador",
                "Cuenta denominador"
            ]

            available_trace_columns = [
                col for col in trace_columns
                if col in kpis_df.columns
            ]

            st.dataframe(kpis_df[available_trace_columns], width="stretch")




def render_kpi_executive_visuals(show_tables=True):
    """
    Visualización ejecutiva de KPIs reales.
    Usa st.session_state.kpis generado por kpi_engine.py.
    """
    if st.session_state.get("kpis") is None:
        st.warning("Todavía no hay KPIs calculados. Primero generá el análisis FP&A.")
        return

    kpis_df = prepare_kpi_visual_dataframe(st.session_state.kpis)

    if kpis_df.empty:
        st.warning("No se pudieron preparar los KPIs para visualización.")
        return

    score_data = build_health_score(kpis_df)

    section_header(
        "Dashboard ejecutivo de KPIs",
        "Indicadores reales calculados por AFINA, con semáforos y lectura FP&A."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_card(
            "Score salud financiera",
            f"{score_data['score']}%",
            score_data["label"],
            "green" if score_data["score"] >= 70 else "yellow" if score_data["score"] >= 40 else "red",
            "green" if score_data["score"] >= 70 else "yellow" if score_data["score"] >= 40 else "red"
        )

    with col2:
        kpi_card(
            "KPIs verdes",
            score_data["green"],
            "Indicadores saludables",
            "green",
            "green"
        )

    with col3:
        kpi_card(
            "KPIs amarillos",
            score_data["yellow"],
            "Requieren seguimiento",
            "yellow",
            "yellow"
        )

    with col4:
        kpi_card(
            "KPIs rojos",
            score_data["red"],
            "Alertas críticas",
            "red" if score_data["red"] > 0 else "green",
            "red" if score_data["red"] > 0 else "green"
        )

    st.subheader("KPIs principales")

    for start in range(0, len(kpis_df), 4):
        cols = st.columns(4)
        chunk = kpis_df.iloc[start:start + 4]

        for idx, (_, row) in enumerate(chunk.iterrows()):
            color = row.get("Color", "blue")

            if color not in ["green", "yellow", "red", "blue"]:
                color = "blue"

            with cols[idx]:
                kpi_card(
                    row["KPI"],
                    row["Valor formateado"],
                    f'{row["Estado"]} · {row["Fuente cálculo"]}',
                    color,
                    color
                )

    # Vista agrupada por dimensiones FPA
    render_kpis_grouped_by_dimension(kpis_df)

    st.subheader("Visualización ejecutiva")

    fig_gauge, _ = build_health_gauge(kpis_df)
    fig_donut = build_status_donut(kpis_df)

    c1, c2 = st.columns(2)

    with c1:
        st.plotly_chart(fig_gauge, width="stretch")

    if fig_donut is not None:
        with c2:
            st.plotly_chart(fig_donut, width="stretch")

    fig_percentages = build_percentage_kpis_chart(kpis_df)
    fig_radar = build_kpi_radar_chart(kpis_df)

    c1, c2 = st.columns(2)

    if fig_percentages is not None:
        with c1:
            st.plotly_chart(fig_percentages, width="stretch")

    if fig_radar is not None:
        with c2:
            st.plotly_chart(fig_radar, width="stretch")

    fig_ratios = build_ratio_kpis_chart(kpis_df)
    fig_cash_cycle = build_cash_cycle_chart(kpis_df)

    c1, c2 = st.columns(2)

    if fig_ratios is not None:
        with c1:
            st.plotly_chart(fig_ratios, width="stretch")

    if fig_cash_cycle is not None:
        with c2:
            st.plotly_chart(fig_cash_cycle, width="stretch")

    if show_tables:
        st.subheader("Tabla ejecutiva de KPIs")

        visible_columns = [
            "KPI",
            "Valor formateado",
            "Fórmula",
            "Fuente cálculo",
            "Estado",
            "Lectura"
        ]

        available_columns = [
            col for col in visible_columns
            if col in kpis_df.columns
        ]

        st.dataframe(kpis_df[available_columns], width="stretch")

        with st.expander("Trazabilidad técnica de cálculo"):
            trace_columns = [
                "KPI",
                "Numerador usado",
                "Valor numerador",
                "Fuente numerador",
                "Hoja numerador",
                "Cuenta numerador",
                "Denominador usado",
                "Valor denominador",
                "Fuente denominador",
                "Hoja denominador",
                "Cuenta denominador"
            ]

            available_trace_columns = [
                col for col in trace_columns
                if col in kpis_df.columns
            ]

            st.dataframe(kpis_df[available_trace_columns], width="stretch")


# =========================
# Sidebar
# =========================
with st.sidebar:
    st.markdown(
        """
        <div class="afina-logo">
            <div class="afina-logo-icon">📊</div>
            <div>
                <div class="afina-logo-title">AFINA</div>
                <div class="afina-logo-subtitle">Análisis Financiero</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    section = st.radio(
        "Navegación",
        NAV_OPTIONS,
        key="current_section"
    )

    st.divider()

    if st.session_state.analysis_ready:
        st.success("Análisis activo")
        st.caption(f"Período: {st.session_state.analysis_period}")
        st.caption(f"Industria: {st.session_state.selected_industry}")

        if st.session_state.mapping_completeness:
            st.caption(f"Mapeo: {st.session_state.mapping_completeness['status']}")
    else:
        st.info("Sin análisis activo")

    st.caption("AFINA MVP · GOBLEXA")


# =========================
# 1. Nuevo análisis FP&A
# =========================
if section == "1. Nuevo análisis FP&A":
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">Nuevo Análisis FP&A</div>
            <div class="hero-subtitle">
                Cargá el archivo financiero y confirmá qué hoja representa cada estado contable para generar el contexto del análisis.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="workflow-box">
            <strong>Flujo profesional del análisis:</strong><br>
            1. Subir archivo → 2. Detectar hojas → 3. Mapear estados financieros → 4. Elegir período e industria → 5. Generar análisis FP&A
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "1. Seleccioná el archivo financiero",
        type=["xlsx", "csv"]
    )

    sheet_names = []
    suggested_mapping = {}

    if uploaded_file is not None:
        st.session_state.uploaded_file_name = uploaded_file.name

        if not st.session_state.get("company_name"):
            inferred_company = uploaded_file.name
            for ext in [".xlsx", ".xls", ".csv", ".pdf"]:
                inferred_company = inferred_company.replace(ext, "")
            if inferred_company.endswith(" (1)"):
                inferred_company = inferred_company[:-4]
            st.session_state.company_name = inferred_company.strip() or "Empresa analizada"

        file_name_lower = uploaded_file.name.lower()

        if file_name_lower.endswith(".xlsx"):
            sheet_names = get_excel_sheets(uploaded_file)
            st.session_state.workbook_sheets = sheet_names

            st.markdown(
                f"""
                <div class="success-box">
                    <strong>Archivo Excel detectado correctamente.</strong><br>
                    AFINA encontró <strong>{len(sheet_names)}</strong> hojas disponibles.
                </div>
                """,
                unsafe_allow_html=True
            )

            st.write("Hojas detectadas:")
            st.write(", ".join(sheet_names))

            suggested_mapping = suggest_sheet_mapping(sheet_names)

        elif file_name_lower.endswith(".csv"):
            sheet_names = ["Archivo CSV"]
            st.session_state.workbook_sheets = sheet_names
            suggested_mapping = {
                "balance": NO_USAR,
                "pnl": NO_USAR,
                "cashflow": NO_USAR,
                "ratios": NO_USAR,
                "database": "Archivo CSV"
            }

            st.info("Archivo CSV detectado. Se mapeará como base contable auxiliar.")

    if uploaded_file is not None:
        section_header(
            "2. Mapeo de estados financieros",
            "Confirmá qué hoja corresponde a cada bloque del análisis FP&A."
        )

        sheet_options = [NO_USAR] + sheet_names
        mapping = {}

        col1, col2 = st.columns(2)
        roles = list(STATEMENT_ROLES.keys())

        for index, role in enumerate(roles):
            suggested_sheet = suggested_mapping.get(role, NO_USAR)
            default_index = sheet_options.index(suggested_sheet) if suggested_sheet in sheet_options else 0

            target_col = col1 if index % 2 == 0 else col2

            with target_col:
                mapping[role] = st.selectbox(
                    STATEMENT_ROLES[role],
                    sheet_options,
                    index=default_index,
                    key=f"mapping_{role}"
                )

        completeness = calculate_mapping_completeness(mapping)

        if completeness["score"] >= 90:
            score_color = "green"
            score_dot = "green"
        elif completeness["score"] >= 60:
            score_color = "yellow"
            score_dot = "yellow"
        else:
            score_color = "red"
            score_dot = "red"

        st.subheader("Calidad del mapeo FP&A")

        col1, col2, col3 = st.columns(3)

        with col1:
            kpi_card("Completitud", f"{completeness['score']}%", completeness["status"], score_color, score_dot)
        with col2:
            kpi_card("Estados clave", completeness["required_done"], "Balance + Resultados + Flujo", "blue", "blue")
        with col3:
            kpi_card("Bloques opcionales", completeness["optional_done"], "Ratios + Base auxiliar", "yellow", "yellow")

        st.markdown(
            f"""
            <div class="info-box">
                <strong>Lectura FP&A:</strong><br>
                {completeness["detail"]}
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            selected_period = st.selectbox(
                "3. Seleccioná el período principal a analizar",
                PERIODS,
                index=PERIODS.index("Año 2022")
            )

        with col2:
            selected_analysis_type = st.radio(
                "4. Tipo de análisis",
                ANALYSIS_TYPES,
                horizontal=True
            )

        selected_comparison_period = None

        if selected_analysis_type == "Comparativo":
            comparison_options = [period for period in PERIODS if period != selected_period]
            selected_comparison_period = st.selectbox(
                "Período de comparación",
                comparison_options,
                index=comparison_options.index("Año 2023") if "Año 2023" in comparison_options else 0
            )

        selected_industry = st.selectbox(
            "5. Industria / sector económico",
            INDUSTRIES,
            index=INDUSTRIES.index(st.session_state.selected_industry)
        )

        st.session_state.selected_industry = selected_industry

        can_process = uploaded_file is not None and any(
            sheet != NO_USAR for sheet in mapping.values()
        )

        st.write("")

        if st.button("Generar análisis FP&A", type="primary", disabled=not can_process):
            try:
                documents = load_mapped_financial_documents(uploaded_file, mapping)
                financial_items, financial_items_summary = extract_financial_items(documents)
                kpis, kpis_summary = calculate_kpis(
                    financial_items,
                    industry=selected_industry
                )

                st.session_state.sheet_mapping = mapping
                st.session_state.fpna_documents = documents
                st.session_state.financial_items = financial_items
                st.session_state.financial_items_summary = financial_items_summary
                st.session_state.kpis = kpis
                st.session_state.kpis_summary = kpis_summary
                st.session_state.mapping_completeness = completeness
                st.session_state.analysis_period = selected_period
                st.session_state.comparison_period = selected_comparison_period
                st.session_state.analysis_type = selected_analysis_type
                st.session_state.analysis_ready = True

                st.session_state.fpna_context = {
                    "file_name": uploaded_file.name,
                    "period": selected_period,
                    "comparison_period": selected_comparison_period,
                    "analysis_type": selected_analysis_type,
                    "industry": selected_industry,
                    "mapping": mapping,
                    "completeness": completeness,
                    "documents_summary": documents_summary_table(documents).to_dict(orient="records"),
                    "financial_items_summary": financial_items_summary,
                    "kpis_summary": kpis_summary
                }

                st.markdown(
                    """
                    <div class="success-box">
                        <strong>Análisis FP&A preparado correctamente.</strong><br>
                        AFINA ya tiene mapeados los estados financieros y el contexto base para Dashboard, KPIs, IA e Informe.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            except Exception as e:
                st.error("No se pudo generar el análisis FP&A.")
                st.write("Revisá el archivo, las hojas seleccionadas o intentá mapear menos bloques.")
                st.caption(str(e))

        if not can_process:
            st.caption("Para generar el análisis, seleccioná al menos una hoja en el mapeo FP&A.")

    if st.session_state.analysis_ready and st.session_state.fpna_documents is not None:
        section_header(
            "Resumen del análisis activo",
            "AFINA preparó el archivo como insumo financiero para el análisis ejecutivo."
        )

        context = st.session_state.fpna_context
        completeness = st.session_state.mapping_completeness

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            kpi_card("Archivo", context["file_name"], "Archivo cargado", "blue", "green")
        with col2:
            kpi_card("Período", context["period"], "Período principal", "green", "green")
        with col3:
            kpi_card("Tipo", context["analysis_type"], "Modo de análisis", "blue", "green")
        with col4:
            kpi_card("Mapeo", completeness["status"], "Calidad FP&A", "yellow", "yellow")

        if context["comparison_period"]:
            st.markdown(
                f"""
                <div class="info-box">
                    <strong>Comparación activa:</strong> {context["period"]} vs. {context["comparison_period"]}
                </div>
                """,
                unsafe_allow_html=True
            )

        st.subheader("Estados financieros mapeados")
        summary_df = documents_summary_table(st.session_state.fpna_documents)
        st.dataframe(summary_df, width="stretch")

        render_financial_items_section()
        render_kpis_section(show_trace=True)

        with st.expander("Detalle técnico para desarrollo"):
            for role, doc in st.session_state.fpna_documents.items():
                st.markdown(f"### {doc['role_label']} — {doc['sheet_name']}")
                st.write("Columnas detectadas:")
                st.write(", ".join([str(col) for col in doc["metadata"]["column_names"]]))

                normalized_df = doc["normalization"]["normalized_df"]

                if not normalized_df.empty:
                    st.write("Vista normalizada:")
                    st.dataframe(normalized_df.head(20), width="stretch")
                else:
                    st.warning("No se pudo normalizar esta hoja.")

        st.button(
            "Ir al Dashboard financiero",
            type="secondary",
            on_click=go_to,
            args=("2. Dashboard financiero",)
        )


# =========================
# 2. Dashboard financiero
# =========================
elif section == "2. Dashboard financiero":
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">Dashboard Financiero</div>
            <div class="hero-subtitle">Resumen ejecutivo · Salud financiera · KPIs principales</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not st.session_state.analysis_ready:
        st.markdown(
            """
            <div class="warning-box">
                <strong>No hay análisis FP&A activo.</strong><br>
                Primero cargá un archivo y confirmá el mapeo de estados financieros.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.button(
            "Iniciar nuevo análisis FP&A",
            type="primary",
            on_click=go_to,
            args=("1. Nuevo análisis FP&A",)
        )

    else:
        context = st.session_state.fpna_context
        completeness = st.session_state.mapping_completeness

        st.markdown(
            f"""
            <div class="success-box">
                <strong>Análisis activo:</strong> {context["file_name"]}<br>
                Período: <strong>{context["period"]}</strong> · Tipo: <strong>{context["analysis_type"]}</strong> · Sector: <strong>{context["industry"]}</strong>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.session_state.kpis is None:
            st.warning("El análisis está preparado, pero todavía no hay KPIs calculados.")
        else:
            kpis_df = prepare_kpi_visual_dataframe(st.session_state.kpis)
            score_data = build_health_score(kpis_df)

            section_header(
                "Resumen ejecutivo",
                "Vista rápida del estado financiero general y los KPIs más relevantes."
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                score_color = "green" if score_data["score"] >= 70 else "yellow" if score_data["score"] >= 40 else "red"
                kpi_card(
                    "Score salud financiera",
                    f"{score_data['score']}%",
                    score_data["label"],
                    score_color,
                    score_color
                )

            with col2:
                kpi_card(
                    "Mapeo FP&A",
                    f"{completeness['score']}%",
                    completeness["status"],
                    "green" if completeness["score"] >= 90 else "yellow",
                    "green" if completeness["score"] >= 90 else "yellow"
                )

            with col3:
                kpi_card(
                    "KPIs calculados",
                    st.session_state.kpis_summary["calculated_kpis"],
                    "Indicadores disponibles",
                    "green",
                    "green"
                )

            with col4:
                kpi_card(
                    "Alertas críticas",
                    score_data["red"],
                    "KPIs en rojo",
                    "red" if score_data["red"] > 0 else "green",
                    "red" if score_data["red"] > 0 else "green"
                )

            section_header(
                "KPIs principales",
                "Indicadores clave para lectura rápida de liquidez, rentabilidad, deuda y eficiencia."
            )

            main_kpis = [
                ("current_ratio", "Liquidez corriente"),
                ("roe", "ROE"),
                ("debt_ratio", "Endeudamiento"),
                ("asset_turnover", "Rotación de activos")
            ]

            cols = st.columns(4)

            for i, (code, fallback_label) in enumerate(main_kpis):
                row = kpis_df[kpis_df["Código KPI"] == code]

                with cols[i]:
                    if not row.empty:
                        item = row.iloc[0]
                        color = item.get("Color", "blue")

                        if color not in ["green", "yellow", "red", "blue"]:
                            color = "blue"

                        kpi_card(
                            item["KPI"],
                            item["Valor formateado"],
                            f'{item["Estado"]} · {item["Fuente cálculo"]}',
                            color,
                            color
                        )
                    else:
                        kpi_card(
                            fallback_label,
                            "Sin datos",
                            "No calculado",
                            "yellow",
                            "yellow"
                        )

            section_header(
                "Visualización ejecutiva",
                "Score general y distribución semafórica de los indicadores calculados."
            )

            fig_gauge, _ = build_health_gauge(kpis_df)
            fig_donut = build_status_donut(kpis_df)

            col1, col2 = st.columns(2)

            with col1:
                st.plotly_chart(fig_gauge, width="stretch")

            if fig_donut is not None:
                with col2:
                    st.plotly_chart(fig_donut, width="stretch")

            st.markdown(
                """
                <div class="info-box">
                    <strong>Lectura ejecutiva:</strong><br>
                    Para revisar todos los indicadores, gráficos detallados, tabla ejecutiva y trazabilidad de cálculo,
                    ingresá a la pestaña <strong>3. KPIs</strong>.
                </div>
                """,
                unsafe_allow_html=True
            )
# =========================
# 3. KPIs
# =========================
elif section == "3. KPIs":
    section_header(
        "KPIs financieros",
        "Análisis detallado de indicadores calculados, semáforos, gráficos y trazabilidad FP&A."
    )

    if not st.session_state.analysis_ready:
        st.markdown(
            """
            <div class="warning-box">
                Primero debés preparar un análisis FP&A.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.button(
            "Iniciar nuevo análisis FP&A",
            type="primary",
            on_click=go_to,
            args=("1. Nuevo análisis FP&A",)
        )

    else:
        context = st.session_state.fpna_context

        st.markdown(
            f"""
            <div class="success-box">
                <strong>Análisis FP&A activo:</strong> {context["file_name"]}<br>
                Período: <strong>{context["period"]}</strong> · Tipo: <strong>{context["analysis_type"]}</strong>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader("Estados disponibles para KPIs")
        st.dataframe(
            documents_summary_table(st.session_state.fpna_documents),
            width="stretch"
        )

        render_kpi_executive_visuals(show_tables=True)

        st.divider()

        render_financial_items_section()
# =========================
# 4. Proyecciones
# =========================
elif section == "4. Proyecciones":
    section_header(
        "Proyecciones financieras",
        "Simulación inicial de escenarios para flujo de caja."
    )

    if not st.session_state.analysis_ready:
        st.markdown(
            """
            <div class="warning-box">
                Primero debés preparar un análisis FP&A.
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        col1, col2 = st.columns(2)

        with col1:
            crecimiento_ventas = st.slider("Crecimiento de ventas esperado (%)", -20, 50, 15)
        with col2:
            variacion_costos = st.slider("Variación de costos esperada (%)", -20, 30, -10)

        col1, col2, col3 = st.columns(3)

        with col1:
            kpi_card("Escenario Base", "Activo", "Supuestos actuales", "blue", "yellow")
        with col2:
            kpi_card("Optimista", f"+{crecimiento_ventas}%", "Crecimiento ventas", "green", "green")
        with col3:
            kpi_card("Costos", f"{variacion_costos}%", "Variación estimada", "yellow", "yellow")

        st.markdown(
            """
            <div class="info-box">
                El gráfico de flujo de caja proyectado a 12 meses se integrará en la siguiente etapa.
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================
# 5. Chatbot AFINA
# =========================
elif section == "5. Chatbot AFINA":
    section_header(
        "Chatbot AFINA",
        "Asistente financiero contextualizado sobre los estados cargados."
    )

    if not st.session_state.analysis_ready:
        st.markdown(
            """
            <div class="warning-box">
                Primero debés preparar un análisis FP&A para que el chatbot tenga contexto financiero.
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        context = st.session_state.fpna_context

        st.markdown(
            f"""
            <div class="info-box">
                <strong>Contexto activo del chatbot:</strong><br>
                Archivo: {context["file_name"]}<br>
                Período: {context["period"]}<br>
                Tipo de análisis: {context["analysis_type"]}<br>
                Industria: {context["industry"]}<br>
                Estados mapeados: {len(st.session_state.fpna_documents)}
            </div>
            """,
            unsafe_allow_html=True
        )

        pregunta = st.text_input(
            "Hacé una pregunta financiera",
            placeholder="Ejemplo: ¿por qué mi margen operativo está en rojo?"
        )

        if pregunta:
            st.markdown(
                """
                <div class="info-box">
                    <strong>Respuesta provisoria:</strong><br><br>
                    En la siguiente etapa, AFINA responderá usando los estados financieros mapeados,
                    KPIs calculados, industria seleccionada y período analizado.
                </div>
                """,
                unsafe_allow_html=True
            )


# =========================
# 6. Informe
# =========================
elif section == "6. Informe":
    if st.session_state.get("analysis_ready"):
        render_financial_snapshot_section()
        st.divider()
        render_ai_insights_section()
        st.divider()
        render_fpa_report_template_section()
        st.divider()

    section_header(
        "Informe financiero",
        "Generación de reportes ejecutivos descargables."
    )

    if not st.session_state.analysis_ready:
        st.markdown(
            """
            <div class="warning-box">
                Primero debés preparar un análisis FP&A para generar el informe.
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        context = st.session_state.fpna_context

        st.markdown(
            f"""
            <div class="success-box">
                <strong>Informe listo para etapa de generación:</strong><br>
                Archivo: {context["file_name"]}<br>
                Período: {context["period"]}<br>
                Industria: {context["industry"]}<br>
                Estados financieros mapeados: {len(st.session_state.fpna_documents)}
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            action_card("📘", "PDF ejecutivo", "Portada, KPIs, diagnóstico, acciones y disclaimer.")
        with col2:
            action_card("📝", "Word editable", "Documento con estilos corporativos editable por el usuario.")


# =========================
# 7. Admin básico
# =========================
elif section == "7. Admin básico":
    section_header(
        "Admin básico",
        "Panel inicial para configuración y control del MVP."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        kpi_card("Usuarios activos", "Demo", "Pendiente de autenticación", "blue", "yellow")
    with col2:
        kpi_card("Análisis realizados", "1" if st.session_state.analysis_ready else "0", "Sesión actual", "blue", "green")
    with col3:
        kpi_card("Sectores", "6", "Umbrales configurables", "green", "green")

    col1, col2, col3 = st.columns(3)

    with col1:
        action_card("⚙️", "Editar umbrales", "Modificar criterios de semáforo por industria.")
    with col2:
        action_card("📊", "Ver uso", "Actividad, análisis y reportes generados.")
    with col3:
        action_card("👥", "Gestionar usuarios", "Roles y accesos para una etapa futura.")


st.markdown(
    """
    <div class="footer">
        AFINA MVP · GOBLEXA · Versión inicial para validación comercial y técnica
    </div>
    """,
    unsafe_allow_html=True
)
