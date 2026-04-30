# © 2026 ceob68 / Vaultly. All rights reserved.
# Unauthorized copying, distribution or modification is prohibited.

"""
settings_dialog.py — CÓNCLAVE Agente Settings & Model Download Dialog
"""

import os
import json
import threading
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFrame, QProgressBar, QMessageBox,
    QDialogButtonBox, QTabWidget, QWidget, QGroupBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread

SETTINGS_PATH = os.path.join(os.path.expanduser("~"), ".conclave_agente", "settings.json")


def load_settings() -> dict:
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"hf_token": "", "default_model": "google/gemma-3-1b-it"}


def save_settings(data: dict):
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(data, f, indent=2)


def get_hf_token() -> str:
    """Get HuggingFace token from settings or environment."""
    # Check env first
    env_token = os.environ.get("HF_TOKEN", "")
    if env_token:
        return env_token
    # Then settings file
    return load_settings().get("hf_token", "")


class DownloadWorker(QThread):
    log_signal = Signal(str)
    progress_signal = Signal(int)
    finished_signal = Signal(bool, str)  # success, message

    def __init__(self, model_id: str, token: str):
        super().__init__()
        self.model_id = model_id
        self.token = token

    def run(self):
        try:
            self.log_signal.emit(f"Iniciando descarga de {self.model_id}...")
            self.progress_signal.emit(10)

            if self.token:
                os.environ["HF_TOKEN"] = self.token
                os.environ["HUGGING_FACE_HUB_TOKEN"] = self.token

            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch

            self.log_signal.emit("Descargando tokenizer...")
            self.progress_signal.emit(20)

            AutoTokenizer.from_pretrained(
                self.model_id,
                token=self.token or None,
            )

            self.log_signal.emit("Tokenizer listo. Descargando modelo (puede tardar varios minutos)...")
            self.progress_signal.emit(40)

            AutoModelForCausalLM.from_pretrained(
                self.model_id,
                token=self.token or None,
                torch_dtype=torch.float32,
                device_map="cpu",
                low_cpu_mem_usage=True,
            )

            self.progress_signal.emit(100)
            self.finished_signal.emit(True, f"✅ Modelo {self.model_id} descargado correctamente.")

        except Exception as e:
            err = str(e)
            if "401" in err or "authentication" in err.lower() or "token" in err.lower():
                msg = (
                    "❌ Error de autenticación (401).\n\n"
                    "Gemma-3 requiere:\n"
                    "1. Cuenta en huggingface.co (gratis)\n"
                    "2. Aceptar la licencia en: huggingface.co/google/gemma-3-1b-it\n"
                    "3. Crear un token en: huggingface.co/settings/tokens\n"
                    "4. Pegar el token en el campo 'Token HuggingFace' y guardar"
                )
            elif "403" in err:
                msg = (
                    "❌ Acceso denegado (403).\n\n"
                    "Debes aceptar la licencia del modelo primero:\n"
                    "Ve a huggingface.co/google/gemma-3-1b-it\n"
                    "y haz clic en 'Agree and access repository'"
                )
            elif "429" in err or "rate" in err.lower():
                msg = "❌ Rate limit de HuggingFace. Espera unos minutos y vuelve a intentarlo."
            else:
                msg = f"❌ Error: {err[:300]}"

            self.finished_signal.emit(False, msg)


class SettingsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración — CÓNCLAVE Agente")
        self.setMinimumSize(620, 520)
        self._settings = load_settings()
        self._worker = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 12)
        layout.setSpacing(10)

        tabs = QTabWidget()

        # ── Tab 1: HuggingFace ──────────────────────────────────────────────
        hf_tab = QWidget()
        hf_layout = QVBoxLayout(hf_tab)
        hf_layout.setSpacing(10)

        # Info box
        info = QLabel(
            "⚠️  Los modelos Gemma-3 de Google requieren autenticación en HuggingFace.\n"
            "Es gratuito. Sigue estos 3 pasos antes de descargar:"
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            "background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.4); "
            "border-radius: 8px; padding: 10px; color: #FDE68A; font-size: 9pt;"
        )
        hf_layout.addWidget(info)

        # Steps
        steps_group = QGroupBox("Pasos para obtener el token")
        steps_group.setStyleSheet(
            "QGroupBox { color: #06B6D4; font-weight: 700; border: 1px solid #2A3A5C; "
            "border-radius: 8px; margin-top: 8px; padding-top: 8px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; }"
        )
        steps_layout = QVBoxLayout(steps_group)
        steps = [
            "1. Crea cuenta gratis en:  https://huggingface.co/join",
            "2. Acepta la licencia en:  https://huggingface.co/google/gemma-3-1b-it",
            "3. Crea tu token en:  https://huggingface.co/settings/tokens  (tipo Read)",
        ]
        for step in steps:
            lbl = QLabel(step)
            lbl.setStyleSheet("color: #E8EAF0; font-size: 9pt; padding: 2px 4px;")
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            steps_layout.addWidget(lbl)
        hf_layout.addWidget(steps_group)

        # Token input
        token_group = QGroupBox("Token de HuggingFace")
        token_group.setStyleSheet(
            "QGroupBox { color: #7C3AED; font-weight: 700; border: 1px solid #2A3A5C; "
            "border-radius: 8px; margin-top: 8px; padding-top: 8px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; }"
        )
        token_layout = QVBoxLayout(token_group)

        token_row = QHBoxLayout()
        self._token_input = QLineEdit()
        self._token_input.setPlaceholderText("hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        self._token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._token_input.setText(self._settings.get("hf_token", ""))
        token_row.addWidget(self._token_input, 1)

        btn_show = QPushButton("👁")
        btn_show.setFixedWidth(36)
        btn_show.setCheckable(True)
        btn_show.toggled.connect(
            lambda checked: self._token_input.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        token_row.addWidget(btn_show)
        token_layout.addLayout(token_row)

        btn_save_token = QPushButton("💾  Guardar Token")
        btn_save_token.setObjectName("btn_primary")
        btn_save_token.clicked.connect(self._save_token)
        token_layout.addWidget(btn_save_token)

        hf_layout.addWidget(token_group)
        hf_layout.addStretch()
        tabs.addTab(hf_tab, "🔑  HuggingFace Token")

        # ── Tab 2: Download Models ──────────────────────────────────────────
        dl_tab = QWidget()
        dl_layout = QVBoxLayout(dl_tab)
        dl_layout.setSpacing(10)

        dl_info = QLabel(
            "Descarga el modelo mínimo para empezar a usar CÓNCLAVE Agente.\n"
            "Gemma-3 1B es el más ligero (~0.8 GB) y funciona bien en CPU."
        )
        dl_info.setWordWrap(True)
        dl_info.setStyleSheet("color: #8892A4; font-size: 9pt;")
        dl_layout.addWidget(dl_info)

        # Model selector
        model_group = QGroupBox("Modelo a descargar")
        model_group.setStyleSheet(
            "QGroupBox { color: #10B981; font-weight: 700; border: 1px solid #2A3A5C; "
            "border-radius: 8px; margin-top: 8px; padding-top: 8px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; }"
        )
        model_layout = QVBoxLayout(model_group)

        from PySide6.QtWidgets import QComboBox
        self._model_combo = QComboBox()
        models = [
            ("google/gemma-3-1b-it", "Gemma-3 1B  —  ~0.8 GB  —  Recomendado para CPU"),
            ("google/gemma-3-4b-it", "Gemma-3 4B  —  ~2.5 GB  —  Mejor calidad"),
            ("microsoft/phi-4",      "Phi-4 (Microsoft)  —  ~8 GB  —  Excelente en CPU"),
            ("Qwen/Qwen2.5-1.5B-Instruct", "Qwen 2.5 1.5B  —  ~1 GB  —  Ultra ligero"),
        ]
        for model_id, label in models:
            self._model_combo.addItem(label, model_id)
        model_layout.addWidget(self._model_combo)

        btn_download = QPushButton("⬇️  Descargar Modelo Seleccionado")
        btn_download.setObjectName("btn_start")
        btn_download.clicked.connect(self._start_download)
        model_layout.addWidget(btn_download)
        dl_layout.addWidget(model_group)

        # Progress
        self._progress_bar = QProgressBar()
        self._progress_bar.setValue(0)
        self._progress_bar.setVisible(False)
        dl_layout.addWidget(self._progress_bar)

        # Log
        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setFixedHeight(160)
        self._log_view.setStyleSheet(
            "QTextEdit { background: #0D1228; border: 1px solid #2A3A5C; "
            "color: #B0B8CC; font-size: 8.5pt; font-family: Consolas, monospace; }"
        )
        self._log_view.setPlaceholderText("El progreso de la descarga aparecerá aquí...")
        dl_layout.addWidget(self._log_view)
        dl_layout.addStretch()
        tabs.addTab(dl_tab, "⬇️  Descargar Modelos")

        layout.addWidget(tabs, 1)

        # Close button
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _save_token(self):
        token = self._token_input.text().strip()
        self._settings["hf_token"] = token
        save_settings(self._settings)
        # Apply to environment immediately
        if token:
            os.environ["HF_TOKEN"] = token
            os.environ["HUGGING_FACE_HUB_TOKEN"] = token
        QMessageBox.information(self, "Guardado", "✅ Token guardado correctamente.")

    def _start_download(self):
        token = self._token_input.text().strip() or self._settings.get("hf_token", "")
        if not token:
            QMessageBox.warning(
                self, "Token requerido",
                "Debes guardar tu token de HuggingFace antes de descargar.\n"
                "Ve a la pestaña 'HuggingFace Token' y guarda tu token."
            )
            return

        model_id = self._model_combo.currentData()
        self._log_view.clear()
        self._progress_bar.setVisible(True)
        self._progress_bar.setValue(0)

        self._worker = DownloadWorker(model_id, token)
        self._worker.log_signal.connect(self._on_log)
        self._worker.progress_signal.connect(self._progress_bar.setValue)
        self._worker.finished_signal.connect(self._on_download_finished)
        self._worker.start()

    def _on_log(self, msg: str):
        self._log_view.append(msg)
        sb = self._log_view.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_download_finished(self, success: bool, message: str):
        self._progress_bar.setValue(100 if success else 0)
        self._log_view.append(message)
        if success:
            QMessageBox.information(self, "Descarga completada", message)
        else:
            QMessageBox.critical(self, "Error en la descarga", message)
