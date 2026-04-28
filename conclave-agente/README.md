# ◆ CÓNCLAVE Agente

> **Tu consejo privado de inteligencias artificiales — 100% Offline**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)](https://python.org)
[![PySide6](https://img.shields.io/badge/PySide6-6.7+-green?style=flat-square)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=flat-square)](LICENSE.txt)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue?style=flat-square&logo=windows)](https://microsoft.com/windows)

---

## 🎯 ¿Qué es CÓNCLAVE Agente?

CÓNCLAVE Agente es un sistema de escritorio Windows que ejecuta **5 agentes de IA especializados** en un bucle de debate iterativo, completamente **offline**, sin APIs en la nube, sin suscripciones.

Cada agente tiene un rol fijo (Arquitecto, Programador, Seguridad, QA/UX, Documentador) y trabaja con modelos Google Gemma-4 cuantizados a 4-bit. Los agentes heredan el contexto entre sí, construyendo y criticando ideas de forma incremental.

### El problema que resuelve

En lugar de depender de un único modelo masivo o de APIs de pago, CÓNCLAVE Agente aprovecha modelos Small/Medium Language Models cuantizados para mantener una conversación estructurada entre múltiples "expertos" virtuales — todo en tu hardware local.

---

## 🚀 Características Principales

- **5 Agentes Especializados**: Arquitecto, Programador, Seguridad, QA/UX, Documentador
- **100% Offline**: Sin APIs, sin internet durante el uso, sin costes recurrentes
- **Gestión Dinámica de VRAM**: Carga/descarga de modelos entre turnos — soporta GPUs de 12-16 GB
- **Streaming en Tiempo Real**: Tokens aparecen token por token en la UI
- **Intervención del Manager**: Inyecta mensajes en la sesión activa en caliente
- **Personalización Completa**: Configura roles, modelos y disponibilidad de cada agente
- **Historial de Sesiones**: SQLite local — todas tus sesiones guardadas
- **Borrador Acumulativo**: El Documentador sintetiza cada ciclo en un draft evolutivo
- **Diseño Enterprise**: UI glassmorphism con gradientes profundos, nivel Raycast/Linear

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|---|---|
| UI Framework | PySide6 (Qt 6.7+) |
| Inferencia | PyTorch + HuggingFace Transformers |
| Cuantización | BitsAndBytes NF4 4-bit + doble cuantización |
| Gestión GPU | Accelerate (device_map auto + CPU offload) |
| Streaming | TextIteratorStreamer |
| Base de datos | SQLite3 (nativo Python) |
| Modelos | Google Gemma-3/4 (2B, 4B, 12B, 27B) |
| Empaquetado | PyInstaller + Inno Setup |

---

## 📋 Requisitos del Sistema

| Componente | Mínimo | Recomendado |
|---|---|---|
| OS | Windows 10 64-bit | Windows 11 |
| GPU | NVIDIA GTX 1660 (6 GB VRAM) | RTX 3060/4070 (12-16 GB) |
| RAM | 16 GB | 32 GB |
| Almacenamiento | 30 GB libres | 60 GB (para todos los modelos) |
| Python | 3.11+ | 3.13 |

> ⚠️ **CPU-only**: Funciona pero muy lento (5-15 min/respuesta). GPU recomendada.

---

## 🔧 Instalación para Desarrolladores

### 1. Clonar el repo

```powershell
git clone https://github.com/ceob68/conclave-agente.git
cd conclave-agente
```

### 2. Crear entorno virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar PyTorch con CUDA

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

### 4. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 5. Ejecutar

```powershell
python desktop_app.py
```

### Primera vez — Descargar modelos

Los modelos se descargan automáticamente de HuggingFace Hub la primera vez. Asegúrate de tener conexión a internet.

```powershell
# Descargar el modelo ligero primero para probar
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('google/gemma-3-2b-it')"
```

---

## 📦 Build del Instalador

```powershell
# Generar ejecutable con PyInstaller
pyinstaller conclave_agente.spec

# El instalador .exe se genera con Inno Setup
# Abrir installer/conclave_setup.iss en Inno Setup Compiler
```

---

## 📁 Estructura del Proyecto

```
conclave-agente/
├── desktop_app.py              ← Entry Point + Splash Screen
├── backend/
│   ├── ai_engine.py            ← Carga/descarga modelos, inferencia, VRAM
│   ├── orchestrator.py         ← Bucle infinito, 5 agentes, control de sesión
│   └── database.py             ← SQLite: sesiones y mensajes
├── gui/
│   ├── main_window.py          ← UI principal (3 paneles)
│   ├── customization_dialog.py ← Configuración de agentes
│   ├── diagnosis_dialog.py     ← Diagnóstico GPU/VRAM/dependencias
│   ├── ai_worker.py            ← QThread wrapper del enjambre
│   ├── components.py           ← Widgets personalizados
│   └── app_style.py            ← QSS enterprise theme
├── config/
│   ├── current_config.json     ← Config activa de agentes
│   └── settings.json           ← Configuración global
├── requirements.txt
└── installer/
    └── conclave_setup.iss      ← Inno Setup script
```

---

## 📄 Licencia

**Propietaria — Todos los derechos reservados.**

© 2026 ceob68 / Vaultly. Prohibida la redistribución, copia, reventa o ingeniería inversa.  
Ver [LICENSE.txt](LICENSE.txt) para términos completos.

---

## 🛒 Disponible en Vaultly

**Precio: 29 USDT**  
[Comprar en Vaultly](https://vaultly.ceob68.com)
