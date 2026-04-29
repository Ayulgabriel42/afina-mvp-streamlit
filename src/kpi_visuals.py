import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


COLOR_MAP = {
    "Verde": "#22C55E",
    "Amarillo": "#F59E0B",
    "Rojo": "#EF4444",
    "Sin datos": "#64748B",
    "Sin umbral": "#2563EB"
}


def get_status_color(status):
    return COLOR_MAP.get(str(status), "#2563EB")


def prepare_kpi_visual_dataframe(kpis_df):
    """
    Prepara los KPIs para visualización ejecutiva.
    Usa el valor numérico real calculado por kpi_engine.py.
    """
    if kpis_df is None or kpis_df.empty:
        return pd.DataFrame()

    df = kpis_df.copy()

    if "Valor" not in df.columns:
        df["Valor"] = None

    df["Valor numérico"] = pd.to_numeric(df["Valor"], errors="coerce")
    df["Color HEX"] = df["Estado"].apply(get_status_color)

    order = [
        "Liquidez corriente",
        "Endeudamiento",
        "ROE",
        "ROA",
        "Margen bruto",
        "Margen operativo",
        "Rotación de activos",
        "Ciclo de caja"
    ]

    df["Orden visual"] = df["KPI"].apply(
        lambda x: order.index(x) if x in order else 999
    )

    return df.sort_values("Orden visual").reset_index(drop=True)


def build_health_score(kpis_df):
    """
    Score de salud financiera ponderado:
    - Verde = 100 puntos
    - Amarillo = 50 puntos
    - Rojo = 0 puntos

    Esto evita que una empresa con muchos KPIs amarillos quede artificialmente
    como crítica solo porque tiene pocos indicadores verdes.
    """
    if kpis_df is None or kpis_df.empty:
        return {
            "score": 0,
            "green": 0,
            "yellow": 0,
            "red": 0,
            "total": 0,
            "label": "Sin datos"
        }

    calculated = kpis_df[kpis_df["Fuente cálculo"] != "No calculado"].copy()

    if calculated.empty:
        return {
            "score": 0,
            "green": 0,
            "yellow": 0,
            "red": 0,
            "total": 0,
            "label": "Sin datos"
        }

    green = int((calculated["Estado"] == "Verde").sum())
    yellow = int((calculated["Estado"] == "Amarillo").sum())
    red = int((calculated["Estado"] == "Rojo").sum())
    total = len(calculated)

    points = {
        "Verde": 100,
        "Amarillo": 50,
        "Rojo": 0
    }

    calculated["Puntaje KPI"] = calculated["Estado"].map(points).fillna(0)

    score = round(calculated["Puntaje KPI"].sum() / total, 1) if total else 0

    if score >= 75:
        label = "Salud financiera sólida"
    elif score >= 50:
        label = "Salud financiera moderada"
    elif score >= 30:
        label = "Salud financiera bajo observación"
    else:
        label = "Salud financiera crítica"

    return {
        "score": score,
        "green": green,
        "yellow": yellow,
        "red": red,
        "total": total,
        "label": label
    }

def build_health_gauge(kpis_df):
    score_data = build_health_score(kpis_df)
    score = score_data["score"]

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "%"},
            title={"text": "Score de Salud Financiera"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#2563EB"},
                "steps": [
                    {"range": [0, 40], "color": "#FEE2E2"},
                    {"range": [40, 70], "color": "#FEF3C7"},
                    {"range": [70, 100], "color": "#DCFCE7"},
                ],
                "threshold": {
                    "line": {"color": "#0F172A", "width": 4},
                    "thickness": 0.75,
                    "value": score
                }
            }
        )
    )

    fig.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="white",
        font={"color": "#0F172A"}
    )

    return fig, score_data


