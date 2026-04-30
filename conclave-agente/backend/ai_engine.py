# © 2026 ceob68 / Vaultly. All rights reserved.
# Unauthorized copying, distribution or modification is prohibited.

"""
ai_engine.py — CÓNCLAVE Agente AI Engine

Core responsibilities:
  1. Dynamic model loading (demand-based, one at a time)
  2. BitsAndBytes NF4 4-bit quantization with double quantization
  3. Streaming token generation via TextIteratorStreamer
  4. Aggressive VRAM release after each agent turn
  5. Fallback handling when models are not cached
"""

import gc
import os
import threading
from typing import Generator, Optional, Callable

# These will be imported lazily to speed up startup
_torch = None
_transformers = None
_bnb = None


def _lazy_imports():
    global _torch, _transformers, _bnb
    if _torch is None:
        import torch
        _torch = torch
    if _transformers is None:
        import transformers
        _transformers = transformers
    if _bnb is None:
        try:
            import bitsandbytes
            _bnb = bitsandbytes
        except ImportError:
            _bnb = None


# ─── Model Registry ──────────────────────────────────────────────────────────

# Maps agent_id → HuggingFace model ID
MODEL_REGISTRY = {
    0: "google/gemma-3-1b-it",            # Arquitecto   — 1B
    1: "google/gemma-3-4b-it",            # Programador  — 4.4B E4B
    2: "google/gemma-3-27b-it",           # Seguridad    — 27B (was 26B MoE)
    3: "google/gemma-3-12b-it",           # QA/UX        — 12B Dense (realistic for RTX 3060)
    4: "google/gemma-3-1b-it",            # Documentador — 1B
}

# VRAM budget per model (in GB) — for max_memory config
VRAM_BUDGET = {
    0: {"gpu": "14GiB", "cpu": "4GiB"},
    1: {"gpu": "14GiB", "cpu": "4GiB"},
    2: {"gpu": "14GiB", "cpu": "24GiB"},  # Large model needs CPU offload
    3: {"gpu": "14GiB", "cpu": "16GiB"},
    4: {"gpu": "14GiB", "cpu": "4GiB"},
}


def _get_bnb_config():
    """Return BitsAndBytesConfig for NF4 4-bit double quantization."""
    _lazy_imports()
    return _transformers.BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=_torch.bfloat16,
    )


def _get_device_map(agent_id: int) -> dict:
    """Build device_map for this agent's model."""
    _lazy_imports()
    if not _torch.cuda.is_available():
        return {"device_map": "cpu"}

    budget = VRAM_BUDGET.get(agent_id, {"gpu": "14GiB", "cpu": "8GiB"})
    return {
        "device_map": "auto",
        "max_memory": {
            0: budget["gpu"],     # GPU 0
            "cpu": budget["cpu"],
        }
    }


def load_model_and_tokenizer(model_id: str,
                              log_callback=None):
    """
    Load a model and tokenizer.
    - With CUDA GPU: uses BitsAndBytes NF4 4-bit quantization
    - Without GPU (CPU mode): loads in float32, no quantization
    """
    _lazy_imports()

    if log_callback:
        log_callback(f"[AI Engine] Cargando modelo: {model_id}")

    # Check if model is cached locally
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
    model_cache_name = "models--" + model_id.replace("/", "--")
    is_cached = os.path.exists(os.path.join(cache_dir, model_cache_name))

    if not is_cached:
        if log_callback:
            log_callback(
                f"[AI Engine] ⚠️  Modelo '{model_id}' no encontrado en caché. "
                f"Necesita descargarse. Asegúrate de tener conexión a internet."
            )

    cuda_available = _torch.cuda.is_available()
    bnb_available = _bnb is not None

    try:
        tokenizer = _transformers.AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=True,
        )

        if cuda_available and bnb_available:
            # ── GPU mode: NF4 4-bit quantization ──────────────────────────────
            if log_callback:
                log_callback(f"[AI Engine] Modo GPU — cuantización NF4 4-bit activada")

            bnb_config = _transformers.BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=_torch.bfloat16,
            )

            # Determine VRAM budget
            total_vram = _torch.cuda.get_device_properties(0).total_memory / (1024**3)
            gpu_budget = f"{int(total_vram * 0.90)}GiB"

            model = _transformers.AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=bnb_config,
                device_map="auto",
                max_memory={0: gpu_budget, "cpu": "16GiB"},
                trust_remote_code=True,
                torch_dtype=_torch.bfloat16,
            )

        else:
            # ── CPU mode: no quantization, float32 ────────────────────────────
            if log_callback:
                log_callback(
                    f"[AI Engine] Modo CPU — sin cuantización. "
                    f"Respuestas lentas esperadas (5-20 min por agente)."
                )

            model = _transformers.AutoModelForCausalLM.from_pretrained(
                model_id,
                device_map="cpu",
                trust_remote_code=True,
                torch_dtype=_torch.float32,
                low_cpu_mem_usage=True,
            )

        model.eval()

        if log_callback:
            if cuda_available:
                vram_used = _get_vram_used_gb()
                log_callback(f"[AI Engine] ✅ Modelo cargado. VRAM usada: {vram_used:.1f} GB")
            else:
                log_callback(f"[AI Engine] ✅ Modelo cargado en CPU.")

        return model, tokenizer

    except Exception as e:
        if log_callback:
            log_callback(f"[AI Engine] ❌ Error cargando modelo '{model_id}': {e}")
        raise


