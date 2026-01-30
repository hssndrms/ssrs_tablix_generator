import streamlit as st
import yaml
from pathlib import Path
import pandas as pd

FORMAT_PATH = Path(__file__).parent.parent / "config" / "formats.yaml"

st.title("Format Ayarları")

# --- YAML oku ---
with open(FORMAT_PATH, "r", encoding="utf-8") as f:
    formats = yaml.safe_load(f)

types = list(formats.keys())

# --- Type seçimi ---
selected_type = st.selectbox(
    "Alan Tipi (TypeName)",
    types
)

type_cfg = formats.get(selected_type, {})

st.markdown("## Varsayılan Ayarlar")

# --- Default ayarlar ---
col1, col2, col3 = st.columns(3)

with col1:
    width = st.text_input(
        "Kolon Genişliği",
        value=type_cfg.get("width", "")
    )

with col2:
    fmt = st.text_input(
        "Format",
        value=type_cfg.get("format") or ""
    )

with col3:
    align = st.selectbox(
        "Hizalama",
        ["Left", "Right", "Center"],
        index=["Left", "Right", "Center"].index(type_cfg.get("align", "Left"))
    )

st.markdown("## Name Override'ları")

# --- Override tablo ---
overrides = type_cfg.get("overrides", {})

ov_df = pd.DataFrame(
    [{"Anahtar": k, "Format": v.get("format"), "Width": v.get("width")}
     for k, v in overrides.items()]
)

edited_ov = st.data_editor(ov_df, num_rows="dynamic")

# --- Kaydet ---
if st.button("Kaydet"):
    # Default ayarları yaz
    formats[selected_type] = {
        "width": width or None,
        "format": fmt or None,
        "align": align
    }

    # Override'ları yaz
    ov_dict = {}
    for _, row in edited_ov.iterrows():
        key = str(row["Anahtar"]).strip().lower()
        if not key:
            continue

        ov_dict[key] = {}
        if pd.notna(row.get("Format")) and row["Format"]:
            ov_dict[key]["format"] = row["Format"]
        if pd.notna(row.get("Width")) and row["Width"]:
            ov_dict[key]["width"] = row["Width"]

    if ov_dict:
        formats[selected_type]["overrides"] = ov_dict

    # YAML'e yaz
    with open(FORMAT_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(formats, f, allow_unicode=True)

    st.success("Format ayarları kaydedildi")
    st.rerun()
