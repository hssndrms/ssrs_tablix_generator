import streamlit as st
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "tablix.yaml"

st.title("Tablix Ayarları")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

dataset = st.text_input("Dataset Adı", cfg.get("dataset_name", "DataSet1"))
tablix = st.text_input("Tablix Adı", cfg.get("tablix_name", "Tablix1"))

col1, col2 = st.columns(2)
with col1:
    top = st.text_input("Üst", cfg.get("top", "1cm"))
with col2:
    left = st.text_input("Sol", cfg.get("left", "1cm"))

row_h = st.text_input("Satır Yüksekliği", cfg.get("row_height", "0.6cm"))
header_h = st.text_input("Başlık Yüksekliği", cfg.get("header_height", "0.7cm"))

if st.button("Kaydet"):
    cfg.update({
        "dataset_name": dataset,
        "tablix_name": tablix,
        "top": top,
        "left": left,
        "row_height": row_h,
        "header_height": header_h
    })

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True)

    st.success("Tablix ayarları kaydedildi")
    st.rerun()
