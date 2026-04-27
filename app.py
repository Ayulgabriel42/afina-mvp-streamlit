import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.loader import get_excel_sheets, load_financial_file
from src.analyzer import analyze_financial_dataframe

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
if "dataframe" not in st.session_state:
    st.session_state.dataframe = None

if "file_name" not in st.session_state:
    st.session_state.file_name = None

if "selected_industry" not in st.session_state:
    st.session_state.selected_industry = "Sector Químico"

if "file_metadata" not in st.session_state:
    st.session_state.file_metadata = None

if "analysis_period" not in st.session_state:
    st.session_state.analysis_period = None

if "comparison_period" not in st.session_state:
    st.session_state.comparison_period = None

if "analysis_type" not in st.session_state:
    st.session_state.analysis_type = None

if "analysis_ready" not in st.session_state:
    st.session_state.analysis_ready = False

if "analysis_context" not in st.session_state:
    st.session_state.analysis_context = None

if "financial_analysis" not in st.session_state:
    st.session_state.financial_analysis = None

if "current_section" not in st.session_state:
    st.session_state.current_section = "1. Nuevo análisis"

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
    "Año 2021"
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
        [
            "1. Nuevo análisis",
            "2. Dashboard financiero",
            "3. KPIs / Industria",
            "4. Proyecciones",
            "5. Chatbot AFINA",
            "6. Informe",
            "7. Admin básico"
        ],
        key="current_section"
    )

    st.divider()

    if st.session_state.analysis_ready:
        st.success("Análisis activo")
        st.caption(st.session_state.file_name)
        st.caption(f"Período: {st.session_state.analysis_period}")
        st.caption(f"Industria: {st.session_state.selected_industry}")
    else:
        st.info("Sin análisis activo")

    st.caption("AFINA MVP · GOBLEXA")

