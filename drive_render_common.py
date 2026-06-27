"""Shared utilities for the DriveRender Colab notebook."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

# =============================================================================
# ⚠️ CAMBIA ESTO POR TU USUARIO Y TU REPOSITORIO DE GITHUB
# =============================================================================
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/V3ct0R924/DriveRender/main"
# =============================================================================

DRIVE_RENDER = "/content/drive/MyDrive/DriveRender"
CONFIG_DIR = f"{DRIVE_RENDER}/config"
LANGS_DIR = f"{CONFIG_DIR}/langs"
CONFIG_PATH = f"{CONFIG_DIR}/config.json"
BLENDER_DIR = f"{DRIVE_RENDER}/blender"
PROJECTS_DIR = f"{DRIVE_RENDER}/projects"
OUTPUT_DIR = f"{DRIVE_RENDER}/output"
TEMP_DIR = f"{DRIVE_RENDER}/temp"
SELECTED_FILE_PATH = f"{CONFIG_DIR}/selected_to_render.txt"
SELECTED_META_PATH = f"{CONFIG_DIR}/selected_to_render.meta.json"

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ("en", "es")

class Color:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

def make_translator(lang_dict: dict):
    def T(section: str, key: str, **kwargs) -> str:
        text = lang_dict.get(section, {}).get(key, f"[{section}.{key}]")
        try:
            return text.format(**kwargs) if kwargs else text
        except KeyError as e:
            return f"[{section}.{key} (Missing key: {e})]"
    return T

def load_language_dict(language: str = DEFAULT_LANGUAGE) -> dict:
    lang_path = Path(LANGS_DIR) / f"{language}.json"
    if not lang_path.exists():
        fallback = Path(LANGS_DIR) / f"{DEFAULT_LANGUAGE}.json"
        return json.load(fallback.open("r", encoding="utf-8")) if fallback.exists() else {}
    with lang_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

def load_user_config() -> dict:
    config_path = Path(CONFIG_PATH)
    if not config_path.exists():
        return {}
    try:
        with config_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return {}

def get_user_language(default: str = DEFAULT_LANGUAGE) -> str:
    config = load_user_config()
    language = config.get("language", default)
    return language if language in SUPPORTED_LANGUAGES else default

def ensure_dirs() -> dict[str, str]:
    folders = {
        "base": DRIVE_RENDER,
        "config": CONFIG_DIR,
        "blender": BLENDER_DIR,
        "projects": PROJECTS_DIR,
        "output": OUTPUT_DIR,
        "temp": TEMP_DIR,
    }
    for path in folders.values():
        Path(path).mkdir(parents=True, exist_ok=True)
    return folders

def clean_temp_dir() -> None:
    temp = Path(TEMP_DIR)
    if temp.exists():
        for item in temp.iterdir():
            if item.is_file(): item.unlink()
            elif item.is_dir(): shutil.rmtree(item)

def sanitize_filename(name: str) -> str:
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name.strip())
    sanitized = re.sub(r"\s+", "_", sanitized)
    return re.sub(r"_+", "_", sanitized).strip("._") or "render"

def detect_gpu_compute_backends() -> list[str]:
    try:
        subprocess.run(["nvidia-smi"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5, check=True)
        return ["OPTIX", "CUDA"]
    except Exception:
        return ["CUDA"]

def read_selected_blend_path() -> str | None:
    store = Path(SELECTED_FILE_PATH)
    return store.read_text(encoding="utf-8").strip() if store.exists() else None

def write_selected_blend(path: str, metadata: dict | None = None) -> None:
    Path(SELECTED_FILE_PATH).write_text(path.strip() + "\n", encoding="utf-8")
    if metadata is not None:
        Path(SELECTED_META_PATH).write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

def get_blender_version(executable: str, timeout: int = 10) -> str | None:
    try:
        output = subprocess.check_output([executable, "--version"], encoding="utf-8", stderr=subprocess.STDOUT, timeout=timeout)
        return output.splitlines()[0].strip()
    except Exception:
        return None