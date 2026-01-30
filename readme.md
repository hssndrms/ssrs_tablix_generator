# Tablix Generator 🎯

Bu proje, **Microsoft SSRS (RDL)** raporları için **Tablix XML** üretimini otomatikleştiren,
**Streamlit tabanlı** bir yardımcı araçtır.

Amaç; elle tablix yazma, kopyala-yapıştır ve designer hatalarıyla uğraşmadan,
sadece **Fields XML** vererek **standart, tutarlı ve özelleştirilebilir tablix** üretmektir.

---

## 🚀 Ne İşe Yarar?

- SSRS `Fields` tanımından otomatik **Tablix** oluşturur
- Header ve data textbox’larını üretir
- **Alan adlarını çok dilli başlıklara** dönüştürür
- **TypeName ve isim bazlı formatlama** uygular
- Kolon genişliklerini ve formatları **merkezi ayar dosyalarından** yönetir
- Aynı rapora birden fazla tablix eklerken **isim çakışmalarını önler**
- Designer’da açılabilir, hatasız XML üretir

---

## 🧱 Üretilen Yapılar

- `Tablix`
- `TablixColumns`
- `TablixRows`
- `TablixRowHierarchy`
- `TablixColumnHierarchy`
- `Header / Detail Textbox`
- `Dataset`, `Top`, `Left`, `ZIndex` ayarları

> ⚠️ SSRS Designer için **zorunlu tüm hiyerarşi elemanları** otomatik eklenir.

---

## 🖥️ Arayüz Özellikleri (Streamlit)

### 📄 Tablix Generator
- Fields XML girilir
- Suffix belirlenir
- Dil seçilir
- Tek tıkla Tablix XML üretilir
- XML kopyalanabilir

### 🌍 Alan Çevirileri
- Alan isimleri için çok dilli başlıklar tanımlanır
- Toplu ekleme desteklenir
- YAML dosyasına kaydedilir
- Anında etkili olur

### 🎨 Format Ayarları
- TypeName bazlı formatlar
- Kolon genişlikleri
- İsim bazlı override’lar (`Amount`, `Rate`, `Date` vb.)

### ⚙️ Tablix Ayarları
- Dataset adı
- Tablix adı
- Konum (Top / Left)
- Satır yükseklikleri

---

## 📂 Proje Yapısı

```text
tablix_generator/
│
├─ app.py                     # Ana Streamlit giriş dosyası
│
├─ pages/
│   ├─ Alan_Cevirileri.py
│   ├─ Format_Ayarlari.py
│   └─ Tablix_Ayarlari.py
│
├─ core/
│   ├─ tablix_builder.py      # Tablix XML üretimi
│   ├─ fields_parser.py       # Fields XML parse işlemleri
│   ├─ label_provider.py      # Çok dilli alan adları
│   ├─ format_config.py       # Format çözümleyici
│   └─ tablix_config.py       # Tablix ayar loader
│
├─ config/
│   ├─ labels.yaml            # Alan çevirileri
│   ├─ formats.yaml           # Format & width kuralları
│   └─ tablix.yaml            # Tablix genel ayarları
│
├─ requirements.txt
└─ README.md
```
## Kurulum
``` bash
pip install -r requirements.txt
``` 
## Çalıştırma
``` bash
streamlit run app.py
```