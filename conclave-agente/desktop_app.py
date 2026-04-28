# © 2026 ceob68 / Vaultly. All rights reserved.
# Unauthorized copying, distribution or modification is prohibited.

import sys
import os
import ctypes

def setup_windows_env():
    """Configure Windows-specific settings for proper taskbar icon and DPI."""
    if sys.platform == "win32":
        try:
            # Set AppUserModelID for correct taskbar icon
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ceob68.ConclaveAgente.1.0")
            # Enable DPI awareness
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

def main():
    setup_windows_env()

    # Must import Qt after Windows env setup
    from PySide6.QtWidgets import QApplication, QSplashScreen
    from PySide6.QtGui import QPixmap, QFont, QFontDatabase
    from PySide6.QtCore import Qt, QTimer

    from backend.database import init_db
    from gui.main_window import MainWindow
    from gui.app_style import MAIN_STYLESHEET

    app = QApplication(sys.argv)
    app.setApplicationName("CÓNCLAVE Agente")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("ceob68")
    app.setOrganizationDomain("vaultly.ceob68.com")

    # Font setup
    font = QFont("Segoe UI", 10)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    app.setFont(font)

    # Apply global stylesheet
    app.setStyleSheet(MAIN_STYLESHEET)

    # Splash screen
    splash_pixmap = _create_splash_pixmap()
    splash = QSplashScreen(splash_pixmap, Qt.WindowType.WindowStaysOnTopHint)
    splash.setWindowFlag(Qt.WindowType.FramelessWindowHint)
    splash.show()
    splash.showMessage(
        "Iniciando CÓNCLAVE Agente v1.0...",
        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
        Qt.GlobalColor.white
    )
    app.processEvents()

    # Init database
    init_db()

    # Create main window
    window = MainWindow()

    # Close splash and show main window after 2.5s
    def show_main():
        splash.finish(window)
        window.show()

    QTimer.singleShot(2500, show_main)

    sys.exit(app.exec())


def _create_splash_pixmap():
    """Generate a programmatic splash screen with CÓNCLAVE Agente branding."""
    from PySide6.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QFont, QPen, QRadialGradient
    from PySide6.QtCore import Qt, QRect, QPoint

    W, H = 600, 380
    pixmap = QPixmap(W, H)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Background gradient — deep dark navy
    bg_grad = QLinearGradient(0, 0, W, H)
    bg_grad.setColorAt(0.0, QColor("#080C18"))
    bg_grad.setColorAt(0.5, QColor("#0D1228"))
    bg_grad.setColorAt(1.0, QColor("#050810"))
    painter.fillRect(0, 0, W, H, bg_grad)

    # Radial glow — violet center
    glow = QRadialGradient(W / 2, H / 2, 200)
    glow.setColorAt(0.0, QColor(124, 58, 237, 40))
    glow.setColorAt(0.6, QColor(6, 182, 212, 15))
    glow.setColorAt(1.0, QColor(0, 0, 0, 0))
    painter.fillRect(0, 0, W, H, glow)

    # Border frame
    pen = QPen(QColor(124, 58, 237, 80))
    pen.setWidth(1)
    painter.setPen(pen)
    painter.drawRect(10, 10, W - 20, H - 20)

    # Inner accent line top
    accent_grad = QLinearGradient(0, 12, W, 12)
    accent_grad.setColorAt(0.0, QColor(0, 0, 0, 0))
    accent_grad.setColorAt(0.3, QColor(124, 58, 237, 200))
    accent_grad.setColorAt(0.7, QColor(6, 182, 212, 200))
    accent_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
    pen2 = QPen(accent_grad, 2)
    painter.setPen(pen2)
    painter.drawLine(10, 12, W - 10, 12)

    # Five agent dots — symbolic representation
    agent_colors = ["#7C3AED", "#06B6D4", "#10B981", "#F59E0B", "#EF4444"]
    dot_y = H // 2 - 55
    spacing = 52
    start_x = W // 2 - spacing * 2
    for i, color in enumerate(agent_colors):
        cx = start_x + i * spacing
        # Outer glow ring
        glow_r = QRadialGradient(cx, dot_y, 18)
        glow_r.setColorAt(0.0, QColor(color))
        glow_r.setColorAt(0.5, QColor(color[0:7] + "60"))
        glow_r.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(glow_r)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(cx - 18, dot_y - 18, 36, 36)
        # Inner solid dot
        painter.setBrush(QColor(color))
        painter.drawEllipse(cx - 7, dot_y - 7, 14, 14)

    # Connecting line between dots
    line_grad = QLinearGradient(start_x, dot_y, start_x + spacing * 4, dot_y)
    for i, color in enumerate(agent_colors):
        line_grad.setColorAt(i / 4, QColor(color + "90"))
    pen3 = QPen(line_grad, 1)
    painter.setPen(pen3)
    painter.drawLine(start_x, dot_y, start_x + spacing * 4, dot_y)

    # Main title
    title_font = QFont("Segoe UI", 32, QFont.Weight.Bold)
    painter.setFont(title_font)
    title_grad = QLinearGradient(0, H // 2, W, H // 2)
    title_grad.setColorAt(0.0, QColor("#C4B5FD"))
    title_grad.setColorAt(0.5, QColor("#FFFFFF"))
    title_grad.setColorAt(1.0, QColor("#67E8F9"))
    pen4 = QPen(QColor("#FFFFFF"))
    painter.setPen(pen4)
    painter.drawText(QRect(0, H // 2 - 10, W, 50), Qt.AlignmentFlag.AlignHCenter, "CÓNCLAVE")

    # Subtitle
    sub_font = QFont("Segoe UI", 14, QFont.Weight.Normal)
    painter.setFont(sub_font)
    pen5 = QPen(QColor("#7C3AED"))
    painter.setPen(pen5)
    painter.drawText(QRect(0, H // 2 + 42, W, 30), Qt.AlignmentFlag.AlignHCenter, "A G E N T E")

    # Tagline
    tag_font = QFont("Segoe UI", 9)
    painter.setFont(tag_font)
    pen6 = QPen(QColor("#64748B"))
    painter.setPen(pen6)
    painter.drawText(QRect(0, H - 55, W, 20), Qt.AlignmentFlag.AlignHCenter,
                     "Tu consejo privado de inteligencias artificiales  ·  100% Offline")

    # Version
    ver_font = QFont("Segoe UI", 8)
    painter.setFont(ver_font)
    pen7 = QPen(QColor("#374151"))
    painter.setPen(pen7)
    painter.drawText(QRect(0, H - 30, W - 15, 20), Qt.AlignmentFlag.AlignRight, "v1.0.0  ©2026 ceob68")

    painter.end()
    return pixmap


if __name__ == "__main__":
    main()
