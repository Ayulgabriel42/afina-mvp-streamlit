import streamlit as st
import pandas as pd

# =========================
# Configuración general
# =========================
st.set_page_config(
    page_title="AFINA MVP - GOBLEXA",
    page_icon="📊",
    layout="wide"
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

# =========================
# Sidebar
# =========================
st.sidebar.title("AFINA MVP")
st.sidebar.caption("Analista Financiero Inteligente")

section = st.sidebar.radio(
    "Navegación",
    [
        "1. Dashboard financiero",
        "2. Carga de archivo",
        "3. Análisis por industria",
        "4. Proyecciones",
        "5. Chatbot AFINA",
        "6. Informe",
        "7. Admin básico"
    ]
)

st.sidebar.divider()
st.sidebar.info("MVP desarrollado en Streamlit para validación inicial de AFINA.")

# =========================
# Header
# =========================
st.title("AFINA - Analista Financiero Inteligente")
st.caption("MVP financiero desarrollado por GOBLEXA")

# =========================
# 1. Dashboard financiero
# =========================
if section == "1. Dashboard financiero":
    st.header("Dashboard financiero")

    if st.session_state.dataframe is None:
        st.warning("Todavía no cargaste ningún archivo financiero.")
        st.write(
            "Para comenzar, ingresá a **Carga de archivo** y subí un archivo Excel o CSV. "
            "Luego AFINA mostrará los KPIs, semáforos y score de salud financiera."
        )
    else:
        st.success(f"Archivo cargado: {st.session_state.file_name}")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Score financiero", "Pendiente")
        col2.metric("KPIs calculados", "Pendiente")
        col3.metric("Industria", st.session_state.selected_industry)
        col4.metric("Estado", "En análisis")

        st.subheader("Vista previa de datos cargados")
        st.dataframe(st.session_state.dataframe.head(20), use_container_width=True)

# =========================
# 2. Carga de archivo
# =========================
elif section == "2. Carga de archivo":
    st.header("Carga de archivo")

    uploaded_file = st.file_uploader(
        "Subí un archivo financiero en formato Excel o CSV",
        type=["xlsx", "csv"]
    )

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.session_state.dataframe = df
            st.session_state.file_name = uploaded_file.name

            st.success("Archivo procesado correctamente.")
            st.write(f"Nombre del archivo: **{uploaded_file.name}**")
            st.write(f"Filas detectadas: **{df.shape[0]}**")
            st.write(f"Columnas detectadas: **{df.shape[1]}**")

            st.subheader("Vista previa")
            st.dataframe(df.head(20), use_container_width=True)

        except Exception as e:
            st.error("No se pudo procesar el archivo.")
            st.write("Revisá que el archivo sea un Excel o CSV válido.")

# =========================
# 3. Análisis por industria
# =========================
elif section == "3. Análisis por industria":
    st.header("Análisis por industria")

    industry = st.selectbox(
        "Seleccioná la industria",
        [
            "Sector Químico",
            "SaaS / Tecnología",
            "Manufactura",
            "Retail / Comercio",
            "Salud / Farmacia",
            "Servicios Financieros"
        ],
        index=0
    )

    st.session_state.selected_industry = industry

    st.success(f"Industria seleccionada: {industry}")
    st.info("En la próxima etapa, los semáforos de KPIs se recalcularán según esta industria.")

# =========================
# 4. Proyecciones
# =========================
elif section == "4. Proyecciones":
    st.header("Proyecciones financieras")

    st.info("Módulo pendiente de desarrollo.")

    crecimiento_ventas = st.slider("Crecimiento de ventas esperado (%)", -20, 50, 10)
    variacion_costos = st.slider("Variación de costos esperada (%)", -20, 30, 0)

    st.write(f"Crecimiento de ventas seleccionado: **{crecimiento_ventas}%**")
    st.write(f"Variación de costos seleccionada: **{variacion_costos}%**")

# =========================
# 5. Chatbot AFINA
# =========================
elif section == "5. Chatbot AFINA":
    st.header("Chatbot AFINA")

    st.info("Módulo pendiente de integración con IA.")

    pregunta = st.text_input("Hacé una pregunta financiera")

    if pregunta:
        st.write("Respuesta provisoria:")
        st.write(
            "En esta etapa, el chatbot todavía no está conectado al motor financiero. "
            "Luego responderá usando los datos reales cargados por el usuario."
        )

# =========================
# 6. Informe
# =========================
elif section == "6. Informe":
    st.header("Informe financiero")

    st.info("Módulo pendiente de generación PDF / Word.")

    if st.session_state.dataframe is None:
        st.warning("Primero debés cargar un archivo financiero.")
    else:
        st.success("Ya hay datos cargados para generar un informe en próximas etapas.")

# =========================
# 7. Admin básico
# =========================
elif section == "7. Admin básico":
    st.header("Admin básico")

    st.info("Panel administrativo inicial.")

    st.write("Funciones futuras:")
    st.write("- Visualizar cantidad de análisis realizados")
    st.write("- Editar umbrales por industria")
    st.write("- Gestionar configuraciones básicas del MVP")
