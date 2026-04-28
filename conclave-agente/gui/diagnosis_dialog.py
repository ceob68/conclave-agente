# © 2026 ceob68 / Vaultly. All rights reserved.
# Unauthorized copying, distribution or modification is prohibited.

"""
diagnosis_dialog.py — System Diagnostics Dialog

Shows real-time GPU info, VRAM status, and dependency checks.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame, QProgressBar, QDialogButtonBox, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class DiagnosisDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Diagnóstico del Sistema — CÓNCLAVE Agente")
        self.setMinimumSize(600, 520)
        self._setup_ui()
        self._refresh()

        # Auto-refresh every 2 seconds
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_vram)
        self._timer.start(2000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 12)
        layout.setSpacing(12)

        # Title
        title = QLabel("🔬  Diagnóstico del Sistema")
        title.setStyleSheet("font-size: 13pt; font-weight: 700; color: #FFFFFF;")
        layout.addWidget(title)

        # GPU Group
        gpu_group = QGroupBox("GPU & VRAM")
        gpu_group.setStyleSheet(
            "QGroupBox { color: #7C3AED; font-weight: 700; border: 1px solid #2A3A5C; "
            "border-radius: 8px; margin-top: 8px; padding-top: 8px; } "
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; }"
        )
        gpu_layout = QVBoxLayout(gpu_group)
        gpu_layout.setSpacing(8)

        # GPU name
        self._gpu_name_lbl = QLabel("GPU: Detectando...")
        self._gpu_name_lbl.setStyleSheet("color: #E8EAF0; font-size: 10pt;")
        gpu_layout.addWidget(self._gpu_name_lbl)

        # CUDA
        self._cuda_lbl = QLabel("CUDA: —")
        self._cuda_lbl.setStyleSheet("color: #8892A4; font-size: 9pt;")
        gpu_layout.addWidget(self._cuda_lbl)

        # VRAM bar
        vram_row = QHBoxLayout()
        vram_lbl = QLabel("VRAM:")
        vram_lbl.setStyleSheet("color: #8892A4; font-size: 9pt;")
        vram_lbl.setFixedWidth(50)
        vram_row.addWidget(vram_lbl)
        self._vram_bar = QProgressBar()
        self._vram_bar.setRange(0, 100)
        self._vram_bar.setValue(0)
        self._vram_bar.setFixedHeight(12)
        vram_row.addWidget(self._vram_bar, 1)
        self._vram_text_lbl = QLabel("— / —")
        self._vram_text_lbl.setStyleSheet("color: #8892A4; font-size: 9pt;")
        self._vram_text_lbl.setFixedWidth(100)
        vram_row.addWidget(self._vram_text_lbl)
        gpu_layout.addLayout(vram_row)

        layout.addWidget(gpu_group)

        # Dependencies Group
        deps_group = QGroupBox("Dependencias")
        deps_group.setStyleSheet(
            "QGroupBox { color: #06B6D4; font-weight: 700; border: 1px solid #2A3A5C; "
            "border-radius: 8px; margin-top: 8px; padding-top: 8px; } "
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; }"
        )
        deps_layout = QVBoxLayout(deps_group)

        self._deps_text = QTextEdit()
        self._deps_text.setReadOnly(True)
        self._deps_text.setFixedHeight(160)
        self._deps_text.setStyleSheet(
            "QTextEdit { background: #0D1228; border: none; color: #B0B8CC; font-size: 9pt; font-family: 'Cascadia Code', 'Consolas', monospace; }"
        )
        deps_layout.addWidget(self._deps_text)
        layout.addWidget(deps_group)

        # Model Cache Group
        cache_group = QGroupBox("Modelos en Caché Local")
        cache_group.setStyleSheet(
            "QGroupBox { color: #10B981; font-weight: 700; border: 1px solid #2A3A5C; "
            "border-radius: 8px; margin-top: 8px; padding-top: 8px; } "
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; }"
        )
        cache_layout = QVBoxLayout(cache_group)
        self._cache_text = QTextEdit()
        self._cache_text.setReadOnly(True)
        self._cache_text.setFixedHeight(120)
        self._cache_text.setStyleSheet(
            "QTextEdit { background: #0D1228; border: none; color: #B0B8CC; font-size: 9pt; font-family: 'Cascadia Code', 'Consolas', monospace; }"
        )
        cache_layout.addWidget(self._cache_text)
        layout.addWidget(cache_group)

        layout.addStretch()

        # Button row
        btn_row = QHBoxLayout()
        btn_refresh = QPushButton("🔄  Actualizar")
        btn_refresh.clicked.connect(self._refresh)
        btn_row.addWidget(btn_refresh)
        btn_row.addStretch()
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _refresh(self):
        """Full refresh of all sections."""
        self._refresh_vram()
        self._refresh_deps()
        self._refresh_cache()

    def _refresh_vram(self):
        """Update GPU/VRAM section."""
        try:
            from backend.ai_engine import get_gpu_info
            info = get_gpu_info()

            if info["cuda_available"]:
                self._gpu_name_lbl.setText(f"GPU: {info['gpu_name']}")
                self._cuda_lbl.setText(
                    f"CUDA: {info['compute_capability']}  ·  Total: {info['vram_total_gb']:.1f} GB"
                )
                total = info["vram_total_gb"]
                used = info["vram_used_gb"]
                free = info["vram_free_gb"]
                pct = int((used / total * 100)) if total > 0 else 0
                self._vram_bar.setValue(pct)
                self._vram_text_lbl.setText(f"{used:.1f} / {total:.1f} GB")

                if pct > 85:
                    self._vram_bar.setStyleSheet(
                        "QProgressBar::chunk { background: #EF4444; }"
                    )
                elif pct > 60:
                    self._vram_bar.setStyleSheet(
                        "QProgressBar::chunk { background: #F59E0B; }"
                    )
                else:
                    self._vram_bar.setStyleSheet("")  # Use default stylesheet
            else:
                self._gpu_name_lbl.setText("GPU: No disponible (modo CPU)")
                self._cuda_lbl.setText("CUDA: No detectado — La inferencia será muy lenta en CPU")
                self._vram_bar.setValue(0)
                self._vram_text_lbl.setText("N/A")
        except Exception as e:
            self._gpu_name_lbl.setText(f"Error al obtener info GPU: {e}")

    def _refresh_deps(self):
        """Check and display dependency status."""
        try:
            from backend.ai_engine import check_dependencies
            deps = check_dependencies()
            lines = []
            for name, status in deps.items():
                lines.append(f"{status}  {name}")
            self._deps_text.setPlainText("\n".join(lines))
        except Exception as e:
            self._deps_text.setPlainText(f"Error: {e}")

    def _refresh_cache(self):
        """Check which models are downloaded locally."""
        import os
        from backend.ai_engine import MODEL_REGISTRY

        cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
        lines = []

        agent_names = ["Arquitecto", "Programador", "Seguridad", "QA/UX", "Documentador"]
        for agent_id, model_id in MODEL_REGISTRY.items():
            model_cache_name = "models--" + model_id.replace("/", "--")
            cached = os.path.exists(os.path.join(cache_dir, model_cache_name))
            status = "✅" if cached else "❌"
            name = agent_names[agent_id] if agent_id < len(agent_names) else f"#{agent_id}"
            lines.append(f"{status}  [{name}]  {model_id}")

        if not lines:
            lines = ["No se encontraron modelos descargados."]

        self._cache_text.setPlainText(
            f"Directorio caché: {cache_dir}\n\n" + "\n".join(lines)
        )

    def closeEvent(self, event):
        self._timer.stop()
        super().closeEvent(event)
