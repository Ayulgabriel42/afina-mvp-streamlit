import json
import os

from openai import OpenAI


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")


def compact_snapshot_for_ai(snapshot):
    """
    Reduce el JSON financiero para enviar a la IA solo lo necesario.
    La IA no recalcula KPIs: solo interpreta el snapshot.
    """
    if not snapshot:
        return {}

    compact_dimensions = []

    for dim in snapshot.get("dimensions_fpa", []):
        compact_dimensions.append({
            "dimension": dim.get("dimension"),
            "score": dim.get("score"),
            "estado_dimension": dim.get("estado_dimension"),
            "kpis_calculados": dim.get("kpis_calculados"),
            "kpis_pendientes": dim.get("kpis_pendientes"),
            "verdes": dim.get("verdes"),
            "amarillos": dim.get("amarillos"),
            "rojos": dim.get("rojos"),
            "sin_datos": dim.get("sin_datos"),
            "kpis": [
                {
                    "codigo_srs": kpi.get("codigo_srs"),
                    "nombre": kpi.get("nombre"),
                    "valor_formateado": kpi.get("valor_formateado"),
                    "estado": kpi.get("estado"),
                    "lectura": kpi.get("lectura"),
                    "nota_calculo": kpi.get("nota_calculo"),
                }
                for kpi in dim.get("kpis", [])
            ],
        })

    return {
        "analysis_context": snapshot.get("analysis_context", {}),
        "health_score": snapshot.get("health_score", {}),
        "kpi_summary": snapshot.get("kpi_summary", {}),
        "dimensions_fpa": compact_dimensions,
        "alerts": snapshot.get("alerts", []),
        "data_quality_warnings": snapshot.get("data_quality_warnings", []),
        "methodological_notes": snapshot.get("methodological_notes", []),
    }


def build_insights_prompt(compact_snapshot):
    snapshot_json = json.dumps(
        compact_snapshot,
        ensure_ascii=False,
        indent=2,
        default=str,
    )

    return f"""
Sos AFINA, un motor de inteligencia financiera automatizado para análisis FP&A.
Actuá como analista financiero senior bajo enfoque NIIF/NIC.

Tu tarea:
Generar una síntesis consultiva breve para complementar un informe FP&A estructurado.
El informe completo lo arma AFINA con un template fijo. Tu respuesta debe ser solo un bloque breve.

Reglas obligatorias:
- No recalcules KPIs.
- No inventes valores.
- No repitas todo el informe.
- No hagas portada.
- No hagas scorecards.
- No hagas diagnóstico completo por cada dimensión.
- No uses lenguaje coloquial.
- No uses tono alarmista.
- No ocultes KPIs sin datos.
- Redactá en español profesional, ejecutivo y consultivo.
- Máximo 280 palabras.
- Terminá la respuesta con una frase completa.
- No dejes oraciones inconclusas.

Estructura exacta de salida:

## Síntesis consultiva IA

**Lectura estratégica:** Un párrafo breve integrando la situación financiera general.

**Riesgos prioritarios:**
- Máximo 3 riesgos, vinculados a KPIs concretos.

**Acciones sugeridas:**
- Máximo 3 acciones ejecutivas y concretas.

**Cautela metodológica:** Una oración breve sobre limitaciones de datos, KPIs no calculados o diferencias metodológicas.

Snapshot financiero:
{snapshot_json}
""".strip()


def generate_ai_insights(snapshot, model=None):
    """
    Genera una síntesis consultiva breve usando OpenAI Responses API.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "No se encontró OPENAI_API_KEY. Configurala como variable de entorno o en Streamlit Secrets."
        )

    model = model or DEFAULT_MODEL

    compact_snapshot = compact_snapshot_for_ai(snapshot)
    prompt = build_insights_prompt(compact_snapshot)

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=model,
        input=prompt,
        max_output_tokens=850,
    )

    return {
        "model": model,
        "prompt_tokens_estimate": round(len(prompt) / 4),
        "output_text": response.output_text,
    }
