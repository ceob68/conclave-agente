# © 2026 ceob68 / Vaultly. All rights reserved.
# Unauthorized copying, distribution or modification is prohibited.

"""
main_window.py — CÓNCLAVE Agente Main Window

Three-panel layout:
  LEFT   — Agent cards with status indicators
  CENTER — Live chat with streaming tokens
  RIGHT  — Cumulative draft panel

Top header bar with logo + controls (Start, Pause, Stop)
Bottom status bar with session info
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QFrame, QLabel, QVBoxLayout,
    QHBoxLayout, QPushButton, QSplitter, QScrollArea,
    QTextEdit, QInputDialog, QMessageBox, QMenuBar, QMenu,
    QStatusBar, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QAction, QIcon, QFont

from gui.components import AgentCard, ChatBubble, DraftPanel
from gui.app_style import AGENT_COLORS
from gui.ai_worker import SwarmWorker
from gui.settings_dialog import SettingsDialog, load_settings, get_hf_token
from backend.orchestrator import load_agent_config, save_agent_config, DEFAULT_AGENTS
from backend.database import create_session, get_all_sessions


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CÓNCLAVE Agente  v1.0")
        self.setMinimumSize(900, 600)
        self.resize(1280, 820)

        self._agents = load_agent_config()
        self._worker: SwarmWorker | None = None
        self._current_session_id: int | None = None
        self._cycle_count = 0
        self._is_running = False
        self._is_paused = False
        self._current_bubbles: dict[int, ChatBubble] = {}

        # Apply HuggingFace token from settings to environment immediately
        import os
        hf_token = get_hf_token()
        if hf_token:
            os.environ["HF_TOKEN"] = hf_token
            os.environ["HUGGING_FACE_HUB_TOKEN"] = hf_token

        self._setup_menu()
        self._setup_ui()
        self._setup_status_bar()

        # GPU + token check after UI is built
        QTimer.singleShot(600, self._check_gpu_on_startup)

    # ─── Menu ─────────────────────────────────────────────────────────────────

    def _setup_menu(self):
        menubar = self.menuBar()

        # Sesión
        session_menu = menubar.addMenu("Sesión")
        act_new = QAction("🆕  Nueva Sesión", self)
        act_new.setShortcut("Ctrl+N")
        act_new.triggered.connect(self._start_new_session)
        session_menu.addAction(act_new)

        act_history = QAction("📂  Historial de Sesiones", self)
        act_history.triggered.connect(self._show_history)
        session_menu.addAction(act_history)
        session_menu.addSeparator()

        act_exit = QAction("❌  Salir", self)
        act_exit.triggered.connect(self.close)
        session_menu.addAction(act_exit)

        # Agentes
        agents_menu = menubar.addMenu("Agentes")
        act_customize = QAction("✏️  Personalizar Agentes", self)
        act_customize.triggered.connect(self._open_customization)
        agents_menu.addAction(act_customize)

        act_reset = QAction("🔄  Restaurar Configuración por Defecto", self)
        act_reset.triggered.connect(self._reset_agent_config)
        agents_menu.addAction(act_reset)

        # Herramientas
        tools_menu = menubar.addMenu("Herramientas")
        act_settings = QAction("⚙️  Configuración y Descarga de Modelos", self)
        act_settings.setShortcut("Ctrl+,")
        act_settings.triggered.connect(self._open_settings)
        tools_menu.addAction(act_settings)
        tools_menu.addSeparator()
        act_diag = QAction("🔬  Diagnóstico del Sistema", self)
        act_diag.triggered.connect(self._open_diagnosis)
        tools_menu.addAction(act_diag)

        act_export = QAction("💾  Exportar Draft", self)
        act_export.triggered.connect(self._export_draft)
        tools_menu.addAction(act_export)

        # Ayuda
        help_menu = menubar.addMenu("Ayuda")
        act_about = QAction("ℹ️  Acerca de CÓNCLAVE Agente", self)
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    # ─── UI Setup ──────────────────────────────────────────────────────────────

    def _setup_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Header bar
        root_layout.addWidget(self._build_header())

        # Main splitter (3 panels)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_center_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([280, 720, 380])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        root_layout.addWidget(splitter, 1)

        # Manager input bar
        root_layout.addWidget(self._build_manager_bar())

    def _build_header(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("header_bar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # Logo text
        logo_lbl = QLabel("◆ CÓNCLAVE")
        logo_lbl.setStyleSheet(
            "color: #FFFFFF; font-size: 15pt; font-weight: 800; "
            "letter-spacing: 3px; background: transparent;"
        )
        layout.addWidget(logo_lbl)

        agente_lbl = QLabel("AGENTE")
        agente_lbl.setStyleSheet(
            "color: #7C3AED; font-size: 9pt; font-weight: 600; "
            "letter-spacing: 3px; background: transparent; "
            "padding: 2px 8px; border: 1px solid rgba(124,58,237,40); border-radius: 4px;"
        )
        layout.addWidget(agente_lbl)

        layout.addStretch()

        # Session info label
        self._session_info_lbl = QLabel("Sin sesión activa")
        self._session_info_lbl.setObjectName("status_label")
        layout.addWidget(self._session_info_lbl)

        layout.addSpacing(16)

        # Cycle counter
        self._cycle_lbl = QLabel("Ciclo: —")
        self._cycle_lbl.setStyleSheet(
            "color: #4B5675; font-size: 9pt; background: transparent;"
        )
        layout.addWidget(self._cycle_lbl)

        layout.addSpacing(20)

        # Control buttons
        self._btn_start = QPushButton("▶  Iniciar")
        self._btn_start.setObjectName("btn_start")
        self._btn_start.setFixedHeight(36)
        self._btn_start.clicked.connect(self._start_new_session)
        layout.addWidget(self._btn_start)

        self._btn_pause = QPushButton("⏸  Pausar")
        self._btn_pause.setObjectName("btn_pause")
        self._btn_pause.setFixedHeight(36)
        self._btn_pause.setEnabled(False)
        self._btn_pause.clicked.connect(self._toggle_pause)
        layout.addWidget(self._btn_pause)

        self._btn_stop = QPushButton("⏹  Detener")
        self._btn_stop.setObjectName("btn_stop")
        self._btn_stop.setFixedHeight(36)
        self._btn_stop.setEnabled(False)
        self._btn_stop.clicked.connect(self._stop_session)
        layout.addWidget(self._btn_stop)

        return bar

    def _build_left_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel_left")
        panel.setFixedWidth(280)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(8)

        # Section header
        hdr = QLabel("AGENTES  DEL  ENJAMBRE")
        hdr.setObjectName("section_header")
        layout.addWidget(hdr)

        # Agent cards
        self._agent_cards: dict[int, AgentCard] = {}
        for agent in self._agents:
            card = AgentCard(agent, self)
            self._agent_cards[agent["id"]] = card
            layout.addWidget(card)

        layout.addStretch()

        # Customize button
        btn_customize = QPushButton("✏️  Personalizar Agentes")
        btn_customize.clicked.connect(self._open_customization)
        layout.addWidget(btn_customize)

        # Diagnostics button
        btn_diag = QPushButton("🔬  Diagnóstico del Sistema")
        btn_diag.clicked.connect(self._open_diagnosis)
        layout.addWidget(btn_diag)

        return panel

    def _build_center_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel_center")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Chat header
        chat_hdr = QLabel("💬  CONVERSACIÓN EN VIVO")
        chat_hdr.setObjectName("section_header")
        chat_hdr.setContentsMargins(14, 10, 14, 6)
        layout.addWidget(chat_hdr)

        # Scroll area for chat
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._chat_container = QWidget()
        self._chat_container.setStyleSheet("background: transparent;")
        self._chat_layout = QVBoxLayout(self._chat_container)
        self._chat_layout.setContentsMargins(12, 8, 12, 8)
        self._chat_layout.setSpacing(12)
        self._chat_layout.addStretch()

        self._scroll_area.setWidget(self._chat_container)
        layout.addWidget(self._scroll_area, 1)

        return panel

    def _build_right_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel_right")
        panel.setFixedWidth(380)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._draft_panel = DraftPanel(self)
        layout.addWidget(self._draft_panel, 1)

        return panel

    def _build_manager_bar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("manager_bar")
        bar.setFixedHeight(48)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Label
        lbl = QLabel("📢  Manager:")
        lbl.setStyleSheet("color: #F59E0B; font-size: 9pt; font-weight: 600; background: transparent;")
        lbl.setFixedWidth(90)
        layout.addWidget(lbl)

        # Input
        from PySide6.QtWidgets import QLineEdit
        self._manager_input = QLineEdit()
        self._manager_input.setPlaceholderText(
            "Escribe aquí para intervenir en la sesión activa..."
        )
        self._manager_input.returnPressed.connect(self._send_manager_message)
        layout.addWidget(self._manager_input, 1)

        btn_send = QPushButton("↑")
        btn_send.setObjectName("btn_send")
        btn_send.setFixedSize(36, 36)
        btn_send.clicked.connect(self._send_manager_message)
        layout.addWidget(btn_send)

        return bar

    def _setup_status_bar(self):
        self._statusbar = QStatusBar()
        self._statusbar.setStyleSheet(
            "QStatusBar { background: #050810; color: #374151; font-size: 8pt; "
            "border-top: 1px solid #1E2D4A; }"
        )
        self.setStatusBar(self._statusbar)
        self._statusbar.showMessage("CÓNCLAVE Agente v1.0  ·  © 2026 ceob68  ·  Listo")

    # ─── Session Control ──────────────────────────────────────────────────────

    def _start_new_session(self):
        if self._is_running:
            self._stop_session()
            return

        # Get topic from user
        topic, ok = QInputDialog.getMultiLineText(
            self,
            "Nueva Sesión del Enjambre",
            "¿Sobre qué tema deben razonar los agentes?\n"
            "(Describe el problema, idea o pregunta con el mayor detalle posible)",
            ""
        )

        if not ok or not topic.strip():
            return

        topic = topic.strip()

        # Clear chat
        self._clear_chat()
        self._cycle_count = 0
        self._current_bubbles.clear()

        # Create DB session
        self._current_session_id = create_session(topic)

        # Announce in chat
        self._add_system_message(
            f"🚀  Sesión #{self._current_session_id} iniciada\n"
            f"Tema: «{topic[:80]}{'...' if len(topic) > 80 else ''}»"
        )

        # Create and start worker
        self._worker = SwarmWorker(
            session_id=self._current_session_id,
            user_topic=topic,
            agents=[dict(a) for a in self._agents],
            parent=self,
        )

        self._worker.token_signal.connect(self._on_token)
        self._worker.status_signal.connect(self._on_agent_status)
        self._worker.log_signal.connect(self._on_log)
        self._worker.info_signal.connect(self._on_info)
        self._worker.draft_signal.connect(self._on_draft_update)
        self._worker.finished_signal.connect(self._on_worker_finished)

        self._worker.start()

        # Update UI state
        self._is_running = True
        self._is_paused = False
        self._btn_start.setEnabled(False)
        self._btn_pause.setEnabled(True)
        self._btn_stop.setEnabled(True)
        self._session_info_lbl.setText(f"Sesión #{self._current_session_id} activa")
        self._statusbar.showMessage(f"Enjambre activo — Sesión #{self._current_session_id}")

    def _toggle_pause(self):
        if not self._worker:
            return
        if self._is_paused:
            self._worker.resume()
            self._is_paused = False
            self._btn_pause.setText("⏸  Pausar")
            self._session_info_lbl.setText(f"Sesión #{self._current_session_id} activa")
            self._add_system_message("▶️  Enjambre reanudado.")
        else:
            self._worker.pause()
            self._is_paused = True
            self._btn_pause.setText("▶  Reanudar")
            self._session_info_lbl.setText(f"Sesión #{self._current_session_id} — PAUSADA")
            self._add_system_message("⏸  Enjambre pausado.")

    def _stop_session(self):
        if not self._worker:
            return
        reply = QMessageBox.question(
            self, "Detener Sesión",
            "¿Detener el enjambre?\nEl progreso actual se guardará en la base de datos.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._worker.stop()
        self._add_system_message("⏹  Sesión detenida por el usuario.")

    def _on_worker_finished(self):
        self._is_running = False
        self._is_paused = False
        self._btn_start.setEnabled(True)
        self._btn_pause.setEnabled(False)
        self._btn_pause.setText("⏸  Pausar")
        self._btn_stop.setEnabled(False)
        self._session_info_lbl.setText("Sin sesión activa")

        for card in self._agent_cards.values():
            card.set_status("Inactivo")
            card.set_active_style(False)

        self._statusbar.showMessage(
            f"Sesión #{self._current_session_id} finalizada — "
            f"{self._cycle_count} ciclos  ·  © 2026 ceob68"
        )

    # ─── Signal Handlers ──────────────────────────────────────────────────────

    def _on_token(self, agent_id: int, token: str, is_done: bool):
        if is_done:
            # Mark current bubble as complete
            self._current_bubbles.pop(agent_id, None)
            # Scroll to bottom
            QTimer.singleShot(50, self._scroll_to_bottom)
            return

        if agent_id not in self._current_bubbles:
            # Create new bubble
            agent = next((a for a in self._agents if a["id"] == agent_id), None)
            if not agent:
                return
            bubble = ChatBubble(
                agent_id=agent_id,
                agent_name=agent.get("name", f"Agente {agent_id}"),
                agent_icon=agent.get("icon", "🤖"),
                parent=self._chat_container,
            )
            # Insert before the stretch
            self._chat_layout.insertWidget(self._chat_layout.count() - 1, bubble)
            self._current_bubbles[agent_id] = bubble

            # Mark card as active
            if agent_id in self._agent_cards:
                self._agent_cards[agent_id].set_active_style(True)

        self._current_bubbles[agent_id].append_token(token)
        self._scroll_to_bottom()

    def _on_agent_status(self, agent_id: int, status: str):
        if agent_id in self._agent_cards:
            self._agent_cards[agent_id].set_status(status)
            if "inactivo" in status.lower() or "esperando" in status.lower():
                self._agent_cards[agent_id].set_active_style(False)

    def _on_log(self, message: str):
        # Update status bar with last log message
        self._statusbar.showMessage(message[:120])

    def _on_info(self, message: str):
        self._session_info_lbl.setText(message[:60])
        # Count cycles
        if "ciclo" in message.lower():
            try:
                import re
                match = re.search(r"(\d+)\s+ciclo", message.lower())
                if match:
                    self._cycle_count = int(match.group(1))
                    self._cycle_lbl.setText(f"Ciclo: {self._cycle_count}")
            except Exception:
                pass

    def _on_draft_update(self, draft: str):
        self._draft_panel.update_draft(draft)

    # ─── Manager Message ──────────────────────────────────────────────────────

    def _send_manager_message(self):
        msg = self._manager_input.text().strip()
        if not msg:
            return

        if not self._is_running or not self._worker:
            QMessageBox.information(self, "Sin sesión activa",
                                    "Inicia una sesión del enjambre primero.")
            return

        self._worker.inject_manager(msg)

        # Show in chat
        from backend.database import save_message
        if self._current_session_id:
            save_message(self._current_session_id, -1, "Manager", msg, 0, True)

        bubble = ChatBubble(-1, "Manager", "📢", is_manager=True, parent=self._chat_container)
        bubble.set_text(msg)
        self._chat_layout.insertWidget(self._chat_layout.count() - 1, bubble)
        self._scroll_to_bottom()

        self._manager_input.clear()

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _clear_chat(self):
        while self._chat_layout.count() > 1:  # Keep the stretch
            item = self._chat_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

    def _add_system_message(self, text: str):
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(
            "color: #374151; font-size: 8.5pt; background: rgba(30,45,74,80); "
            "border: 1px solid #1E2D4A; border-radius: 8px; padding: 8px 16px; margin: 4px 40px;"
        )
        self._chat_layout.insertWidget(self._chat_layout.count() - 1, lbl)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        scrollbar = self._scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _show_history(self):
        sessions = get_all_sessions()
        if not sessions:
            QMessageBox.information(self, "Historial", "No hay sesiones previas guardadas.")
            return
        lines = []
        for s in sessions[:20]:
            lines.append(f"#{s['id']}  {s['created_at'][:16]}  [{s['status']}]  Ciclos: {s['cycle_count']}\n   {s['topic'][:60]}")
        QMessageBox.information(self, "Historial de Sesiones", "\n\n".join(lines))

    def _open_customization(self):
        from gui.customization_dialog import CustomizationDialog
        dlg = CustomizationDialog(self._agents, self)
        if dlg.exec():
            self._agents = dlg.get_agents()
            save_agent_config(self._agents)
            # Rebuild agent cards
            for agent in self._agents:
                aid = agent["id"]
                if aid in self._agent_cards:
                    self._agent_cards[aid].agent = agent

    def _open_diagnosis(self):
        from gui.diagnosis_dialog import DiagnosisDialog
        dlg = DiagnosisDialog(self)
        dlg.exec()

    def _reset_agent_config(self):
        reply = QMessageBox.question(
            self, "Restaurar Configuración",
            "¿Restaurar la configuración por defecto de todos los agentes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            import copy
            self._agents = copy.deepcopy(DEFAULT_AGENTS)
            save_agent_config(self._agents)
            QMessageBox.information(self, "Listo", "Configuración restaurada a los valores por defecto.")

    def _export_draft(self):
        from PySide6.QtWidgets import QFileDialog
        from backend.database import get_session
        if not self._current_session_id:
            QMessageBox.information(self, "Sin sesión", "No hay sesión activa para exportar.")
            return
        session = get_session(self._current_session_id)
        draft = session.get("draft", "") if session else ""
        if not draft:
            QMessageBox.information(self, "Sin borrador", "El borrador está vacío.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Borrador", f"conclave_draft_{self._current_session_id}.txt", "Text Files (*.txt)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(draft)
            QMessageBox.information(self, "Exportado", f"Borrador guardado en:\n{path}")

    def _show_about(self):
        QMessageBox.about(
            self,
            "Acerca de CÓNCLAVE Agente",
            "<h2 style='color:#7C3AED;'>CÓNCLAVE Agente v1.0</h2>"
            "<p><b>Tu consejo privado de inteligencias artificiales</b></p>"
            "<p>Sistema de 5 agentes IA especializados con razonamiento colaborativo "
            "100% offline, usando modelos Google Gemma-4 con cuantización NF4 4-bit.</p>"
            "<hr>"
            "<p><small>© 2026 ceob68 / Vaultly. Todos los derechos reservados.<br>"
            "Prohibida la redistribución o ingeniería inversa.</small></p>"
        )

    def _check_gpu_on_startup(self):
        """Show warnings for missing GPU or HF token."""
        import os

        # Check HF token
        hf_token = get_hf_token()
        if not hf_token:
            msg = QMessageBox(self)
            msg.setWindowTitle("⚙️  Configuración requerida")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("<b style='color:#06B6D4; font-size:11pt;'>Token de HuggingFace no configurado</b>")
            msg.setInformativeText(
                "Para descargar y usar los modelos de IA (Gemma-3), necesitas:\n\n"
                "1. Cuenta gratis en huggingface.co\n"
                "2. Aceptar la licencia del modelo Gemma-3\n"
                "3. Crear un token de acceso (Read)\n\n"
                "Ve a: Herramientas → Configuración y Descarga de Modelos"
            )
            btn_config = msg.addButton("⚙️  Abrir Configuración", QMessageBox.ButtonRole.AcceptRole)
            msg.addButton("Ahora no", QMessageBox.ButtonRole.RejectRole)
            msg.exec()
            if msg.clickedButton() == btn_config:
                self._open_settings()
            return  # Don't show GPU warning on top of this

        # Check GPU
        try:
            import torch
            if not torch.cuda.is_available():
                msg = QMessageBox(self)
                msg.setWindowTitle("⚠️  Sin GPU NVIDIA detectada")
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText("<b style='color:#F59E0B; font-size:11pt;'>Modo CPU activado</b>")
                msg.setInformativeText(
                    "No se detectó GPU NVIDIA con CUDA.\n\n"
                    "CÓNCLAVE Agente funcionará pero las respuestas\n"
                    "tardarán entre 5 y 20 minutos por agente.\n\n"
                    "Recomendación: activa solo 1 o 2 agentes con\n"
                    "el modelo más pequeño (Gemma-3 2B)."
                )
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
                self._statusbar.showMessage(
                    "⚠️  Modo CPU — Respuestas lentas esperadas  ·  CÓNCLAVE Agente v1.0"
                )
        except ImportError:
            pass

    def _open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    def closeEvent(self, event):
        if self._is_running and self._worker:
            reply = QMessageBox.question(
                self, "Salir",
                "Hay una sesión activa. ¿Detener y salir?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._worker.stop()
                self._worker.wait(3000)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
