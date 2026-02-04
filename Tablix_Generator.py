import streamlit as st
import xml.dom.minidom
import xml.etree.ElementTree as ET

from core.fields_parser import parse_fields
from core.tablix_builder import create_tablix

st.set_page_config(
    page_title="Tablix Generator",
    page_icon="📊",
    layout="wide"
)

st.sidebar.title("Tablix Generator")
st.sidebar.markdown("SSRS Tablix Üretici")

selected_lang = st.sidebar.selectbox(
    "Oluşacak Tablix Başlık Dili",
    options=["TR", "EN"],
    index=0  # default TR
)

st.set_page_config(layout="wide")
st.title("SSRS Tablix Generator")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Fields XML",
                 help="SSRS için oluşturulmuş datasete ait Fields bloğu buraya yapıştırılarak Tablix Oluştur Butonuna basılacaktır.")
    fields_xml = st.text_area(
        label="Fields XML",
        height=400,
        placeholder="<Fields>...</Fields>",
        label_visibility="collapsed"
    )
    suffix = st.text_input(
        "Suffix",
        value="10",
        help="Aynı rapora birden fazla tablix eklerken isim çakışmasını önlemek için kullanılır."
    )

    st.button("Tablix Oluştur")

with col2:
    st.subheader("Oluşturulan Tablix XML")

    if fields_xml.strip():
        try:
            fields = parse_fields(fields_xml)
            tablix = create_tablix(fields, suffix, lang=selected_lang)

            raw = ET.tostring(tablix, encoding="utf-8")
            pretty = xml.dom.minidom.parseString(raw).toprettyxml(indent="  ")
            final_xml = "\n".join(pretty.splitlines()[1:])

            st.code(final_xml, language="xml", height=485)

            st.download_button(
                "XML’i İndir",
                final_xml,
                file_name="tablix.xml"
            )
        except ET.ParseError as e:
            st.error(f"Geçersiz Fields XML: {e}", icon=":metarial/block:")
    else:
        st.info("Lütfen önce Fields XML alanını doldurun.", icon=":material/chat_info:")
