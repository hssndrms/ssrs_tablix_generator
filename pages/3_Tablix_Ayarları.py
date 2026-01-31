import time

import streamlit as st
import yaml
from pathlib import Path

from jinja2.utils import concat
from streamlit import color_picker

CONFIG_PATH = Path(__file__).parent.parent / "config" / "tablix.yaml"

st.title("Tablix Ayarları")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

dataset = st.text_input("Dataset Adı", cfg.get("dataset_name", "DataSet1"))
tablix = st.text_input("Tablix Adı", cfg.get("tablix_name", "Tablix1"))

col1_1, col1_2 = st.columns(2)
with col1_1:
    top = st.text_input("Üst", cfg.get("top", "1cm"))
with col1_2:
    left = st.text_input("Sol", cfg.get("left", "1cm"))

row_h = st.text_input("Satır Yüksekliği", cfg.get("row_height", "0.6cm"))
header_h = st.text_input("Başlık Yüksekliği", cfg.get("header_height", "0.7cm"))

col2_1, col2_2, col2_3 = st.columns(3)


def extract_number(size):
    if isinstance(size, str):
        return int(''.join(filter(str.isdigit, size)) or 9)
    return size


with col2_1:
    bckcolor_h = st.color_picker("Başlık Arkaplan Rengi", cfg.get("bckcolor", "#4682B4"))
    st.text(bckcolor_h)

with col2_2:
    txtcolor_h = st.color_picker("Yazı Rengi", cfg.get("txtcolor", "#FFFFFF"))
    st.text(txtcolor_h)

with col2_3:
    textsize_h = st.number_input(
        "Yazı Boyutu (pt)",
        value=extract_number(cfg.get("textsize", 9))
    )

if st.button("Kaydet"):
    cfg.update({
        "dataset_name": dataset,
        "tablix_name": tablix,
        "top": top,
        "left": left,
        "row_height": row_h,
        "header_height": header_h,
        "bckcolor": bckcolor_h,
        "txtcolor": txtcolor_h,
        "textsize": f"{textsize_h}pt"
    })


    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True)

    st.success("Tablix ayarları kaydedildi")
    time.sleep(2)
    st.rerun()
