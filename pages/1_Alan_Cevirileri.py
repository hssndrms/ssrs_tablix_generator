import streamlit as st
import yaml
from pathlib import Path
import pandas as pd
import time

# ------------------ PATHS ------------------
BASE_PATH = Path(__file__).parent.parent
DEFAULT_PATH = BASE_PATH / "config" / "labels.yaml"
CUSTOM_PATH = BASE_PATH / "config" / "labels_custom.yaml"

st.set_page_config(layout="centered")
st.title("Alan Çevirileri", anchor=False)


# ------------------ HELPERS ------------------
def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def normalize_lang_dict(d: dict, lang: str) -> dict:
    """
    Garantiler:
    - d dict olur
    - d[lang] dict olur
    """
    d = d or {}
    if lang not in d or d[lang] is None:
        d[lang] = {}
    return d


# ------------------ LOAD YAML ------------------
default_labels = load_yaml(DEFAULT_PATH)
custom_labels = load_yaml(CUSTOM_PATH)

langs = sorted(set(default_labels.keys()) | set(custom_labels.keys()))
if not langs:
    langs = ["TR"]

lang = st.selectbox(
    "Dil",
    langs,
    index=langs.index("TR") if "TR" in langs else 0
)

# normalize
default_labels = normalize_lang_dict(default_labels, lang)
custom_labels = normalize_lang_dict(custom_labels, lang)

# ------------------ MERGE (custom overrides default) ------------------
merged = dict(default_labels[lang])
merged.update(custom_labels[lang])  # custom her zaman kazanır

# ------------------ TABLE DATA ------------------
rows = []
for field, label in sorted(merged.items()):
    is_custom = field in custom_labels[lang]
    rows.append({
        "Alan": field,
        "Etiket": label,
        "Kaynak": "🛠️ Custom" if is_custom else "📦 Default"
    })

df = pd.DataFrame(rows)

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    width="stretch",
    column_config={
        "Kaynak": st.column_config.TextColumn(disabled=True),
    }
)

# ------------------ BULK INPUT ------------------
st.subheader(":material/add: Toplu Alan Ekle (Custom)", anchor=False)

# Kaydet sonrası metin kutusunu temizle (widget oluşturulmadan önce)
if st.session_state.pop("clear_bulk", False):
    st.session_state["bulk_input"] = ""

bulk_input = st.text_area(
    "Her satır: FieldName=Label",
    height=150,
    placeholder="StoreCode=Mağaza Kodu\nStoreDescription=Mağaza Adı",
    key="bulk_input"
)

# ------------------ SAVE ------------------
if st.button("Kaydet", type="secondary", icon=":material/save:"):
    # Custom sözlüğü tablodan SIFIRDAN kur -> silinen satırlar da çıkar
    new_custom = {}

    # 1️⃣ data_editor'daki mevcut satırlar
    for _, row in edited_df.iterrows():
        field = str(row["Alan"]).strip()
        label = str(row["Etiket"]).strip()

        if not field or not label:
            continue

        # default ile aynıysa custom'a gerek yok
        if default_labels[lang].get(field) == label:
            continue

        new_custom[field] = label

    # 2️⃣ bulk input (HER ZAMAN custom)
    if bulk_input.strip():
        for line in bulk_input.splitlines():
            if "=" in line:
                field, label = line.split("=", 1)
                field, label = field.strip(), label.strip()
                if field and label:
                    new_custom[field] = label

    # 3️⃣ ilgili dili güncelle / boşsa temizle
    if new_custom:
        custom_labels[lang] = new_custom
    else:
        custom_labels.pop(lang, None)

    # 4️⃣ YAML yaz
    with open(CUSTOM_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(custom_labels, f, allow_unicode=True)

    st.session_state["clear_bulk"] = True
    st.success("Çeviriler kaydedildi")
    time.sleep(1.2)
    st.rerun()