# =========================
# 1. Nuevo análisis
# =========================
if section == "1. Nuevo análisis":
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">Nuevo Análisis Financiero</div>
            <div class="hero-subtitle">Cargá un archivo, elegí hoja, período, tipo de análisis e industria para preparar el contexto de AFINA.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="workflow-box">
            <strong>Flujo del análisis:</strong><br>
            1. Subir archivo financiero → 2. Elegir hoja → 3. Elegir período → 4. Elegir tipo de análisis → 5. Procesar análisis
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "1. Seleccioná el archivo financiero",
        type=["xlsx", "csv"]
    )

    selected_sheet = None

    if uploaded_file is not None:
        file_name_lower = uploaded_file.name.lower()

        if file_name_lower.endswith(".xlsx"):
            sheets = get_excel_sheets(uploaded_file)

            if sheets:
                selected_sheet = st.selectbox(
                    "2. Seleccioná la hoja del Excel a procesar",
                    sheets
                )
                st.caption(f"Hojas detectadas: {', '.join(sheets)}")
            else:
                st.warning("No se pudieron detectar hojas en el archivo Excel.")

        elif file_name_lower.endswith(".csv"):
            st.info("Archivo CSV detectado. No requiere selección de hoja.")

    col1, col2 = st.columns(2)

    with col1:
        selected_period = st.selectbox(
            "3. Seleccioná el período a analizar",
            PERIODS,
            index=PERIODS.index("Año 2024")
        )

    with col2:
        selected_analysis_type = st.radio(
            "4. Tipo de análisis",
            ANALYSIS_TYPES,
            horizontal=True
        )

    selected_comparison_period = None

    if selected_analysis_type == "Comparativo":
        selected_comparison_period = st.selectbox(
            "Período de comparación",
            [period for period in PERIODS if period != selected_period],
            index=0
        )

    selected_industry = st.selectbox(
        "5. Industria / sector económico",
        INDUSTRIES,
        index=INDUSTRIES.index(st.session_state.selected_industry)
    )

    st.session_state.selected_industry = selected_industry

    can_process = uploaded_file is not None

    if uploaded_file is not None and uploaded_file.name.lower().endswith(".xlsx") and selected_sheet is None:
        can_process = False

    st.write("")

    if st.button("Procesar análisis", type="primary", disabled=not can_process):
        try:
            df, metadata = load_financial_file(
                uploaded_file,
                sheet_name=selected_sheet
            )

            st.session_state.dataframe = df
            st.session_state.file_name = metadata["file_name"]
            st.session_state.file_metadata = metadata
            st.session_state.analysis_period = selected_period
            st.session_state.comparison_period = selected_comparison_period
            st.session_state.analysis_type = selected_analysis_type
            st.session_state.analysis_ready = True

            st.session_state.analysis_context = {
                "file_name": metadata["file_name"],
                "file_type": metadata["file_type"],
                "sheet_name": metadata["sheet_name"],
                "rows": metadata["rows"],
                "columns": metadata["columns"],
                "period": selected_period,
                "comparison_period": selected_comparison_period,
                "analysis_type": selected_analysis_type,
                "industry": selected_industry,
                "column_names": metadata["column_names"]
            }

            # Preanálisis financiero inicial
            st.session_state.financial_analysis = analyze_financial_dataframe(
                df,
                metadata=metadata
            )

            st.markdown(
                """
                <div class="success-box">
                    <strong>Análisis preparado correctamente.</strong><br>
                    Los datos quedaron cargados como contexto principal para Dashboard, KPIs, Proyecciones, Chatbot e Informe.
                </div>
                """,
                unsafe_allow_html=True
            )

        except Exception:
            st.error("No se pudo procesar el archivo.")
            st.write("Revisá que sea un Excel o CSV válido y que la hoja seleccionada tenga datos.")

    if not can_process:
        st.caption("Para procesar, primero subí un archivo válido.")

    if st.session_state.analysis_ready and st.session_state.analysis_context is not None:
        context = st.session_state.analysis_context

        st.subheader("Resumen del análisis activo")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            kpi_card("Archivo", context["file_name"], "Archivo cargado", "blue", "green")
        with col2:
            kpi_card("Período", context["period"], "Período seleccionado", "green", "green")
        with col3:
            kpi_card("Tipo", context["analysis_type"], "Modo de análisis", "blue", "green")
        with col4:
            kpi_card("Industria", context["industry"], "Sector seleccionado", "yellow", "yellow")

        if context["comparison_period"]:
            st.markdown(
                f"""
                <div class="info-box">
                    <strong>Comparación activa:</strong> {context["period"]} vs. {context["comparison_period"]}
                </div>
                """,
                unsafe_allow_html=True
            )

        st.subheader("Datos detectados")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            kpi_card("Tipo archivo", context["file_type"], "Formato procesado", "blue", "green")
        with col2:
            kpi_card("Hoja", context["sheet_name"] or "No aplica", "Hoja procesada", "green", "green")
        with col3:
            kpi_card("Filas", context["rows"], "Registros detectados", "blue", "green")
        with col4:
            kpi_card("Columnas", context["columns"], "Campos detectados", "blue", "green")

        st.subheader("Columnas detectadas")
        st.write(", ".join([str(col) for col in context["column_names"]]))

        st.subheader("Vista previa del archivo")
        st.dataframe(st.session_state.dataframe.head(20), width="stretch")

        if st.session_state.financial_analysis is not None:
            analysis = st.session_state.financial_analysis

            st.subheader("Preanálisis generado")

            col1, col2, col3 = st.columns(3)

            with col1:
                kpi_card("Score detección", f"{analysis['detection_score']}%", analysis["status"], "blue", "green")
            with col2:
                kpi_card("Coincidencias", analysis["total_matches"], "Partidas encontradas", "green", "green")
            with col3:
                kpi_card("Categorías", len(analysis["detected_categories"]), "Grupos detectados", "yellow", "yellow")

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
                <strong>No hay análisis activo.</strong><br>
                Primero iniciá un nuevo análisis financiero cargando un archivo y seleccionando período, tipo de análisis e industria.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.button(
            "Iniciar nuevo análisis",
            type="primary",
            on_click=go_to,
            args=("1. Nuevo análisis",)
        )

    else:
        context = st.session_state.analysis_context

        st.markdown(
            f"""
            <div class="success-box">
                <strong>Análisis activo:</strong> {context["file_name"]}<br>
                Período: <strong>{context["period"]}</strong> · Tipo: <strong>{context["analysis_type"]}</strong> · Industria: <strong>{context["industry"]}</strong>
            </div>
            """,
            unsafe_allow_html=True
        )

        analysis = st.session_state.financial_analysis

        if analysis is not None:
            section_header(
                "Preanálisis financiero detectado",
                "AFINA realizó una primera lectura del archivo para identificar partidas financieras y calidad de datos."
            )

            score = analysis["detection_score"]
            total_matches = analysis["total_matches"]
            detected_categories = analysis["detected_categories"]
            quality = analysis["quality"]

            if score >= 70:
                score_color = "green"
                score_dot = "green"
            elif score >= 40:
                score_color = "yellow"
                score_dot = "yellow"
            else:
                score_color = "red"
                score_dot = "red"

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                kpi_card("Score de detección", f"{score}%", analysis["status"], score_color, score_dot)
            with col2:
                kpi_card("Coincidencias", total_matches, "Partidas financieras encontradas", "blue", "blue")
            with col3:
                kpi_card("Categorías", len(detected_categories), "Grupos financieros detectados", "green", "green")
            with col4:
                kpi_card("Celdas vacías", f"{quality['empty_percentage']}%", "Calidad estructural del archivo", "yellow", "yellow")

            st.markdown(
                f"""
                <div class="info-box">
                    <strong>Diagnóstico inicial:</strong><br>
                    {analysis["status_detail"]}
                </div>
                """,
                unsafe_allow_html=True
            )

            if detected_categories:
                st.subheader("Categorías financieras detectadas")
                st.write(", ".join(detected_categories))

            if quality["warnings"]:
                st.subheader("Alertas de calidad de datos")
                for warning in quality["warnings"]:
                    st.warning(warning)

            detection_rows = []

            for category, data in analysis["detections"].items():
                for match in data["matches"]:
                    detection_rows.append({
                        "Categoría": category,
                        "Fila": match["fila"],
                        "Coincidencia": match["coincidencia"],
                        "Detalle detectado": match["detalle"]
                    })

            if detection_rows:
                st.subheader("Ejemplos de cuentas detectadas")
                st.dataframe(pd.DataFrame(detection_rows), width="stretch")

        st.write("")

        section_header(
            "KPIs demostrativos",
            "Estos valores todavía son referenciales. En el siguiente módulo serán reemplazados por cálculos reales."
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            kpi_card("Ratio de Liquidez", "0.75", "Capacidad de pago a corto plazo", "red", "red")
        with col2:
            kpi_card("Rentabilidad ROE", "5.8%", "Retorno sobre patrimonio", "red", "red")
        with col3:
            kpi_card("Nivel de Endeudamiento", "18.2%", "Deuda total / Activos totales", "green", "green")
        with col4:
            kpi_card("Rotación de Activos", "0.7x", "Eficiencia en uso de activos", "red", "red")

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

        section_header("Acciones rápidas", "Accesos principales para completar el flujo de demo.")

        col1, col2, col3 = st.columns(3)

        with col1:
            action_card("📤", "Nuevo análisis", "Cargar otro archivo o período financiero.")
        with col2:
            action_card("🤖", "Consultar AFINA", "Preguntar causas, riesgos y recomendaciones al chatbot.")
        with col3:
            action_card("📄", "Generar informe", "Descargar un reporte ejecutivo en PDF o Word.")

# =========================
# 3. KPIs / Industria
# =========================
elif section == "3. KPIs / Industria":
    section_header("KPIs / Análisis por industria", "Selección de industria y preparación de semáforos financieros.")

    if not st.session_state.analysis_ready:
        st.markdown(
            """
            <div class="warning-box">
                Primero debés preparar un nuevo análisis para calcular KPIs.
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
        st.session_state.analysis_context["industry"] = industry

        st.markdown(
            f"""
            <div class="success-box">
                <strong>Industria seleccionada:</strong> {industry}<br>
                En la siguiente etapa, esta selección recalculará los semáforos de los indicadores.
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

        col1, col2, col3 = st.columns(3)

        with col1:
            action_card("🛒", "Retail / Comercio", "Rotación, liquidez, inventario y caja.")
        with col2:
            action_card("💊", "Salud / Farmacia", "Stock, flujo operativo y estructura financiera.")
        with col3:
            action_card("🏦", "Servicios Financieros", "Riesgo, capital y rentabilidad.")

# =========================
# 4. Proyecciones
# =========================
elif section == "4. Proyecciones":
    section_header("Proyecciones financieras", "Simulación inicial de escenarios para flujo de caja.")

    if not st.session_state.analysis_ready:
        st.markdown(
            """
            <div class="warning-box">
                Primero debés preparar un nuevo análisis para generar proyecciones.
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
    section_header("Chatbot AFINA", "Asistente financiero contextualizado sobre los datos cargados.")

    if not st.session_state.analysis_ready:
        st.markdown(
            """
            <div class="warning-box">
                Primero debés preparar un nuevo análisis para que el chatbot tenga contexto financiero.
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        context = st.session_state.analysis_context

        st.markdown(
            f"""
            <div class="info-box">
                <strong>Contexto activo del chatbot:</strong><br>
                Archivo: {context["file_name"]}<br>
                Período: {context["period"]}<br>
                Tipo de análisis: {context["analysis_type"]}<br>
                Industria: {context["industry"]}
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
                    En la siguiente etapa, AFINA responderá usando los KPIs calculados,
                    la industria seleccionada, el período analizado y el contexto del archivo cargado.
                </div>
                """,
                unsafe_allow_html=True
            )

# =========================
# 6. Informe
# =========================
elif section == "6. Informe":
    section_header("Informe financiero", "Generación de reportes ejecutivos descargables.")

    if not st.session_state.analysis_ready:
        st.markdown(
            """
            <div class="warning-box">
                Primero debés preparar un nuevo análisis para generar el informe.
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        context = st.session_state.analysis_context

        st.markdown(
            f"""
            <div class="success-box">
                <strong>Informe listo para etapa de generación:</strong><br>
                Archivo: {context["file_name"]}<br>
                Período: {context["period"]}<br>
                Industria: {context["industry"]}
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
    section_header("Admin básico", "Panel inicial para configuración y control del MVP.")

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