def build_status_donut(kpis_df):
    if kpis_df is None or kpis_df.empty:
        return None

    status_df = (
        kpis_df.groupby("Estado")
        .size()
        .reset_index(name="Cantidad")
    )

    fig = px.pie(
        status_df,
        names="Estado",
        values="Cantidad",
        hole=0.55,
        color="Estado",
        color_discrete_map=COLOR_MAP,
        title="Distribución semafórica"
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    fig.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="white",
        legend_title_text=""
    )

    return fig


def build_percentage_kpis_chart(kpis_df):
    if kpis_df is None or kpis_df.empty:
        return None

    percentage_kpis = [
        "Endeudamiento",
        "ROE",
        "ROA",
        "Margen bruto",
        "Margen operativo"
    ]

    df = kpis_df[kpis_df["KPI"].isin(percentage_kpis)].copy()

    if df.empty:
        return None

    df["Valor gráfico"] = df["Valor numérico"] * 100

    fig = px.bar(
        df,
        x="KPI",
        y="Valor gráfico",
        color="Estado",
        color_discrete_map=COLOR_MAP,
        text="Valor formateado",
        title="KPIs porcentuales"
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        height=380,
        yaxis_title="Porcentaje (%)",
        xaxis_title="",
        margin=dict(l=20, r=20, t=55, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend_title_text=""
    )

    return fig


def build_ratio_kpis_chart(kpis_df):
    if kpis_df is None or kpis_df.empty:
        return None

    ratio_kpis = [
        "Liquidez corriente",
        "Rotación de activos"
    ]

    df = kpis_df[kpis_df["KPI"].isin(ratio_kpis)].copy()

    if df.empty:
        return None

    fig = px.bar(
        df,
        x="KPI",
        y="Valor numérico",
        color="Estado",
        color_discrete_map=COLOR_MAP,
        text="Valor formateado",
        title="Ratios financieros"
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        height=360,
        yaxis_title="Veces",
        xaxis_title="",
        margin=dict(l=20, r=20, t=55, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend_title_text=""
    )

    return fig


def build_cash_cycle_chart(kpis_df):
    if kpis_df is None or kpis_df.empty:
        return None

    df = kpis_df[kpis_df["KPI"] == "Ciclo de caja"].copy()

    if df.empty:
        return None

    fig = px.bar(
        df,
        x="KPI",
        y="Valor numérico",
        color="Estado",
        color_discrete_map=COLOR_MAP,
        text="Valor formateado",
        title="Ciclo de caja"
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        height=360,
        yaxis_title="Días",
        xaxis_title="",
        margin=dict(l=20, r=20, t=55, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend_title_text=""
    )

    return fig


def build_kpi_radar_chart(kpis_df):
    """
    Radar normalizado para lectura ejecutiva.
    No busca precisión matemática comparativa, sino visualización relativa.
    """
    if kpis_df is None or kpis_df.empty:
        return None

    df = kpis_df.copy()
    df = df[df["KPI"] != "Ciclo de caja"]

    if df.empty:
        return None

    normalized_values = []

    for _, row in df.iterrows():
        kpi = row["KPI"]
        value = row["Valor numérico"]

        if pd.isna(value):
            normalized_values.append(0)
            continue

        if kpi in ["Endeudamiento"]:
            # Menor es mejor. Se invierte con techo simple.
            normalized = max(0, min(100, (1 - value) * 100))
        elif kpi in ["ROE", "ROA", "Margen bruto", "Margen operativo"]:
            normalized = max(0, min(100, value * 100 * 4))
        elif kpi in ["Liquidez corriente", "Rotación de activos"]:
            normalized = max(0, min(100, value * 50))
        else:
            normalized = max(0, min(100, value * 100))

        normalized_values.append(normalized)

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=normalized_values,
            theta=df["KPI"].tolist(),
            fill="toself",
            name="Desempeño relativo",
            line_color="#2563EB"
        )
    )

    fig.update_layout(
        title="Vista radial de desempeño",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        height=420,
        margin=dict(l=40, r=40, t=60, b=30),
        paper_bgcolor="white"
    )

    return fig
