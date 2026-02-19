"""Persist which model to use and its class names (for violation logic)."""
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "model_config.json"
WEIGHTS_DIR = Path(__file__).resolve().parent.parent / "weights"
DEFAULT_MODEL = "yolov8n.pt"


def get_config():
    if not CONFIG_PATH.exists():
        return {"model_path": None, "class_names": None}
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except Exception:
        return {"model_path": None, "class_names": None}


def set_custom_model(weights_path: str, class_names: list):
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump({"model_path": weights_path, "class_names": class_names}, f, indent=2)


def get_model_path():
    cfg = get_config()
    path = cfg.get("model_path")
    if path and Path(path).exists():
        return path
    return DEFAULT_MODEL


def get_class_names():
    cfg = get_config()
    return cfg.get("class_names")
