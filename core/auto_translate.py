# core/auto_translate.py
"""Çevirisi bulunmayan alanlar için otomatik çeviri önerisi üretir.

Strateji (hızdan yavaşa):
1. Disk cache — daha önce üretilmiş öneriler.
2. Çevrimdışı sözlük — mevcut labels.yaml çevirilerinden türetilen
   kelime düzeyinde EN->TR eşlemesi (ağ gerektirmez, anında sonuç).
3. Google (deep-translator) — yalnızca endpoint'e erişilebiliyorsa.
   Erişim kontrolü kısa timeout'lu tek bir prob ile yapılır; ağ kapalıysa
   hiç istek atılmaz, böylece alan başına dakikalarca bekleme olmaz.

Ağ açıksa alanlar tek tek değil tek istekte toplu çevrilir; toplu istek
güvenilir dönmezse paralel tekil isteklere düşülür.
"""
import json
import os
import re
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

from core.label_provider import _load, LABEL_PATH, LABEL_CUSTOM_PATH

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

# Google'a erişilebilir mi kontrolü için azami bekleme (saniye)
_PROBE_TIMEOUT = 3
# Tek istekte gönderilecek azami alan sayısı
_BATCH_SIZE = 40
# Paralel fallback'te eşzamanlı istek sayısı
_MAX_WORKERS = 8
# Çeviri isteklerinin tamamı için azami süre (saniye)
_TRANSLATE_DEADLINE = 20

_CACHE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config", ".translate_cache.json",
)

# Sık kullanılan rapor/ERP terimleri için çekirdek sözlük. labels.yaml'dan
# türetilen eşlemeler bunun üzerine yazılır.
_SEED_TR = {
    "amount": "Tutarı", "base": "Kaynak", "card": "Kartı", "code": "Kodu",
    "company": "Şirketi", "credit": "Kredi", "currency": "Para Birimi",
    "customer": "Müşteri", "date": "Tarihi", "description": "Açıklaması",
    "discount": "İskonto", "doc": "Belge", "document": "Belge",
    "error": "Hata", "exchange": "Kur", "file": "Dosya", "first": "İlk",
    "id": "ID", "import": "İthalat", "invoice": "Fatura", "is": "",
    "item": "Ürün", "last": "Son", "line": "Satır", "message": "Mesajı",
    "name": "Adı", "net": "Net", "number": "Numarası", "order": "Sipariş",
    "payment": "Ödeme", "price": "Fiyatı", "process": "Süreç",
    "product": "Ürün", "quantity": "Miktarı", "rate": "Oranı",
    "reason": "Nedeni", "ref": "Ref.", "return": "İade", "row": "Satır",
    "sales": "Satış", "status": "Durumu", "store": "Mağaza",
    "success": "Başarılı", "tax": "Vergi", "total": "Toplam",
    "type": "Tipi", "unit": "Birim", "user": "Kullanıcı",
    "vendor": "Tedarikçi", "warehouse": "Depo",
}

_lock = threading.Lock()
_disk_cache = None
_glossary = None
_network_ok = None


def split_camel_case(name):
    """'SalesChannelCode' -> 'Sales Channel Code'."""
    parts = [p.strip("_ ") for p in _SPLIT_RE.findall(name)]
    parts = [p for p in parts if p]
    return " ".join(parts)


# --------------------------------------------------------------------------
# Cache
# --------------------------------------------------------------------------
def _load_disk_cache():
    """Diskteki çeviri cache'ini bir kez okuyup bellekte tutar."""
    global _disk_cache
    if _disk_cache is None:
        try:
            with open(_CACHE_PATH, "r", encoding="utf-8") as f:
                _disk_cache = json.load(f)
        except Exception:
            _disk_cache = {}
    return _disk_cache


