# © 2026 ceob68 / Vaultly. All rights reserved.
# Unauthorized copying, distribution or modification is prohibited.

"""
ai_worker.py — QThread wrapper for the swarm orchestrator.

Decouples inference (potentially infinite loop) from the PySide6 UI thread.
All communication back to the UI happens via Qt signals.
"""

from PySide6.QtCore import QThread, Signal

from backend import orchestrator


class SwarmWorker(QThread):
    """
    Runs the full multi-agent swarm session in a background thread.

    Signals:
      token_signal(agent_id: int, token: str, is_done: bool)
        — Emitted for each streamed token and once with is_done=True per agent turn.

      status_signal(agent_id: int, status_text: str)
        — Status update for each agent card (e.g., "Cargando modelo...", "Generando...").

      log_signal(message: str)
        — System/diagnostic log messages.

      info_signal(message: str)
        — High-level info for the status bar.

      draft_signal(draft_text: str)
        — Emitted when the cumulative draft is updated (end of each cycle).

      finished_signal()
        — Emitted when the swarm loop exits (stop requested or error).
    """

    token_signal   = Signal(int, str, bool)
    status_signal  = Signal(int, str)
    log_signal     = Signal(str)
    info_signal    = Signal(str)
    draft_signal   = Signal(str)
    finished_signal = Signal()

    def __init__(self, session_id: int, user_topic: str, agents: list, parent=None):
        super().__init__(parent)
        self.session_id = session_id
        self.user_topic = user_topic
        self.agents = agents

    def run(self):
        """Called by QThread.start() — runs in background thread."""
        try:
            orchestrator.run_swarm_session(
                session_id=self.session_id,
                user_topic=self.user_topic,
                agents=self.agents,
                token_callback=self._on_token,
                status_callback=self._on_status,
                log_callback=self._on_log,
                info_callback=self._on_info,
                draft_callback=self._on_draft,
            )
        except Exception as e:
            self.log_signal.emit(f"[SwarmWorker] ❌ Error inesperado: {e}")
        finally:
            self.finished_signal.emit()

    def stop(self):
        """Request graceful stop of the swarm session."""
        orchestrator.stop_session(self.session_id)

    def pause(self):
        """Pause the swarm session."""
        orchestrator.pause_session(self.session_id)

    def resume(self):
        """Resume a paused swarm session."""
        orchestrator.resume_session(self.session_id)

    def inject_manager(self, message: str):
        """Inject a manager intervention into the active session."""
        orchestrator.add_manager_intervention(self.session_id, message)

    # ── Internal callbacks (called from background thread via Qt signals) ───

    def _on_token(self, agent_id: int, token: str, is_done: bool):
        self.token_signal.emit(agent_id, token, is_done)

    def _on_status(self, agent_id: int, status: str):
        self.status_signal.emit(agent_id, status)

    def _on_log(self, message: str):
        self.log_signal.emit(message)

    def _on_info(self, message: str):
        self.info_signal.emit(message)

    def _on_draft(self, draft: str):
        self.draft_signal.emit(draft)
