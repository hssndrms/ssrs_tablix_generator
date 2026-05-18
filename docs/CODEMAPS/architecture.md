<!-- Generated: 2026-05-18 | Files scanned: 11 | Token estimate: ~400 -->

# Architecture

## Project Type
Single Streamlit app — no server, no database. Runs locally.

## Data Flow

```
User (browser)
  │
  ├─ Pastes Fields XML + selects suffix & lang
  │
  ▼
Tablix_Generator.py  (entry point)
  │
  ├─ parse_fields(fields_xml)  →  core/fields_parser.py
  │     • injects rd: namespace if missing
  │     • returns: [(field_name, TypeName), ...]
  │
  └─ create_tablix(fields, suffix, lang)  →  core/tablix_builder.py
        │
        ├─ per column: resolve_format(name, type_name)  →  core/format_config.py
        │     reads config/formats.yaml → TypeName default + name-substring overrides
        │
        ├─ per header cell: get_label(name, lang)  →  core/label_provider.py
        │     reads config/labels.yaml (defaults) + config/labels_custom.yaml (overrides)
        │
        └─ load_tablix_config()  →  core/tablix_config.py
              reads config/tablix.yaml → colors, sizes, dataset name, position
        │
        ▼
  ET.Element (Tablix XML tree)
        │
        ▼
  Pretty-printed XML → st.code() + download button
```

## Module Map

```
Tablix_Generator.py          entry point, Streamlit UI
core/
  fields_parser.py           XML parse, namespace injection
  tablix_builder.py          XML assembly (header + data textboxes, hierarchy)
  label_provider.py          TR/EN label lookup
  format_config.py           format/width/align resolution
  tablix_config.py           tablix.yaml loader
pages/
  1_Alan_Cevirileri.py       label editor (writes labels_custom.yaml)
  2_Format_Ayarlari.py       format editor (writes formats.yaml)
  3_Tablix_Ayarlari.py       tablix settings editor (writes tablix.yaml)
config/
  labels.yaml                default TR/EN translations
  labels_custom.yaml         user overrides (highest priority)
  formats.yaml               format rules by System.* TypeName
  tablix.yaml                Tablix position, colors, sizes
```
