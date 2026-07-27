# core/label_provider.py
import yaml
from pathlib import Path

_CONFIG = Path(__file__).parent.parent / "config"
LABEL_PATH        = _CONFIG / "labels.yaml"
LABEL_CUSTOM_PATH = _CONFIG / "labels_custom.yaml"


def _load(path):
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _merged_labels(lang):
    defaults = _load(LABEL_PATH)
    customs  = _load(LABEL_CUSTOM_PATH)
    return {**defaults.get(lang, {}), **customs.get(lang, {})}


def get_label(field, lang="TR"):
    return _merged_labels(lang).get(field, field)


def has_label(field, lang="TR"):
    return field in _merged_labels(lang)
