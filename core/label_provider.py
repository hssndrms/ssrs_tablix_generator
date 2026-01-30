# core/label_provider.py
import yaml
from pathlib import Path

LABEL_PATH = Path(__file__).parent.parent / "config" / "labels.yaml"

def get_label(field, lang="TR"):
    with open(LABEL_PATH, "r", encoding="utf-8") as f:
        labels = yaml.safe_load(f) or {}

    return labels.get(lang, {}).get(field, field)
