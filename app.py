import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.loader import get_excel_sheets, load_financial_file
from src.analyzer import analyze_financial_dataframe
from src.normalizer import normalize_financial_dataframe
from src.extractor import extract_financial_items
from src.kpi_engine import calculate_kpis
from src.statement_mapper import (
    NO_USAR,
    STATEMENT_ROLES,
    suggest_sheet_mapping,
    calculate_mapping_completeness,
)

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
    "analysis_ready": False,
    "current_section": "1. Nuevo análisis FP&A"
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

NAV_OPTIONS = [
    "1. Nuevo análisis FP&A",
    "2. Dashboard financiero",
    "3. KPIs / Industria",
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
            <div class="hero-subtitle">KPIs financieros · Semáforos por industria · Reportes ejecutivos</div>
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
                Período: <strong>{context["period"]}</strong> · Tipo: <strong>{context["analysis_type"]}</strong> · Industria: <strong>{context["industry"]}</strong>
            </div>
            """,
            unsafe_allow_html=True
        )

        section_header(
            "Base FP&A preparada",
            "AFINA ya cuenta con los estados financieros mapeados para comenzar el cálculo de indicadores."
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            kpi_card(
                "Completitud FP&A",
                f"{completeness['score']}%",
                completeness["status"],
                "green" if completeness["score"] >= 90 else "yellow",
                "green" if completeness["score"] >= 90 else "yellow"
            )
        with col2:
            kpi_card("Estados cargados", len(st.session_state.fpna_documents), "Bloques financieros disponibles", "blue", "blue")
        with col3:
            kpi_card("Industria", context["industry"], "Umbrales futuros", "yellow", "yellow")
        with col4:
            kpi_card("Estado", "Preparado", "Listo para motor KPI", "green", "green")

        st.subheader("Fuentes utilizadas por AFINA")
        st.dataframe(documents_summary_table(st.session_state.fpna_documents), width="stretch")

        render_financial_items_section()

        section_header(
            "KPIs principales",
            "Indicadores calculados desde las partidas detectadas por AFINA."
        )

        if st.session_state.kpis is not None:
            kpis_df = st.session_state.kpis

            main_kpis = [
                ("current_ratio", "Liquidez corriente"),
                ("roe", "ROE"),
                ("debt_ratio", "Endeudamiento"),
                ("asset_turnover", "Rotación de activos")
            ]

            col1, col2, col3, col4 = st.columns(4)
            cols = [col1, col2, col3, col4]

            for i, (code, label) in enumerate(main_kpis):
                row = kpis_df[kpis_df["Código KPI"] == code]

                with cols[i]:
                    if not row.empty:
                        item = row.iloc[0]
                        color = item["Color"] if item["Color"] in ["green", "yellow", "red", "blue"] else "blue"
                        kpi_card(
                            label,
                            item["Valor formateado"],
                            item["Estado"],
                            color,
                            color
                        )
                    else:
                        kpi_card(label, "Sin datos", "No calculado", "yellow", "yellow")

            render_kpis_section(show_trace=False)
        else:
            st.warning("Todavía no hay KPIs calculados.")

        col1, col2 = st.columns(2)

        with col1:
            section_header(
                "📈 Ratios Financieros vs. Objetivos",
                "Comparación visual entre estado actual y referencia esperada."
            )
            st.plotly_chart(build_bar_chart(), width="stretch")

        with col2:
            section_header(
                "🧩 Composición de Activos",
                "Distribución inicial estimada para el tablero demostrativo."
            )
            st.plotly_chart(build_pie_chart(), width="stretch")


# =========================
# 3. KPIs / Industria
# =========================
elif section == "3. KPIs / Industria":
    section_header(
        "KPIs / Industria",
        "Selección de industria y preparación de semáforos financieros."
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
        industry = st.selectbox(
            "Industria",
            INDUSTRIES,
            index=INDUSTRIES.index(st.session_state.selected_industry)
        )

        st.session_state.selected_industry = industry
        st.session_state.fpna_context["industry"] = industry

        st.markdown(
            f"""
            <div class="success-box">
                <strong>Industria seleccionada:</strong> {industry}<br>
                En la siguiente etapa, esta selección recalculará los semáforos de los KPIs.
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            action_card("🧪", "Sector Químico", "Capital de trabajo, margen operativo y estructura de deuda.")
        with col2:
            action_card("💻", "SaaS / Tecnología", "Margen, crecimiento, eficiencia y liquidez.")
        with col3:
            action_card("🏭", "Manufactura", "Activos, inventario, costos y rentabilidad.")

        st.subheader("Estados disponibles para KPIs")
        st.dataframe(documents_summary_table(st.session_state.fpna_documents), width="stretch")

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
