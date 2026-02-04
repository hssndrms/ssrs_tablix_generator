import time

import streamlit as st
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "tablix.yaml"

st.set_page_config(layout="centered")
st.title("Tablix Ayarları")
st.subheader("Genel", divider="grey", anchor=False)

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

dataset = st.text_input("Dataset Adı", cfg.get("dataset_name", "DataSet1"), icon=":material/database:")
tablix = st.text_input("Tablix Adı", cfg.get("tablix_name", "Tablix1"), icon=":material/table:")

st.subheader("Pozisyon", divider="grey", anchor=False)
col1_1, col1_2 = st.columns(2)
with col1_1:
    top = st.text_input("Üstten Konum", cfg.get("top", "1cm"))
with col1_2:
    left = st.text_input("Soldan Konum", cfg.get("left", "1cm"))

row_h = st.text_input("Satır Yüksekliği", cfg.get("row_height", "0.6cm"))
header_h = st.text_input("Başlık Yüksekliği", cfg.get("header_height", "0.7cm"))

st.subheader("Başlık Satırı Ayarları", divider="grey", anchor=False)
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

st.subheader("Kenarlık", divider="grey", anchor=False)
col3_1, col3_2 = st.columns(2)
with col3_1:
    brdcolor = st.color_picker("Kenarlık Rengi", cfg.get("brdcolor", "#D9D9D9"))
    st.text(brdcolor)

with col3_2:
    brdsize = st.number_input("Kenar Kalınlığı", value=extract_number(cfg.get("brdsize", 1)))

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
        "textsize": f"{textsize_h}pt",
        "brdcolor": brdcolor,
        "brdsize": f"{brdsize}pt"
    })

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True)

    st.success("Tablix ayarları kaydedildi")
    time.sleep(2)
    st.rerun()
