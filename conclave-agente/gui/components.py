# © 2026 ceob68 / Vaultly. All rights reserved.
# Unauthorized copying, distribution or modification is prohibited.

"""
components.py — CÓNCLAVE Agente Custom Widgets

AgentCard      — Agent status card with toggle, color indicator, and status
ChatBubble     — Styled message bubble per agent
PulseIndicator — Animated dot indicating active state
DraftPanel     — Accumulative draft display with syntax
"""

from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QSizePolicy, QTextEdit
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, Property
from PySide6.QtGui import QColor, QPainter, QFont, QLinearGradient, QPen, QBrush, QRadialGradient

from gui.app_style import AGENT_COLORS


# ─── Pulse Indicator ──────────────────────────────────────────────────────────

class PulseIndicator(QWidget):
    """Animated circular dot — pulses when active."""

    def __init__(self, color: str = "#10B981", size: int = 10, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self._dot_size = size
        self._pulse_radius = 0.0
        self._active = False
        self.setFixedSize(size + 12, size + 12)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._phase = 0.0

    def set_active(self, active: bool):
        self._active = active
        if active:
            self._timer.start(50)
        else:
            self._timer.stop()
            self._pulse_radius = 0.0
            self.update()

    def set_color(self, color: str):
        self._color = QColor(color)
        self.update()

    def _tick(self):
        import math
        self._phase = (self._phase + 0.15) % (2 * math.pi)
        import math
        self._pulse_radius = abs(math.sin(self._phase)) * (self._dot_size * 0.8)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() / 2
        cy = self.height() / 2
        r = self._dot_size / 2

        if self._active and self._pulse_radius > 0:
            # Glow ring
            glow_color = QColor(self._color)
            glow_color.setAlpha(40)
            painter.setBrush(QBrush(glow_color))
            painter.setPen(Qt.PenStyle.NoPen)
            pr = r + self._pulse_radius
            painter.drawEllipse(int(cx - pr), int(cy - pr), int(pr * 2), int(pr * 2))

        # Core dot
        painter.setBrush(QBrush(self._color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))


# ─── Agent Card ───────────────────────────────────────────────────────────────

class AgentCard(QFrame):
    """
    Agent status card showing:
    - Color accent sidebar
    - Icon + Name
    - Current status text
    - Pulse indicator
    - Toggle ON/OFF button
    """

    def __init__(self, agent: dict, parent=None):
        super().__init__(parent)
        self.agent = agent
        self.agent_id = agent["id"]
        self._enabled = agent.get("enabled", True)
        colors = AGENT_COLORS.get(self.agent_id, AGENT_COLORS[0])
        self._primary_color = colors["primary"]

        self.setObjectName("card")
        self.setFixedHeight(76)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        # Color sidebar accent
        sidebar = QFrame(self)
        sidebar.setFixedWidth(4)
        sidebar.setFixedHeight(48)
        sidebar.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
            f"stop:0 {self._primary_color}, stop:1 transparent); "
            f"border-radius: 2px;"
        )
        layout.addWidget(sidebar)

        # Pulse indicator
        self._pulse = PulseIndicator(self._primary_color, 8, self)
        layout.addWidget(self._pulse)

        # Text section
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)

        # Agent name row
        name_row = QHBoxLayout()
        name_row.setSpacing(6)
        self._icon_label = QLabel(agent_data.get("icon", "🤖") if (agent_data := self.agent) else "🤖")
        self._icon_label.setStyleSheet("background: transparent; font-size: 13pt;")
        self._name_label = QLabel(self.agent.get("name", "Agente"))
        self._name_label.setStyleSheet(
            f"color: #FFFFFF; font-size: 10pt; font-weight: 700; background: transparent;"
        )
        name_row.addWidget(self._icon_label)
        name_row.addWidget(self._name_label)
        name_row.addStretch()
        text_layout.addLayout(name_row)

        # Status text
        self._status_label = QLabel("Inactivo")
        self._status_label.setStyleSheet(
            f"color: {self._primary_color}; font-size: 8pt; background: transparent; opacity: 0.8;"
        )
        text_layout.addWidget(self._status_label)

        layout.addLayout(text_layout)
        layout.addStretch()

        # Toggle button
        self._toggle_btn = QPushButton("ON" if self._enabled else "OFF")
        self._toggle_btn.setObjectName("btn_toggle_on" if self._enabled else "btn_toggle_off")
        self._toggle_btn.setFixedSize(44, 22)
        self._toggle_btn.clicked.connect(self._toggle)
        layout.addWidget(self._toggle_btn)

    def _toggle(self):
        self._enabled = not self._enabled
        self.agent["enabled"] = self._enabled
        self._toggle_btn.setText("ON" if self._enabled else "OFF")
        self._toggle_btn.setObjectName("btn_toggle_on" if self._enabled else "btn_toggle_off")
        self._toggle_btn.style().unpolish(self._toggle_btn)
        self._toggle_btn.style().polish(self._toggle_btn)

    def set_status(self, status: str):
        self._status_label.setText(status)
        active_keywords = ["generando", "cargando", "token"]
        is_active = any(k in status.lower() for k in active_keywords)
        self._pulse.set_active(is_active)

        if "error" in status.lower():
            self._status_label.setStyleSheet(
                "color: #EF4444; font-size: 8pt; background: transparent;"
            )
        elif "completó" in status.lower() or "inactivo" in status.lower():
            self._status_label.setStyleSheet(
                f"color: {self._primary_color}; font-size: 8pt; background: transparent; opacity: 0.7;"
            )
        else:
            self._status_label.setStyleSheet(
                f"color: {self._primary_color}; font-size: 8pt; background: transparent;"
            )

    def set_active_style(self, active: bool):
        self.setObjectName("card_active" if active else "card")
        self.style().unpolish(self)
        self.style().polish(self)


