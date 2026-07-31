import streamlit as st
import xml.dom.minidom
import xml.etree.ElementTree as ET

from core.fields_parser import parse_fields
from core.tablix_builder import create_tablix
from core.label_provider import has_label
from core.auto_translate import suggest_labels
from core.tablix_config import load_tablix_config

st.set_page_config(
    page_title="Tablix Generator",
    page_icon="📊",
    layout="wide"
)

st.sidebar.title("Tablix Generator")
selected_lang = st.sidebar.selectbox(
    "Oluşacak Tablix Başlık Dili",
    options=["TR", "EN"],
    index=0  # default TR
)

st.title("SSRS Tablix Generator")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Fields XML", anchor=False,
                 help="SSRS için oluşturulmuş datasete ait Fields bloğu buraya yapıştırılarak Tablix Oluştur Butonuna basılacaktır.")
    fields_xml = st.text_area(
        label="Fields XML",
        height=400,
        placeholder="<Fields>...</Fields>",
        label_visibility="collapsed"
    )
    dataset_name = st.text_input(
        "DataSet Adı",
        value=load_tablix_config()["dataset_name"],
        help="Tablix Ayarları sayfasındaki değer varsayılan olarak gelir; burada değiştirilirse "
             "oluşturulan Tablix'te yeni değer kullanılır."
    )
    suffix = st.text_input(
        "Suffix",
        value="10",
        help="Aynı rapora birden fazla tablix eklerken isim çakışmasını önlemek için kullanılır."
    )

    generate = st.button("Tablix Oluştur", type="primary", icon=":material/play_arrow:")
    if generate and fields_xml.strip():
        st.session_state["last_fields_xml"] = fields_xml
        st.session_state["last_suffix"]     = suffix
        st.session_state["last_lang"]       = selected_lang
        st.session_state["last_dataset"]    = dataset_name

with col2:
    st.subheader("Oluşturulan Tablix XML", anchor=False)

    cached_xml  = st.session_state.get("last_fields_xml", "")
    cached_sfx  = st.session_state.get("last_suffix", suffix)
    cached_lang = st.session_state.get("last_lang", selected_lang)
    cached_ds   = st.session_state.get("last_dataset", dataset_name)

    if cached_xml.strip():
        try:
            fields = parse_fields(cached_xml)
            tablix = create_tablix(fields, cached_sfx, lang=cached_lang,
                                   dataset_name=cached_ds)

            raw = ET.tostring(tablix, encoding="utf-8")
            pretty = xml.dom.minidom.parseString(raw).toprettyxml(indent="  ")
            final_xml = "\n".join(pretty.splitlines()[1:])

            st.code(final_xml, language="xml", height=485)

            st.download_button(
                "XML’i İndir",
                final_xml,
                file_name="tablix.xml"
            )

            missing = [name for name, _ in fields if not has_label(name, cached_lang)]
            if missing:
                st.warning(
                    f"Aşağıdaki kolonların {cached_lang} çevirisi bulunamadı, "
                    f"başlık olarak alan adı kullanıldı:",
                    icon=":material/translate:"
                )
                with st.spinner("Çeviri önerileri getiriliyor…"):
                    suggestions = suggest_labels(tuple(missing), cached_lang)
                missing_text = "\n".join(
                    f"{name}={suggestions.get(name, '')}" for name in missing
                )
                st.code(missing_text, language="text")
                st.caption(
                    "Öneriler otomatik çeviridir; listeyi kopyalayıp gerekirse "
                    "düzelterek **Alan Çevirileri** sayfasından ekleyebilirsiniz."
                )
        except ET.ParseError as e:
            st.error(f"Geçersiz Fields XML: {e}", icon=":material/block:")
    else:
        st.info("Lütfen önce Fields XML alanını doldurun.", icon=":material/chat_info:")
