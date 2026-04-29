# © 2026 ceob68 / Vaultly. All rights reserved.
# Unauthorized copying, distribution or modification is prohibited.

"""
orchestrator.py — CÓNCLAVE Agente Orchestrator

Manages the 5-agent swarm loop:
  - Sequential agent execution with context inheritance
  - Dynamic VRAM swapping between agents
  - Manager intervention injection
  - Session state and draft accumulation
  - Pause / Stop / Restart control
"""

import threading
import json
import os
from typing import Callable, Optional
from dataclasses import dataclass, field

from backend import ai_engine
from backend.database import (
    create_session, save_message, update_session_draft,
    increment_session_cycle, close_session, get_last_n_messages
)

# ─── Agent Configuration ──────────────────────────────────────────────────────

DEFAULT_AGENTS = [
    {
        "id": 0,
        "name": "Arquitecto",
        "role": (
            "Eres el Arquitecto del equipo. Tu tarea es analizar la idea o problema presentado, "
            "proponer la estructura conceptual, las tecnologías adecuadas y el enfoque general. "
            "Sé concreto, visionario y estratégico. Construye sobre el trabajo previo si existe."
        ),
        "color": "#7C3AED",
        "model_override": None,
        "enabled": True,
        "icon": "🏛️",
    },
    {
        "id": 1,
        "name": "Programador",
        "role": (
            "Eres el Programador del equipo. Tu tarea es proponer soluciones de código, "
            "algoritmos, y arquitecturas técnicas concretas. Corrige cualquier error técnico "
            "del Arquitecto y enriquece la propuesta con implementaciones reales. "
            "Usa pseudocódigo o código real según corresponda."
        ),
        "color": "#06B6D4",
        "model_override": None,
        "enabled": True,
        "icon": "💻",
    },
    {
        "id": 2,
        "name": "Seguridad",
        "role": (
            "Eres el Experto en Seguridad del equipo. Tu tarea es auditar la propuesta actual "
            "buscando vulnerabilidades, riesgos, vectores de ataque y problemas de privacidad. "
            "Propón mitigaciones concretas. No seas diplomático — identifica los problemas reales."
        ),
        "color": "#EF4444",
        "model_override": None,
        "enabled": True,
        "icon": "🔒",
    },
    {
        "id": 3,
        "name": "QA / UX",
        "role": (
            "Eres el Experto en QA y UX del equipo. Tu tarea es identificar casos de fallo, "
            "escenarios límite, problemas de usabilidad y experiencia de usuario deficiente. "
            "Sé crítico con el diseño y propón mejoras que hagan el producto más robusto y "
            "amigable para el usuario final."
        ),
        "color": "#F59E0B",
        "model_override": None,
        "enabled": True,
        "icon": "🧪",
    },
    {
        "id": 4,
        "name": "Documentador",
        "role": (
            "Eres el Documentador del equipo. Tu tarea es sintetizar todo lo discutido en esta "
            "iteración, actualizar el borrador acumulativo con los avances y conclusiones clave, "
            "y preparar el resumen que servirá de contexto para el siguiente ciclo. "
            "Sé claro, estructurado y exhaustivo."
        ),
        "color": "#10B981",
        "model_override": None,
        "enabled": True,
        "icon": "📝",
    },
]

# ─── Config persistence path ──────────────────────────────────────────────────

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".conclave_agente")
AGENT_CONFIG_PATH = os.path.join(CONFIG_DIR, "agents_config.json")


