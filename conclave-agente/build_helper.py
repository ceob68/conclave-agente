#!/usr/bin/env python3
# © 2026 ceob68 / Vaultly. All rights reserved.
"""
build_helper.py — CÓNCLAVE Agente Build Assistant

Verifica el entorno y prepara el proyecto para el build.
Ejecutar con: python build_helper.py

Opciones:
  python build_helper.py check     — Verificar dependencias
  python build_helper.py run       — Lanzar la app directamente
  python build_helper.py build     — Construir el ejecutable con PyInstaller
"""

import sys
import os
import subprocess

def check_dependencies():
    print("=" * 60)
    print("  CÓNCLAVE Agente — Verificación de Dependencias")
    print("=" * 60)

    # Python version
    py_ver = sys.version_info
    status = "✅" if py_ver >= (3, 11) else "❌"
    print(f"\n{status} Python {py_ver.major}.{py_ver.minor}.{py_ver.micro}")
    if py_ver < (3, 11):
        print("   ⚠️  Se requiere Python 3.11 o superior")

    # Check packages
    packages = {
        "PySide6": "PySide6",
        "torch": "PyTorch",
        "transformers": "HuggingFace Transformers",
        "accelerate": "Accelerate",
        "bitsandbytes": "BitsAndBytes",
        "huggingface_hub": "HuggingFace Hub",
        "safetensors": "SafeTensors",
    }

    all_ok = True
    print()
    for pkg, name in packages.items():
        try:
            mod = __import__(pkg)
            ver = getattr(mod, "__version__", "?")
            print(f"  ✅ {name:<30} v{ver}")
        except ImportError:
            print(f"  ❌ {name:<30} NO INSTALADO")
            all_ok = False

    # CUDA check
    print()
    try:
        import torch
        if torch.cuda.is_available():
            gpu = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"  ✅ CUDA disponible")
            print(f"     GPU: {gpu}")
            print(f"     VRAM: {vram:.1f} GB")
            if vram < 6:
                print(f"     ⚠️  VRAM insuficiente. Mínimo recomendado: 12 GB")
            elif vram < 12:
                print(f"     ⚠️  Solo modelos ligeros (2B/4B) funcionarán bien")
        else:
            print("  ⚠️  CUDA no disponible — Modo CPU (muy lento)")
    except Exception as e:
        print(f"  ❌ Error verificando CUDA: {e}")

    print()
    if all_ok:
        print("✅  Todas las dependencias están instaladas. Listo para ejecutar.")
    else:
        print("❌  Faltan dependencias. Instálalas con:")
        print("    pip install -r requirements.txt")
    print()
    return all_ok


def run_app():
    print("Iniciando CÓNCLAVE Agente...")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.run([sys.executable, "desktop_app.py"])


def build_exe():
    print("=" * 60)
    print("  CÓNCLAVE Agente — Build con PyInstaller")
    print("=" * 60)
    print()

    # Check PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} encontrado")
    except ImportError:
        print("❌ PyInstaller no instalado. Instálalo con:")
        print("   pip install pyinstaller")
        return

    print("\nEjecutando PyInstaller...")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "conclave_agente.spec", "--clean"],
        capture_output=False
    )

    if result.returncode == 0:
        print("\n✅ Build exitoso!")
        print("   Ejecutable: dist/CONCLAVE_Agente/CONCLAVE_Agente.exe")
        print("\nPróximo paso:")
        print("   Abrir installer/conclave_setup.iss en Inno Setup Compiler")
        print("   y hacer clic en Build → Compile para generar el .exe instalador.")
    else:
        print("\n❌ Error en el build. Revisa la salida de PyInstaller arriba.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"

    if cmd == "check":
        check_dependencies()
    elif cmd == "run":
        if check_dependencies():
            run_app()
    elif cmd == "build":
        if check_dependencies():
            build_exe()
    else:
        print(f"Comando desconocido: {cmd}")
        print("Uso: python build_helper.py [check|run|build]")
