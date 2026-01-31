import streamlit as st
import yaml
from pathlib import Path
import pandas as pd

LABEL_PATH = Path(__file__).parent.parent / "config" / "labels.yaml"

st.title("Alan Çevirileri")

with open(LABEL_PATH, "r", encoding="utf-8") as f:
    labels = yaml.safe_load(f)

langs = list(labels.keys())

lang = st.selectbox(
    "Dil",
    langs,
    index=langs.index("TR") if "TR" in langs else 0
)


data = [
    {"Field": k, "Label": v}
    for k, v in labels.get(lang, {}).items()
]

df = pd.DataFrame(data)

edited_df = st.data_editor(df, num_rows="dynamic")
st.markdown("### Toplu Alan Ekle")

bulk_input = st.text_area(
    "Her satır: FieldName=Label",
    height=150,
    placeholder="StoreCode=Mağaza Kodu\nStoreDescription=Mağaza Adı"
)

if bulk_input.strip():
    for line in bulk_input.splitlines():
        if "=" in line:
            field, label = line.split("=", 1)
            labels.setdefault(lang, {})[field.strip()] = label.strip()


if st.button("Kaydet"):
    # 1️⃣ Önce data_editor içeriğini al
    labels[lang] = dict(zip(edited_df["Field"], edited_df["Label"]))

    # 2️⃣ Sonra toplu eklemeyi merge et
    if bulk_input.strip():
        for line in bulk_input.splitlines():
            if "=" in line:
                field, label = line.split("=", 1)
                labels[lang][field.strip()] = label.strip()

    # 3️⃣ YAML’e yaz
    with open(LABEL_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(labels, f, allow_unicode=True)

    st.success("Çeviriler kaydedildi")
    time.sleep(2)
    st.rerun()