def load_agent_config() -> list:
    if os.path.exists(AGENT_CONFIG_PATH):
        try:
            with open(AGENT_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return [dict(a) for a in DEFAULT_AGENTS]


def save_agent_config(agents: list):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(AGENT_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)


# ─── Session Control ──────────────────────────────────────────────────────────

# Thread-safe control flags per session_id
_session_controls: dict[int, dict] = {}
_session_lock = threading.Lock()


def _get_control(session_id: int) -> dict:
    with _session_lock:
        if session_id not in _session_controls:
            _session_controls[session_id] = {
                "stop": threading.Event(),
                "pause": threading.Event(),
                "interventions": [],
                "intervention_lock": threading.Lock(),
            }
        return _session_controls[session_id]


def stop_session(session_id: int):
    ctrl = _get_control(session_id)
    ctrl["stop"].set()
    ctrl["pause"].clear()


def pause_session(session_id: int):
    ctrl = _get_control(session_id)
    ctrl["pause"].set()


def resume_session(session_id: int):
    ctrl = _get_control(session_id)
    ctrl["pause"].clear()


def add_manager_intervention(session_id: int, message: str):
    ctrl = _get_control(session_id)
    with ctrl["intervention_lock"]:
        ctrl["interventions"].append(message)


def cleanup_session(session_id: int):
    with _session_lock:
        _session_controls.pop(session_id, None)


# ─── Prompt Builder ────────────────────────────────────────────────────────────

def _build_agent_prompt(agent: dict, user_topic: str, history: list,
                        current_draft: str, cycle: int,
                        prev_response: str, manager_msg: Optional[str] = None) -> str:
    """Build the full prompt for one agent turn."""

    role = agent["role"]
    name = agent["name"]

    # Summarize recent conversation (last 6 messages)
    recent = history[-6:] if len(history) > 6 else history
    conversation_context = ""
    for msg in recent:
        prefix = f"[{msg['agent_name']}]" if not msg["is_manager"] else "[Manager]"
        conversation_context += f"{prefix}: {msg['content'][:400]}\n\n"

    prompt_parts = [
        f"<|system|>\n{role}\n<|end|>",
        f"<|user|>",
        f"TEMA PRINCIPAL: {user_topic}",
        f"\nCICLO DE DEBATE: {cycle + 1}",
    ]

    if current_draft:
        prompt_parts.append(f"\nBORRADOR ACUMULATIVO ACTUAL:\n{current_draft[:1500]}")

    if conversation_context:
        prompt_parts.append(f"\nCONVERSACIÓN RECIENTE:\n{conversation_context}")

    if prev_response:
        prompt_parts.append(f"\nÚLTIMA CONTRIBUCIÓN (agente anterior):\n{prev_response[:600]}")

    if manager_msg:
        prompt_parts.append(f"\n⚡ INTERVENCIÓN DEL MANAGER: {manager_msg}")
        prompt_parts.append("Esta intervención tiene prioridad máxima — responde a ella directamente.")

    prompt_parts.append(
        f"\nAhora es tu turno como {name}. "
        f"Contribuye con tu perspectiva especializada, construyendo sobre el trabajo previo. "
        f"Sé concreto, profundo y útil. Máximo 400 palabras."
    )
    prompt_parts.append("<|end|>\n<|assistant|>")

    return "\n".join(prompt_parts)


# ─── Main Swarm Runner ─────────────────────────────────────────────────────────

def run_swarm_session(
    session_id: int,
    user_topic: str,
    agents: list,
    token_callback: Callable[[int, str, bool], None],
    status_callback: Callable[[int, str], None],
    log_callback: Callable[[str], None],
    info_callback: Callable[[str], None],
    draft_callback: Callable[[str], None],
):
    """
    Main swarm loop. Runs indefinitely until stop_session() is called.

    Callbacks:
      token_callback(agent_id, token, is_done)
      status_callback(agent_id, status_text)
      log_callback(message)
      info_callback(message)
      draft_callback(draft_text)
    """
    ctrl = _get_control(session_id)
    stop_event = ctrl["stop"]

    active_agents = [a for a in agents if a.get("enabled", True)]
    if not active_agents:
        log_callback("[Orchestrator] ❌ No hay agentes habilitados.")
        return

    log_callback(f"[Orchestrator] 🚀 Sesión #{session_id} iniciada con {len(active_agents)} agentes.")
    info_callback(f"Sesión activa: {len(active_agents)} agentes analizando: «{user_topic[:60]}»")

    cycle = 0
    current_draft = ""
    prev_response = ""

    while not stop_event.is_set():
        # ── Pause check ──
        while ctrl["pause"].is_set() and not stop_event.is_set():
            import time
            time.sleep(0.5)

        if stop_event.is_set():
            break

        log_callback(f"[Orchestrator] ━━━ CICLO {cycle + 1} ━━━")

        for agent in active_agents:
            if stop_event.is_set():
                break

            # Pause check between agents
            while ctrl["pause"].is_set() and not stop_event.is_set():
                import time
                time.sleep(0.5)

            if stop_event.is_set():
                break

            agent_id = agent["id"]
            agent_name = agent["name"]
            model_id = agent.get("model_override") or ai_engine.MODEL_REGISTRY.get(agent_id)

            # Check manager interventions
            manager_msg = None
            with ctrl["intervention_lock"]:
                if ctrl["interventions"]:
                    manager_msg = ctrl["interventions"].pop(0)
                    log_callback(f"[Orchestrator] 📢 Intervención del manager inyectada en {agent_name}")

            # Get session history
            history = get_last_n_messages(session_id, 20)

            # Build prompt
            prompt = _build_agent_prompt(
                agent=agent,
                user_topic=user_topic,
                history=history,
                current_draft=current_draft,
                cycle=cycle,
                prev_response=prev_response,
                manager_msg=manager_msg,
            )

            # ── Load model ──
            status_callback(agent_id, "Cargando modelo...")
            log_callback(f"[Orchestrator] 🔄 Cargando {agent_name} ({model_id})...")
            model, tokenizer = None, None

            try:
                model, tokenizer = ai_engine.load_model_and_tokenizer(
                    model_id=model_id,
                    log_callback=log_callback,
                )
            except Exception as e:
                log_callback(f"[Orchestrator] ❌ Error cargando {agent_name}: {e}")
                status_callback(agent_id, "Error al cargar")
                token_callback(agent_id, f"\n[Error: No se pudo cargar el modelo. Verifica que esté descargado.]\n", True)
                continue

            # ── Generate ──
            status_callback(agent_id, "Generando respuesta...")
            log_callback(f"[Orchestrator] ✍️  {agent_name} generando...")
            full_response = ""

            try:
                def on_token(t):
                    nonlocal full_response
                    full_response += t
                    token_callback(agent_id, t, False)

                full_response = ai_engine.generate_streaming(
                    model=model,
                    tokenizer=tokenizer,
                    prompt=prompt,
                    max_new_tokens=600,
                    temperature=0.72,
                    token_callback=on_token,
                    stop_event=stop_event,
                )
                token_callback(agent_id, "", True)  # Signal done

            except Exception as e:
                log_callback(f"[Orchestrator] ❌ Error generando con {agent_name}: {e}")
                token_callback(agent_id, f"\n[Error durante la generación: {e}]\n", True)
                full_response = ""

            # ── Save message ──
            if full_response.strip():
                save_message(
                    session_id=session_id,
                    agent_id=agent_id,
                    agent_name=agent_name,
                    content=full_response,
                    cycle=cycle,
                )
                prev_response = full_response

            # ── Release VRAM ──
            status_callback(agent_id, "Liberando VRAM...")
            ai_engine.release_model(model, log_callback=log_callback)
            model = None

            status_callback(agent_id, "Esperando turno...")
            log_callback(f"[Orchestrator] ✅ {agent_name} completó ciclo {cycle + 1}.")

        # ── End of cycle: update draft via Documentador's last response ──
        if not stop_event.is_set():
            if prev_response:
                current_draft = _update_draft(current_draft, prev_response, cycle)
                update_session_draft(session_id, current_draft)
                draft_callback(current_draft)

            increment_session_cycle(session_id)
            cycle += 1
            log_callback(f"[Orchestrator] 🔁 Ciclo {cycle} completado. Iniciando ciclo {cycle + 1}...")

    # ── Cleanup ──
    close_session(session_id)
    cleanup_session(session_id)
    log_callback(f"[Orchestrator] 🛑 Sesión #{session_id} finalizada tras {cycle} ciclos.")
    info_callback(f"Sesión finalizada — {cycle} ciclos completados.")

    for agent in active_agents:
        status_callback(agent["id"], "Inactivo")


def _update_draft(current_draft: str, last_response: str, cycle: int) -> str:
    """Append a cycle summary to the draft."""
    separator = f"\n\n{'─' * 50}\n📋 CICLO {cycle + 1} — SÍNTESIS\n{'─' * 50}\n"
    # Trim draft if too long (keep last ~3000 chars)
    combined = current_draft + separator + last_response
    if len(combined) > 6000:
        combined = combined[-6000:]
    return combined