def generate_streaming(model, tokenizer, prompt: str,
                        max_new_tokens: int = 1024,
                        temperature: float = 0.7,
                        token_callback: Optional[Callable[[str], None]] = None,
                        stop_event: Optional[threading.Event] = None) -> str:
    """
    Run streaming inference. Calls token_callback for each token.
    Returns the full generated text.
    """
    _lazy_imports()

    from transformers import TextIteratorStreamer

    inputs = tokenizer(prompt, return_tensors="pt")
    input_ids = inputs["input_ids"]

    if _torch.cuda.is_available():
        # Move only input_ids to device
        device = next(model.parameters()).device
        input_ids = input_ids.to(device)

    streamer = TextIteratorStreamer(
        tokenizer,
        skip_special_tokens=True,
        skip_prompt=True,
    )

    gen_kwargs = {
        "input_ids": input_ids,
        "max_new_tokens": max_new_tokens,
        "temperature": temperature,
        "do_sample": temperature > 0,
        "top_p": 0.92,
        "repetition_penalty": 1.1,
        "streamer": streamer,
        "pad_token_id": tokenizer.eos_token_id,
    }

    # Run generation in a background thread
    gen_thread = threading.Thread(target=model.generate, kwargs=gen_kwargs, daemon=True)
    gen_thread.start()

    full_text = []
    for token in streamer:
        if stop_event and stop_event.is_set():
            break
        full_text.append(token)
        if token_callback:
            token_callback(token)

    gen_thread.join(timeout=5)
    return "".join(full_text)


def release_model(model, log_callback: Optional[Callable] = None):
    """Aggressively free model memory and VRAM."""
    _lazy_imports()

    if model is None:
        return

    try:
        # accelerate release
        try:
            from accelerate import release_memory
            release_memory(model)
        except Exception:
            pass

        del model
        gc.collect()

        if _torch.cuda.is_available():
            _torch.cuda.empty_cache()
            _torch.cuda.synchronize()

        if log_callback:
            vram_free = _get_vram_free_gb()
            log_callback(f"[AI Engine] 🗑️  Modelo liberado. VRAM libre: {vram_free:.1f} GB")

    except Exception as e:
        if log_callback:
            log_callback(f"[AI Engine] ⚠️  Error liberando modelo: {e}")


# ─── Diagnostics ──────────────────────────────────────────────────────────────

def get_gpu_info() -> dict:
    """Return GPU diagnostics dictionary."""
    _lazy_imports()
    info = {
        "cuda_available": False,
        "gpu_name": "N/A",
        "vram_total_gb": 0.0,
        "vram_used_gb": 0.0,
        "vram_free_gb": 0.0,
        "compute_capability": "N/A",
    }
    try:
        if _torch.cuda.is_available():
            info["cuda_available"] = True
            info["gpu_name"] = _torch.cuda.get_device_name(0)
            total = _torch.cuda.get_device_properties(0).total_memory
            used = _torch.cuda.memory_allocated(0)
            info["vram_total_gb"] = total / (1024 ** 3)
            info["vram_used_gb"] = used / (1024 ** 3)
            info["vram_free_gb"] = (total - used) / (1024 ** 3)
            cc = _torch.cuda.get_device_capability(0)
            info["compute_capability"] = f"{cc[0]}.{cc[1]}"
    except Exception:
        pass
    return info


def _get_vram_used_gb() -> float:
    try:
        return _torch.cuda.memory_allocated(0) / (1024 ** 3)
    except Exception:
        return 0.0


def _get_vram_free_gb() -> float:
    try:
        total = _torch.cuda.get_device_properties(0).total_memory
        used = _torch.cuda.memory_allocated(0)
        return (total - used) / (1024 ** 3)
    except Exception:
        return 0.0


def _estimate_model_size(agent_id: int) -> str:
    sizes = {0: "1.5", 1: "2.5", 2: "13.5", 3: "7.0", 4: "1.5"}
    return sizes.get(agent_id, "?")


def check_dependencies() -> dict:
    """Check if all required packages are available."""
    results = {}
    packages = [
        ("torch", "PyTorch"),
        ("transformers", "HuggingFace Transformers"),
        ("bitsandbytes", "BitsAndBytes (cuantización 4-bit)"),
        ("accelerate", "Accelerate (gestión de dispositivos)"),
        ("PySide6", "PySide6 (interfaz gráfica)"),
    ]
    for pkg, name in packages:
        try:
            __import__(pkg)
            results[name] = "✅ Instalado"
        except ImportError:
            results[name] = "❌ No instalado"

    # Check CUDA
    try:
        import torch
        results["CUDA"] = f"✅ Disponible ({torch.version.cuda})" if torch.cuda.is_available() else "⚠️  No disponible (modo CPU)"
    except Exception:
        results["CUDA"] = "❌ Error al verificar"

    return results
