from flask import Flask, request, jsonify
from anthropic import Anthropic
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools import tools
from workspaces import find_workspace, get_workspace, fetch_device_status, run_microservice
from microservices import get_microservices_catalog, get_microservice_by_id

app = Flask(__name__)

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Estado por conversación (usando conversation_id de Teams)
conversation_history = {}
last_device = {}
last_device_data = {}
last_flx_unique_id = {}
waiting_for_device = {}


def format_device_data(status: dict) -> str:
    lines = []
    for key, value in status.items():
        if value not in (None, "N/A", "", False, 0) or key in ("cpu", "memory", "disk_pct", "sessions", "idle_time"):
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


@app.route("/api", methods=["POST"])
def teams_handler():
    """
    Endpoint llamado por Power Automate cuando el usuario escribe en Teams.
    Espera un JSON con:
      - text: mensaje del usuario
      - conversation_id: ID único de la conversación (para mantener contexto)
    Devuelve:
      - response: texto de respuesta para postear en Teams
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    text = data.get("text", "").strip()
    # conversation_id identifica el hilo/chat en Teams
    conv_id = data.get("conversation_id", "default")

    if not text:
        return jsonify({"error": "No text received"}), 400

    # Si esperamos el nombre del dispositivo, guardarlo
    if waiting_for_device.get(conv_id):
        device_name = text.strip()
        status = fetch_device_status(device_name)
        if not status:
            return jsonify({
                "response": f"❌ No encontré ningún dispositivo con el nombre **{device_name}**. ¿Puedes comprobarlo e intentarlo de nuevo?"
            }), 200

        device_info = find_workspace(device_name)
        if device_info:
            last_flx_unique_id[conv_id] = device_info.get("FLXUniqueID") or device_info.get("FlexxibleMID", "")

        last_device[conv_id] = device_name
        last_device_data[conv_id] = status
        waiting_for_device[conv_id] = False

        return jsonify({
            "response": f"✅ Dispositivo **{device_name}** encontrado y guardado. ¿Qué quieres saber o hacer con él?"
        }), 200

    # Si no hay dispositivo guardado, preguntar
    if conv_id not in last_device:
        waiting_for_device[conv_id] = True
        return jsonify({
            "response": "👋 Para ayudarte necesito saber el nombre de tu equipo. ¿Cómo se llama tu dispositivo? (por ejemplo: **DESKTOP-DEFE7N5**)"
        }), 200

    # Refrescar datos del dispositivo
    status = fetch_device_status(last_device[conv_id])
    if status:
        last_device_data[conv_id] = status

    device_info_str = format_device_data(last_device_data.get(conv_id, {}))
    microservices_catalog = get_microservices_catalog()

    system_prompt = (
        "Eres un asistente IT que responde preguntas y ejecuta acciones en dispositivos. "
        "Responde SIEMPRE en el idioma del usuario. "
        "Interpreta errores tipográficos: 'cepu' es CPU, 'hdd' o 'disco' es disco duro. "
        "Nunca inventes datos. Sé conciso y usa emojis para hacer la respuesta más legible en Microsoft Teams.\n\n"
        f"Dispositivo activo: '{last_device[conv_id]}'\n\n"
        f"Datos actuales del dispositivo:\n{device_info_str}\n\n"
        f"{microservices_catalog}\n\n"
        "Cuando el usuario pida ejecutar una acción en su equipo, usa la tool run_microservice "
        "eligiendo el microservice_id más apropiado del catálogo anterior. "
        "Pide confirmación al usuario antes de ejecutar cualquier acción."
    )

    if conv_id not in conversation_history:
        conversation_history[conv_id] = []
    conversation_history[conv_id].append({"role": "user", "content": text})
    history = conversation_history[conv_id][-10:]

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=600,
            tools=tools,
            tool_choice={"type": "auto"},
            system=system_prompt,
            messages=history
        )

        tool_call = None
        for block in response.content:
            if block.type == "tool_use":
                tool_call = block
                break

        reply = "No se pudo procesar la solicitud."

        if tool_call and tool_call.name == "run_microservice":
            microservice_id = tool_call.input.get("microservice_id")
            microservice_name = tool_call.input.get("microservice_name")
            flx_unique_id = last_flx_unique_id.get(conv_id, "")

            if not flx_unique_id:
                reply = "❌ No tengo el identificador único del dispositivo para ejecutar la acción. Intenta registrar el dispositivo de nuevo."
            else:
                result = run_microservice(
                    microservice_id=microservice_id,
                    flx_unique_id=flx_unique_id,
                    display_name=f"{microservice_name} - FlexxiBot"
                )
                if result:
                    reply = (
                        f"✅ **{microservice_name}** lanzado correctamente en **{last_device[conv_id]}**.\n"
                        f"⏳ El script se está ejecutando en el dispositivo. Puede tardar unos minutos."
                    )
                else:
                    reply = f"❌ No se pudo ejecutar **{microservice_name}**. Comprueba que el dispositivo está online y el agente activo."

        elif tool_call is None:
            for block in response.content:
                if hasattr(block, "text"):
                    reply = block.text
                    break

        conversation_history[conv_id].append({
            "role": "assistant",
            "content": reply
        })

        return jsonify({"response": reply}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"response": "❌ Error interno procesando la solicitud."}), 200


app = app
