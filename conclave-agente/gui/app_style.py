# © 2026 ceob68 / Vaultly. All rights reserved.
# Unauthorized copying, distribution or modification is prohibited.

"""
app_style.py — CÓNCLAVE Agente Visual Theme

Design Language:
  - Deep navy/dark backgrounds with gradient depth
  - Violet (#7C3AED) + Cyan (#06B6D4) accent palette
  - Glassmorphism via layered semi-transparent backgrounds
  - Glowing borders on active/hover states
  - Custom scrollbars, rich progress bars, animated indicators
"""

# ─── Color Tokens ─────────────────────────────────────────────────────────────
BG_DEEPEST    = "#050810"
BG_DEEP       = "#080C18"
BG_BASE       = "#0D1228"
BG_SURFACE    = "#111827"
BG_CARD       = "#141C30"
BG_ELEVATED   = "#1A2340"
BG_HOVER      = "#1F2B4A"

BORDER_SUBTLE  = "#1E2D4A"
BORDER_DEFAULT = "#2A3A5C"
BORDER_ACCENT  = "#3D2E6B"
BORDER_GLOW    = "#7C3AED"

TEXT_PRIMARY   = "#E8EAF0"
TEXT_SECONDARY = "#8892A4"
TEXT_MUTED     = "#4B5675"
TEXT_LINK      = "#7C3AED"

VIOLET_PRIMARY = "#7C3AED"
VIOLET_LIGHT   = "#9D6FEF"
VIOLET_DARK    = "#5B21B6"
CYAN_PRIMARY   = "#06B6D4"
CYAN_LIGHT     = "#22D3EE"
GREEN_OK       = "#10B981"
AMBER_WARN     = "#F59E0B"
RED_DANGER     = "#EF4444"