# ─── Chat Bubble ──────────────────────────────────────────────────────────────

class ChatBubble(QFrame):
    """Message bubble with agent color accent and streaming support."""

    def __init__(self, agent_id: int, agent_name: str, agent_icon: str = "🤖",
                 is_manager: bool = False, parent=None):
        super().__init__(parent)
        self.agent_id = agent_id
        self._is_manager = is_manager
        colors = AGENT_COLORS.get(agent_id, AGENT_COLORS[0])
        self._color = colors["primary"]

        self._setup_ui(agent_name, agent_icon, is_manager, colors)

    def _setup_ui(self, agent_name: str, agent_icon: str, is_manager: bool, colors: dict):
        self.setContentsMargins(0, 4, 0, 4)

        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header row: icon + name + timestamp
        header = QHBoxLayout()
        header.setSpacing(6)

        if is_manager:
            icon_lbl = QLabel("📢")
        else:
            icon_lbl = QLabel(agent_icon)
        icon_lbl.setStyleSheet("background: transparent; font-size: 14pt;")
        header.addWidget(icon_lbl)

        name_color = "#F59E0B" if is_manager else self._color
        name_lbl = QLabel("Manager" if is_manager else agent_name)
        name_lbl.setStyleSheet(
            f"color: {name_color}; font-size: 9pt; font-weight: 700; background: transparent;"
        )
        header.addWidget(name_lbl)
        header.addStretch()

        from datetime import datetime
        time_lbl = QLabel(datetime.now().strftime("%H:%M"))
        time_lbl.setStyleSheet("color: #4B5675; font-size: 8pt; background: transparent;")
        header.addWidget(time_lbl)

        layout.addLayout(header)

        # Content area
        border_color = "#F59E0B" if is_manager else colors["border"]
        bg_color = "rgba(245, 158, 11, 8)" if is_manager else colors["bg"]

        self._content = QLabel("")
        self._content.setWordWrap(True)
        self._content.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._content.setStyleSheet(
            f"color: #D1D5DB; font-size: 9.5pt; line-height: 1.6; "
            f"background: {bg_color}; "
            f"border: 1px solid {border_color}; "
            f"border-radius: 10px; padding: 10px 14px;"
        )
        layout.addWidget(self._content)

        self._full_text = ""

    def append_token(self, token: str):
        self._full_text += token
        self._content.setText(self._full_text)

    def set_text(self, text: str):
        self._full_text = text
        self._content.setText(text)

    def get_text(self) -> str:
        return self._full_text


# ─── Draft Panel ──────────────────────────────────────────────────────────────

class DraftPanel(QWidget):
    """Right panel showing the accumulative draft with cycle markers."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        hdr = QLabel("📋  BORRADOR ACUMULATIVO")
        hdr.setObjectName("section_header")
        hdr.setContentsMargins(12, 10, 12, 6)
        layout.addWidget(hdr)

        # Draft text area
        self._draft_view = QTextEdit()
        self._draft_view.setReadOnly(True)
        self._draft_view.setPlaceholderText(
            "El borrador acumulativo aparecerá aquí\nal completarse cada ciclo del enjambre..."
        )
        self._draft_view.setStyleSheet(
            "QTextEdit { background: transparent; border: none; "
            "color: #B0B8CC; font-size: 9pt; padding: 8px; line-height: 1.7; }"
        )
        layout.addWidget(self._draft_view, 1)

        # Footer stats
        self._stats_label = QLabel("Ciclos: 0  •  Palabras: 0")
        self._stats_label.setStyleSheet(
            "color: #374151; font-size: 8pt; padding: 4px 12px; background: transparent;"
        )
        layout.addWidget(self._stats_label)

    def update_draft(self, draft_text: str):
        self._draft_view.setPlainText(draft_text)
        # Scroll to bottom
        scrollbar = self._draft_view.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        # Update stats
        words = len(draft_text.split()) if draft_text else 0
        cycles = draft_text.count("CICLO") if draft_text else 0
        self._stats_label.setText(f"Ciclos: {cycles}  •  Palabras: {words:,}")
