# © 2026 ceob68 / Vaultly. All rights reserved.
# Unauthorized copying, distribution or modification is prohibited.

"""
customization_dialog.py — Agent Configuration Dialog
"""

import copy
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QTabWidget, QWidget, QCheckBox,
    QMessageBox, QDialogButtonBox, QScrollArea, QFrame
)
from PySide6.QtCore import Qt

from backend.ai_engine import MODEL_REGISTRY
from backend.orchestrator import DEFAULT_AGENTS
from gui.app_style import AGENT_COLORS


# Available models for selection
AVAILABLE_MODELS = {
    "google/gemma-3-2b-it":  "Gemma-3 2B (Ligero, rápido)",
    "google/gemma-3-4b-it":  "Gemma-3 4B (Balanceado)",
    "google/gemma-3-12b-it": "Gemma-3 12B (Potente)",
    "google/gemma-3-27b-it": "Gemma-3 27B (Máxima capacidad)",
    "google/gemma-2-9b-it":  "Gemma-2 9B (Alternativa)",
    "microsoft/phi-4":       "Phi-4 (Microsoft, eficiente)",
    "Qwen/Qwen2.5-7B-Instruct": "Qwen 2.5 7B (Multilingüe)",
}


class AgentConfigTab(QWidget):
    """Configuration tab for a single agent."""

    def __init__(self, agent: dict, parent=None):
        super().__init__(parent)
        self._agent = copy.deepcopy(agent)
        colors = AGENT_COLORS.get(agent["id"], AGENT_COLORS[0])
        self._setup_ui(colors)

    def _setup_ui(self, colors: dict):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # Agent name header
        hdr = QFrame()
        hdr.setStyleSheet(
            f"background: {colors['bg']}; border: 1px solid {colors['border']}; "
            f"border-radius: 10px; padding: 6px;"
        )
        hdr_layout = QHBoxLayout(hdr)
        icon_lbl = QLabel(self._agent.get("icon", "🤖"))
        icon_lbl.setStyleSheet("font-size: 18pt; background: transparent;")
        hdr_layout.addWidget(icon_lbl)
        name_lbl = QLabel(f"Agente #{self._agent['id']} — {self._agent['name']}")
        name_lbl.setStyleSheet(
            f"color: {colors['primary']}; font-size: 11pt; font-weight: 700; background: transparent;"
        )
        hdr_layout.addWidget(name_lbl)
        hdr_layout.addStretch()

        self._enabled_check = QCheckBox("Habilitado")
        self._enabled_check.setChecked(self._agent.get("enabled", True))
        hdr_layout.addWidget(self._enabled_check)

        layout.addWidget(hdr)

        # Model selection
        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("Modelo:"))
        self._model_combo = QComboBox()
        for model_id, display_name in AVAILABLE_MODELS.items():
            self._model_combo.addItem(display_name, model_id)

        # Set current model
        current_model = self._agent.get("model_override") or MODEL_REGISTRY.get(self._agent["id"])
        for i in range(self._model_combo.count()):
            if self._model_combo.itemData(i) == current_model:
                self._model_combo.setCurrentIndex(i)
                break

        model_row.addWidget(self._model_combo, 1)
        layout.addLayout(model_row)

        # Role prompt
        role_lbl = QLabel("Instrucción de rol (system prompt):")
        role_lbl.setStyleSheet("color: #8892A4; font-size: 9pt;")
        layout.addWidget(role_lbl)

        self._role_edit = QTextEdit()
        self._role_edit.setPlainText(self._agent.get("role", ""))
        self._role_edit.setMinimumHeight(160)
        self._role_edit.setPlaceholderText(
            "Define el rol y comportamiento de este agente...\n\n"
            "Ejemplo: 'Eres un experto en seguridad. Tu tarea es identificar vulnerabilidades...'"
        )
        layout.addWidget(self._role_edit, 1)

        # Char count
        self._char_count = QLabel("0 caracteres")
        self._char_count.setStyleSheet("color: #4B5675; font-size: 8pt;")
        self._role_edit.textChanged.connect(self._update_char_count)
        self._update_char_count()
        layout.addWidget(self._char_count)

    def _update_char_count(self):
        n = len(self._role_edit.toPlainText())
        self._char_count.setText(f"{n:,} caracteres")

    def get_agent_data(self) -> dict:
        updated = copy.deepcopy(self._agent)
        updated["enabled"] = self._enabled_check.isChecked()
        updated["role"] = self._role_edit.toPlainText().strip()
        updated["model_override"] = self._model_combo.currentData()
        return updated


class CustomizationDialog(QDialog):
    """Full agent customization dialog with one tab per agent."""

    def __init__(self, agents: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Personalizar Agentes — CÓNCLAVE Agente")
        self.setMinimumSize(700, 560)
        self._agents = [copy.deepcopy(a) for a in agents]
        self._tabs: list[AgentConfigTab] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 12)
        layout.setSpacing(12)

        # Header
        hdr = QLabel("✏️  Configuración de Agentes")
        hdr.setStyleSheet("font-size: 13pt; font-weight: 700; color: #FFFFFF;")
        layout.addWidget(hdr)

        sub = QLabel(
            "Personaliza el rol, modelo y disponibilidad de cada agente del enjambre.\n"
            "Los cambios se aplican en la próxima sesión."
        )
        sub.setStyleSheet("color: #8892A4; font-size: 9pt;")
        layout.addWidget(sub)

        # Tab widget
        self._tab_widget = QTabWidget()
        for agent in self._agents:
            tab = AgentConfigTab(agent, self)
            self._tabs.append(tab)
            icon = agent.get("icon", "🤖")
            name = agent.get("name", f"Agente {agent['id']}")
            self._tab_widget.addTab(tab, f"{icon} {name}")

        layout.addWidget(self._tab_widget, 1)

        # Reset button row
        extra_row = QHBoxLayout()
        btn_reset = QPushButton("🔄  Restaurar Todos")
        btn_reset.clicked.connect(self._reset_all)
        extra_row.addWidget(btn_reset)
        extra_row.addStretch()
        layout.addLayout(extra_row)

        # Dialog buttons
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self._save)
        btn_box.rejected.connect(self.reject)
        btn_box.button(QDialogButtonBox.StandardButton.Save).setObjectName("btn_primary")
        btn_box.button(QDialogButtonBox.StandardButton.Save).setText("💾  Guardar Cambios")
        layout.addWidget(btn_box)

    def _save(self):
        self._agents = [tab.get_agent_data() for tab in self._tabs]
        self.accept()

    def _reset_all(self):
        reply = QMessageBox.question(
            self, "Restaurar Configuración",
            "¿Restaurar los roles por defecto de todos los agentes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            import copy
            from backend.orchestrator import DEFAULT_AGENTS
            for i, tab in enumerate(self._tabs):
                if i < len(DEFAULT_AGENTS):
                    default = DEFAULT_AGENTS[i]
                    tab._role_edit.setPlainText(default["role"])
                    # Reset model combo to default
                    default_model = MODEL_REGISTRY.get(i, "google/gemma-3-2b-it")
                    for j in range(tab._model_combo.count()):
                        if tab._model_combo.itemData(j) == default_model:
                            tab._model_combo.setCurrentIndex(j)
                            break

    def get_agents(self) -> list:
        return self._agents
