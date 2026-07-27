# core/auto_translate.py
"""Çevirisi bulunmayan alanlar için otomatik çeviri önerisi üretir.

CamelCase/PascalCase alan adları önce kelimelere bölünür, ardından
deep-translator'ın (Google) ücretsiz endpoint'i ile hedef dile çevrilir.
Ağ hatası ya da kütüphane eksikliğinde alan adı aynen döndürülür.
"""
import re

# Streamlit varsa çeviri sonuçlarını cache'lemek için kullanılır.
try:
    import streamlit as st
    _cache = st.cache_data(show_spinner=False)
except Exception:  # streamlit dışı bağlamda da çalışsın
    def _cache(func):
        return func

# deep-translator'ın diline kod eşlemesi
_LANG_MAP = {"TR": "tr", "EN": "en"}

_SPLIT_RE = re.compile(
    r".+?(?:(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|[_\s]+|$)"
)


def split_camel_case(name):
    """'SalesChannelCode' -> 'Sales Channel Code'."""
    parts = [p.strip("_ ") for p in _SPLIT_RE.findall(name)]
    parts = [p for p in parts if p]
    return " ".join(parts)


@_cache
def suggest_label(name, lang="TR"):
    """Alan adı için çeviri önerisi döndürür; başarısızsa boş string."""
    target = _LANG_MAP.get(lang)
    if not target:
        return ""

    text = split_camel_case(name)
    try:
        from deep_translator import GoogleTranslator
        result = GoogleTranslator(source="en", target=target).translate(text)
        return (result or "").strip()
    except Exception:
        # İnternet yok / kütüphane yok / rate-limit -> öneri veremiyoruz
        return ""
