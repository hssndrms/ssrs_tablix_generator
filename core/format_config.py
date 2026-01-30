import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "formats.yaml"


def resolve_format(name: str, type_name: str):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        format_config = yaml.safe_load(f) or {}

    cfg = format_config.get(type_name, {})
    fmt = cfg.get("format")
    width = cfg.get("width", "25mm")
    align = cfg.get("align", "Left")

    overrides = cfg.get("overrides", {})
    lname = name.lower()

    for key, override in overrides.items():
        if key in lname:
            fmt = override.get("format", fmt)
            width = override.get("width", width)
            align = override.get("align", align)

    return {
        "format": fmt,
        "width": width,
        "align": align
    }
