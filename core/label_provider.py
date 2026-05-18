# core/label_provider.py
import yaml
from pathlib import Path

_CONFIG = Path(__file__).parent.parent / "config"
LABEL_PATH        = _CONFIG / "labels.yaml"
LABEL_CUSTOM_PATH = _CONFIG / "labels_custom.yaml"


def get_label(field, lang="TR"):
    def _load(path):
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    defaults = _load(LABEL_PATH)
    customs  = _load(LABEL_CUSTOM_PATH)

    merged = {**defaults.get(lang, {}), **customs.get(lang, {})}
    return merged.get(field, field)