MAIN_STYLESHEET = f"""

/* ═══════════════════════════════════════════════════════
   GLOBAL BASE
═══════════════════════════════════════════════════════ */

QWidget {{
    background-color: {BG_BASE};
    color: {TEXT_PRIMARY};
    font-family: "Segoe UI";
    font-size: 10pt;
    selection-background-color: {VIOLET_PRIMARY};
    selection-color: #FFFFFF;
    border: none;
    outline: none;
}}

QMainWindow {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 {BG_DEEPEST},
        stop:0.4 {BG_BASE},
        stop:1.0 #090D1F
    );
}}

/* ═══════════════════════════════════════════════════════
   SCROLLBARS — Custom dark slim design
═══════════════════════════════════════════════════════ */

QScrollBar:vertical {{
    background: {BG_SURFACE};
    width: 8px;
    border-radius: 4px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {VIOLET_PRIMARY}, stop:1 {CYAN_PRIMARY});
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {VIOLET_LIGHT}, stop:1 {CYAN_LIGHT});
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QScrollBar:horizontal {{
    background: {BG_SURFACE};
    height: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: {VIOLET_PRIMARY};
    border-radius: 3px;
    min-width: 30px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ═══════════════════════════════════════════════════════
   LABELS
═══════════════════════════════════════════════════════ */

QLabel {{
    background: transparent;
    color: {TEXT_PRIMARY};
}}

QLabel#title_label {{
    font-size: 15pt;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: 2px;
}}

QLabel#subtitle_label {{
    font-size: 9pt;
    color: {TEXT_SECONDARY};
    letter-spacing: 1px;
}}

QLabel#section_header {{
    font-size: 8pt;
    font-weight: 600;
    color: {VIOLET_PRIMARY};
    letter-spacing: 2px;
    padding: 4px 0 2px 4px;
    text-transform: uppercase;
}}

QLabel#status_label {{
    font-size: 9pt;
    color: {CYAN_PRIMARY};
    padding: 2px 8px;
    background: rgba(6, 182, 212, 0.08);
    border: 1px solid rgba(6, 182, 212, 0.25);
    border-radius: 10px;
}}

/* ═══════════════════════════════════════════════════════
   PANELS & FRAMES — Glassmorphism simulation
═══════════════════════════════════════════════════════ */

QFrame#panel_left {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(20, 28, 48, 220),
        stop:1 rgba(13, 18, 40, 200)
    );
    border-right: 1px solid {BORDER_SUBTLE};
    border-radius: 0;
}}

QFrame#panel_center {{
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(13, 18, 40, 230),
        stop:1 rgba(8, 12, 24, 240)
    );
    border-left: 1px solid {BORDER_SUBTLE};
    border-right: 1px solid {BORDER_SUBTLE};
}}

QFrame#panel_right {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(20, 28, 48, 210),
        stop:1 rgba(11, 16, 35, 220)
    );
    border-left: 1px solid {BORDER_SUBTLE};
}}

QFrame#card {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 {BG_CARD},
        stop:1 rgba(17, 24, 39, 200)
    );
    border: 1px solid {BORDER_DEFAULT};
    border-radius: 12px;
    padding: 4px;
}}

QFrame#card:hover {{
    border: 1px solid {BORDER_ACCENT};
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 {BG_ELEVATED},
        stop:1 rgba(26, 35, 64, 200)
    );
}}

QFrame#card_active {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(124, 58, 237, 15),
        stop:1 rgba(6, 182, 212, 8)
    );
    border: 1px solid rgba(124, 58, 237, 50);
    border-radius: 12px;
    padding: 4px;
}}

QFrame#header_bar {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(8, 12, 24, 255),
        stop:0.3 rgba(13, 18, 40, 240),
        stop:0.7 rgba(13, 18, 40, 240),
        stop:1 rgba(8, 12, 24, 255)
    );
    border-bottom: 1px solid rgba(124, 58, 237, 40);
    min-height: 58px;
    max-height: 58px;
}}

QFrame#status_bar {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {BG_DEEPEST},
        stop:1 rgba(13, 18, 40, 200)
    );
    border-top: 1px solid {BORDER_SUBTLE};
}}

QFrame#manager_bar {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {BG_DEEPEST},
        stop:1 rgba(13, 18, 40, 200)
    );
    border-top: 1px solid {BORDER_SUBTLE};
    min-height: 48px;
    max-height: 48px;
}}

/* ═══════════════════════════════════════════════════════
   BUTTONS — Enterprise grade with glow
═══════════════════════════════════════════════════════ */

QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {BG_ELEVATED}, stop:1 {BG_SURFACE});
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: 8px;
    padding: 7px 16px;
    font-size: 9.5pt;
    font-weight: 500;
}}

QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {BG_HOVER}, stop:1 {BG_ELEVATED});
    border: 1px solid {BORDER_ACCENT};
    color: #FFFFFF;
}}

QPushButton:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {BG_SURFACE}, stop:1 {BG_CARD});
    border: 1px solid {BORDER_GLOW};
}}

/* Start button — Green glow */
QPushButton#btn_start {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #166534, stop:1 #14532D);
    color: #D1FAE5;
    border: 1px solid #16A34A;
    border-radius: 10px;
    padding: 9px 24px;
    font-size: 10pt;
    font-weight: 700;
    letter-spacing: 1px;
}}
QPushButton#btn_start:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #15803D, stop:1 #166534);
    border: 1px solid {GREEN_OK};
    color: #FFFFFF;
}}
QPushButton#btn_start:disabled {{
    background: #1A2332;
    color: {TEXT_MUTED};
    border: 1px solid {BORDER_SUBTLE};
}}

/* Pause button — Amber glow */
QPushButton#btn_pause {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #78350F, stop:1 #451A03);
    color: #FDE68A;
    border: 1px solid #D97706;
    border-radius: 10px;
    padding: 9px 24px;
    font-size: 10pt;
    font-weight: 700;
}}
QPushButton#btn_pause:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #92400E, stop:1 #78350F);
    border: 1px solid {AMBER_WARN};
}}
QPushButton#btn_pause:disabled {{
    background: #1A2332;
    color: {TEXT_MUTED};
    border: 1px solid {BORDER_SUBTLE};
}}

/* Stop button — Red glow */
QPushButton#btn_stop {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #7F1D1D, stop:1 #450A0A);
    color: #FECACA;
    border: 1px solid #DC2626;
    border-radius: 10px;
    padding: 9px 24px;
    font-size: 10pt;
    font-weight: 700;
}}
QPushButton#btn_stop:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #991B1B, stop:1 #7F1D1D);
    border: 1px solid {RED_DANGER};
}}
QPushButton#btn_stop:disabled {{
    background: #1A2332;
    color: {TEXT_MUTED};
    border: 1px solid {BORDER_SUBTLE};
}}

/* Violet primary button */
QPushButton#btn_primary {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {VIOLET_PRIMARY}, stop:1 {VIOLET_DARK});
    color: #FFFFFF;
    border: 1px solid {VIOLET_LIGHT};
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 10pt;
    font-weight: 600;
}}
QPushButton#btn_primary:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #8B5CF6, stop:1 {VIOLET_PRIMARY});
    border: 1px solid #C4B5FD;
}}

/* Send button */
QPushButton#btn_send {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {VIOLET_PRIMARY}, stop:1 {CYAN_PRIMARY});
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 700;
    font-size: 11pt;
    min-width: 48px;
    min-height: 36px;
}}
QPushButton#btn_send:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {VIOLET_LIGHT}, stop:1 {CYAN_LIGHT});
}}

/* Toggle button */
QPushButton#btn_toggle_on {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(16, 185, 129, 30), stop:1 rgba(16, 185, 129, 10));
    color: {GREEN_OK};
    border: 1px solid rgba(16, 185, 129, 50);
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 8pt;
    font-weight: 600;
    min-width: 44px;
}}
QPushButton#btn_toggle_off {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(75, 85, 99, 30), stop:1 rgba(55, 65, 81, 10));
    color: {TEXT_MUTED};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 8pt;
    font-weight: 600;
    min-width: 44px;
}}

/* ═══════════════════════════════════════════════════════
   TEXT INPUTS
═══════════════════════════════════════════════════════ */

QTextEdit, QPlainTextEdit {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {BG_SURFACE}, stop:1 {BG_CARD});
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: 8px;
    padding: 8px;
    font-size: 10pt;
    selection-background-color: {VIOLET_PRIMARY};
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {VIOLET_PRIMARY};
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {BG_ELEVATED}, stop:1 {BG_SURFACE});
}}

QLineEdit {{
    background: {BG_SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 10pt;
}}

QLineEdit:focus {{
    border: 1px solid {VIOLET_PRIMARY};
    background: {BG_ELEVATED};
}}

QLineEdit::placeholder {{
    color: {TEXT_MUTED};
}}

/* ═══════════════════════════════════════════════════════
   COMBOBOX
═══════════════════════════════════════════════════════ */

QComboBox {{
    background: {BG_SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 9.5pt;
    min-width: 140px;
}}

QComboBox:hover {{
    border: 1px solid {BORDER_ACCENT};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {VIOLET_PRIMARY};
    margin-right: 6px;
}}

QComboBox QAbstractItemView {{
    background: {BG_SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_ACCENT};
    border-radius: 8px;
    selection-background-color: {VIOLET_PRIMARY};
    outline: none;
}}

/* ═══════════════════════════════════════════════════════
   SPLITTER
═══════════════════════════════════════════════════════ */

QSplitter::handle {{
    background: {BORDER_SUBTLE};
    width: 2px;
    height: 2px;
}}

QSplitter::handle:hover {{
    background: {VIOLET_PRIMARY};
}}

/* ═══════════════════════════════════════════════════════
   TABS
═══════════════════════════════════════════════════════ */

QTabWidget::pane {{
    background: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: 8px;
    top: -1px;
}}

QTabBar::tab {{
    background: transparent;
    color: {TEXT_SECONDARY};
    padding: 7px 16px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 9.5pt;
}}

QTabBar::tab:selected {{
    color: {TEXT_PRIMARY};
    border-bottom: 2px solid {VIOLET_PRIMARY};
}}

QTabBar::tab:hover {{
    color: {TEXT_PRIMARY};
    border-bottom: 2px solid {BORDER_ACCENT};
}}

/* ═══════════════════════════════════════════════════════
   PROGRESS BAR
═══════════════════════════════════════════════════════ */

QProgressBar {{
    background: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: 5px;
    height: 6px;
    text-align: center;
    font-size: 8pt;
    color: transparent;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {VIOLET_PRIMARY}, stop:1 {CYAN_PRIMARY});
    border-radius: 5px;
}}

/* ═══════════════════════════════════════════════════════
   DIALOGS
═══════════════════════════════════════════════════════ */

QDialog {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {BG_DEEP}, stop:1 {BG_BASE});
    border: 1px solid {BORDER_ACCENT};
    border-radius: 12px;
}}

QMessageBox {{
    background: {BG_SURFACE};
}}

/* ═══════════════════════════════════════════════════════
   TOOLTIPS
═══════════════════════════════════════════════════════ */

QToolTip {{
    background: {BG_ELEVATED};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_ACCENT};
    border-radius: 6px;
    padding: 5px 9px;
    font-size: 9pt;
}}

/* ═══════════════════════════════════════════════════════
   MENU BAR
═══════════════════════════════════════════════════════ */

QMenuBar {{
    background: {BG_DEEPEST};
    color: {TEXT_SECONDARY};
    border-bottom: 1px solid {BORDER_SUBTLE};
    padding: 2px;
}}

QMenuBar::item:selected {{
    background: {BG_ELEVATED};
    color: {TEXT_PRIMARY};
    border-radius: 4px;
}}

QMenu {{
    background: {BG_SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_ACCENT};
    border-radius: 8px;
    padding: 4px;
}}

QMenu::item {{
    padding: 6px 20px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background: {VIOLET_PRIMARY};
    color: #FFFFFF;
}}

QMenu::separator {{
    height: 1px;
    background: {BORDER_SUBTLE};
    margin: 4px 8px;
}}

/* ═══════════════════════════════════════════════════════
   CHECKBOXES
═══════════════════════════════════════════════════════ */

QCheckBox {{
    color: {TEXT_SECONDARY};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {BORDER_DEFAULT};
    border-radius: 4px;
    background: {BG_SURFACE};
}}

QCheckBox::indicator:checked {{
    background: {VIOLET_PRIMARY};
    border: 1px solid {VIOLET_LIGHT};
}}

QCheckBox::indicator:hover {{
    border: 1px solid {VIOLET_PRIMARY};
}}

"""

# ─── Per-agent color map ───────────────────────────────────────────────────────
AGENT_COLORS = {
    0: {"primary": "#7C3AED", "bg": "rgba(124, 58, 237, 12)", "border": "rgba(124, 58, 237, 35)"},
    1: {"primary": "#06B6D4", "bg": "rgba(6, 182, 212, 12)",  "border": "rgba(6, 182, 212, 35)"},
    2: {"primary": "#EF4444", "bg": "rgba(239, 68, 68, 12)",  "border": "rgba(239, 68, 68, 35)"},
    3: {"primary": "#F59E0B", "bg": "rgba(245, 158, 11, 12)", "border": "rgba(245, 158, 11, 35)"},
    4: {"primary": "#10B981", "bg": "rgba(16, 185, 129, 12)", "border": "rgba(16, 185, 129, 35)"},
}
