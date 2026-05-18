<!-- Generated: 2026-05-18 | Files scanned: 4 | Token estimate: ~300 -->

# Frontend (Streamlit Pages)

## Page Tree

```
Tablix_Generator.py          "SSRS Tablix Generator"  (main page)
pages/
  1_Alan_Cevirileri.py       "Alan Çevirileri"        (field label management)
  2_Format_Ayarlari.py       "Format Ayarları"        (format rules per TypeName)
  3_Tablix_Ayarlari.py       "Tablix Ayarları"        (tablix visual settings)
```

## Main Page Layout (`Tablix_Generator.py`)

```
Sidebar: language selector (TR/EN)

col1 (left)                       col2 (right)
─────────────────────────────     ─────────────────────────────
Fields XML text area              Generated Tablix XML
Suffix input                      st.code block (height 485)
"Tablix Oluştur" button           Download button
```

Generation triggers reactively when `fields_xml.strip()` is truthy (not on button click).

## Settings Pages

| Page | Reads | Writes | Key widgets |
|---|---|---|---|
| 1_Alan_Cevirileri.py | labels.yaml + labels_custom.yaml | labels_custom.yaml | st.data_editor, bulk text input |
| 2_Format_Ayarlari.py | formats.yaml | formats.yaml | type selector, data_editor for overrides |
| 3_Tablix_Ayarlari.py | tablix.yaml | tablix.yaml | text inputs, st.color_picker, st.number_input |

## State Management
No `st.session_state` — all state is persisted in YAML files. Pages reload config from disk on each render.