def _save_disk_cache():
    """Cache'i diske yazar; hata olursa sessizce geçer."""
    try:
        with open(_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(_disk_cache, f, ensure_ascii=False, indent=0)
    except Exception:
        pass


# --------------------------------------------------------------------------
# Çevrimdışı sözlük
# --------------------------------------------------------------------------
def _build_glossary():
    """labels.yaml + labels_custom.yaml'dan kelime düzeyinde EN->TR sözlük.

    'InvoiceNumber: Fatura Numarası' kaydından Invoice->Fatura,
    Number->Numarası eşlemesi çıkarılır. Yalnızca kelime sayıları eşleşen
    kayıtlar kullanılır, aksi halde hizalama yanlış olur.
    """
    glossary = dict(_SEED_TR)
    labels = {**_load(LABEL_PATH).get("TR", {}),
              **_load(LABEL_CUSTOM_PATH).get("TR", {})}
    for field, label in labels.items():
        source = split_camel_case(str(field)).split()
        target = str(label).split()
        if len(source) == len(target) and len(source) > 1:
            for en, tr in zip(source, target):
                glossary[en.lower()] = tr
    return glossary


def _offline_suggest(name):
    """Sözlükten kelime kelime çeviri üretir; hiçbiri bilinmiyorsa boş."""
    global _glossary
    if _glossary is None:
        _glossary = _build_glossary()

    words = split_camel_case(name).split()
    out, hit = [], False
    for word in words:
        tr = _glossary.get(word.lower())
        if tr is None:
            out.append(word)
        else:
            hit = True
            if tr:
                out.append(tr)
    return " ".join(out) if hit else ""


# --------------------------------------------------------------------------
# Çevrimiçi çeviri
# --------------------------------------------------------------------------
def _check_network():
    """Google endpoint'ine kısa timeout'lu tek prob; sonuç önbelleklenir.

    requests kullanılmıyor: host birden çok IP'ye çözülüyor ve her biri ayrı
    ayrı denendiği için toplam bekleme timeout değerinin katlarına çıkıyor.
    Tek bir adrese soket bağlantısı denenerek süre garanti altına alınır.
    """
    global _network_ok
    if _network_ok is None:
        _network_ok = False
        try:
            infos = socket.getaddrinfo(
                "translate.google.com", 443, proto=socket.IPPROTO_TCP)
            family, socktype, proto, _, addr = infos[0]
            sock = socket.socket(family, socktype, proto)
            sock.settimeout(_PROBE_TIMEOUT)
            try:
                sock.connect(addr)
                _network_ok = True
            finally:
                sock.close()
        except Exception:
            _network_ok = False
    return _network_ok


def _translate_batch(texts, target):
    """Birden çok metni tek istekte çevirir; satır sayısı uymazsa None."""
    from deep_translator import GoogleTranslator

    joined = "\n".join(texts)
    result = GoogleTranslator(source="en", target=target).translate(joined)
    lines = [line.strip() for line in (result or "").splitlines() if line.strip()]
    if len(lines) != len(texts):
        # Google satırları birleştirmiş/bölmüş olabilir -> güvenilmez
        return None
    return lines


def _translate_parallel(texts, target):
    """Toplu istek başarısızsa: tekil çevirileri eşzamanlı yürütür."""
    from deep_translator import GoogleTranslator

    def one(text):
        try:
            return (GoogleTranslator(
                source="en", target=target).translate(text) or "").strip()
        except Exception:
            return ""

    workers = min(_MAX_WORKERS, len(texts)) or 1
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(one, texts))


def _translate_online(names, target):
    """Ağ üzerinden çeviri; deadline aşılırsa boş sözlük döner."""
    result = {}

    def work():
        for i in range(0, len(names), _BATCH_SIZE):
            chunk = names[i:i + _BATCH_SIZE]
            texts = [split_camel_case(n) for n in chunk]
            try:
                lines = _translate_batch(texts, target)
            except Exception:
                lines = None
            if lines is None:
                lines = _translate_parallel(texts, target)
            result.update(dict(zip(chunk, lines)))

    # deep-translator timeout parametresi almıyor; takılan istek UI'ı
    # kilitlemesin diye daemon thread'i süre dolunca terk ediyoruz.
    worker = threading.Thread(target=work, daemon=True)
    worker.start()
    worker.join(_TRANSLATE_DEADLINE)
    return dict(result)


# --------------------------------------------------------------------------
# Genel API
# --------------------------------------------------------------------------
@_cache
def suggest_labels(names, lang="TR"):
    """Alan adları için {alan: öneri} sözlüğü döndürür.

    `names` hashable olmalıdır (tuple), çünkü sonuç cache'lenir.
    """
    target = _LANG_MAP.get(lang)
    if not target or not names:
        return {}

    cache = _load_disk_cache()
    out, pending = {}, []
    for name in names:
        key = f"{lang}:{name}"
        if key in cache:
            out[name] = cache[key]
        elif name not in pending:
            pending.append(name)

    if not pending:
        return out

    online = {}
    if _check_network():
        online = _translate_online(pending, target)

    fresh = {}
    for name in pending:
        value = (online.get(name) or "").strip()
        if not value:
            # TR'de sözlükten, EN'de alan adının okunabilir hali öneri olur.
            value = (_offline_suggest(name) if lang == "TR"
                     else split_camel_case(name))
        fresh[name] = value

    with _lock:
        for name, value in fresh.items():
            out[name] = value
            if value and online.get(name):
                # Yalnızca gerçek çevirileri kalıcı sakla; sözlük önerisi
                # labels.yaml büyüdükçe kendiliğinden iyileşsin.
                cache[f"{lang}:{name}"] = value
        _save_disk_cache()

    return out


def suggest_label(name, lang="TR"):
    """Tek alan için çeviri önerisi döndürür; başarısızsa boş string."""
    return suggest_labels((name,), lang).get(name, "")
