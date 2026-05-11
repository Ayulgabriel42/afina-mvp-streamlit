import json
import os

from openai import OpenAI

from src.ai_insights import compact_snapshot_for_ai


DEFAULT_CHAT_MODEL = os.getenv(
    "OPENAI_CHAT_MODEL",
    os.getenv("OPENAI_MODEL", "gpt-5-mini")
)

CHATBOT_MAX_OUTPUT_TOKENS = int(
    os.getenv("OPENAI_CHAT_MAX_OUTPUT_TOKENS", "3500")
)

CHATBOT_SYSTEM_INSTRUCTIONS = """
Sos AFINA, un chatbot financiero especializado en FP&A para empresas.
Actuás como analista financiero senior bajo enfoque NIIF/NIC.

Tu tarea es conversar con el usuario sobre el análisis financiero ya generado por AFINA.
El contexto financiero disponible viene de un JSON validado por el motor de cálculo de AFINA.

Reglas obligatorias:
- Respondé siempre en español profesional, claro y ejecutivo.
- Usá únicamente los datos del snapshot financiero y el historial de conversación provisto.
- No inventes valores, KPIs, cuentas, períodos ni resultados.
- No recalcules KPIs principales si ya vienen calculados por AFINA.
- Si falta información, decilo explícitamente y mencioná qué dato falta.
- Si hay KPIs sin datos, no los completes: marcá que requieren validación o mejora de extracción.
- Distinguí entre hechos calculados, interpretación y recomendación.
- Cuando respondas sobre riesgos o acciones, vinculalos a KPIs concretos cuando existan.
- Evitá prometer auditoría, certificación contable o asesoramiento legal/fiscal definitivo.
- Para recomendaciones o proyecciones, cerrá con un disclaimer breve.
- No cortes la respuesta abruptamente. Cerrá siempre con una frase completa.

Formato recomendado:
1. Respuesta ejecutiva breve.
2. Lectura financiera.
3. Causas probables según KPIs disponibles.
4. Acciones sugeridas.
5. Cautela metodológica o disclaimer, si corresponde.
""".strip()


def _json_dumps_safe(payload):
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


def compact_chat_history(chat_history, max_turns=8):
    if not chat_history:
        return []

    cleaned = []

    for message in chat_history[-max_turns:]:
        role = message.get("role", "")
        content = str(message.get("content", "")).strip()

        if role in ["user", "assistant"] and content:
            cleaned.append({
                "role": role,
                "content": content[:2200],
            })

    return cleaned


def build_chatbot_prompt(snapshot, user_question, chat_history=None):
    compact_snapshot = compact_snapshot_for_ai(snapshot)
    compact_history = compact_chat_history(chat_history)

    return f"""
Contexto financiero validado por AFINA:
{_json_dumps_safe(compact_snapshot)}

Historial reciente de conversación:
{_json_dumps_safe(compact_history)}

Pregunta actual del usuario:
{user_question}

Respondé como Chatbot AFINA usando el contexto financiero anterior.
La respuesta debe ser completa, ordenada y cerrar con una conclusión clara.
""".strip()


def _extract_output_text(response):
    output_text = getattr(response, "output_text", None)

    if output_text:
        return output_text

    try:
        chunks = []

        for item in getattr(response, "output", []) or []:
            for content in getattr(item, "content", []) or []:
                text = getattr(content, "text", None)
                if text:
                    chunks.append(text)

        return "\n".join(chunks).strip()
    except Exception:
        return ""



def generate_chatbot_response(snapshot, user_question, chat_history=None, model=None):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "No se encontró OPENAI_API_KEY. Configurala como variable de entorno o en Streamlit Secrets."
        )

    if not snapshot:
        raise RuntimeError(
            "No hay snapshot financiero disponible. Primero generá el análisis FP&A."
        )

    user_question = str(user_question or "").strip()

    if not user_question:
        raise ValueError("La pregunta del usuario está vacía.")

    selected_model = model or DEFAULT_CHAT_MODEL

    prompt = build_chatbot_prompt(
        snapshot=snapshot,
        user_question=user_question,
        chat_history=chat_history,
    )

    client = OpenAI(api_key=api_key)

    response_kwargs = {
        "model": selected_model,
        "instructions": CHATBOT_SYSTEM_INSTRUCTIONS,
        "input": prompt,
        "max_output_tokens": CHATBOT_MAX_OUTPUT_TOKENS,
    }

    if str(selected_model).startswith("gpt-5"):
        response_kwargs["reasoning"] = {"effort": "low"}
        response_kwargs["text"] = {"verbosity": "medium"}

    response = client.responses.create(**response_kwargs)

    incomplete_reason = None

    if getattr(response, "status", None) == "incomplete":
        incomplete_details = getattr(response, "incomplete_details", None)
        incomplete_reason = getattr(incomplete_details, "reason", None)

    output_text = _extract_output_text(response)

    if not output_text:
        output_text = (
            "AFINA no pudo recuperar una respuesta visible del modelo. "
            "Probá nuevamente o aumentá OPENAI_CHAT_MAX_OUTPUT_TOKENS."
        )

    return {
        "model": selected_model,
        "prompt_tokens_estimate": round((len(prompt) + len(CHATBOT_SYSTEM_INSTRUCTIONS)) / 4),
        "max_output_tokens": CHATBOT_MAX_OUTPUT_TOKENS,
        "incomplete_reason": incomplete_reason,
        "output_text": output_text,
    }
