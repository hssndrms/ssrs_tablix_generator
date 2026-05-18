# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Tablix Generator** is a Streamlit-based tool that automates Tablix XML generation for Microsoft SSRS (SQL Server Reporting Services) RDL reports. Users paste Fields XML from their SSRS dataset and receive ready-to-use Tablix XML with proper column widths, data formats, and localized headers (Turkish/English).

## Running the App

```bash
pip install -r requirements.txt
streamlit run Tablix_Generator.py
```

No test framework, linter, or build system is configured.

## Architecture

### Data Flow

1. User pastes **Fields XML** + selects suffix & language in `Tablix_Generator.py`
2. `core/fields_parser.py` → `parse_fields()` extracts `(field_name, TypeName)` tuples
3. `core/tablix_builder.py` → `create_tablix()` builds the full Tablix XML element tree
   - Per field: `create_header_textbox()` (calls `get_label()`) + `create_data_textbox()` (calls `resolve_format()`)
4. Output is pretty-printed XML displayed in the UI with a download button

### Module Responsibilities

| Module | Responsibility |
|---|---|
| `Tablix_Generator.py` | Main Streamlit entry point; UI for input/output |
| `core/fields_parser.py` | Parses Fields XML; handles missing `rd:` namespace |
| `core/tablix_builder.py` | Assembles the full Tablix XML tree |
| `core/label_provider.py` | Resolves localized field labels (TR/EN) from YAML |
| `core/format_config.py` | Resolves format/width/alignment by TypeName + field-name overrides |
| `core/tablix_config.py` | Loads general Tablix settings (colors, sizes, position) |
| `pages/1_Alan_Cevirileri.py` | UI for editing field translation labels |
| `pages/2_Format_Ayarlari.py` | UI for editing format rules per TypeName |
| `pages/3_Tablix_Ayarlari.py` | UI for editing general Tablix properties |

### Configuration Files (`config/`)

| File | Purpose |
|---|---|
| `labels.yaml` | Default multi-language field label translations |
| `labels_custom.yaml` | User overrides for labels (takes precedence over defaults) |
| `formats.yaml` | Format/width/alignment rules by `System.*` TypeName, with field-name substring overrides |
| `tablix.yaml` | Tablix positioning, colors, font, border, dataset name |

### Key Design Patterns

- **Config-driven**: All styling, positioning, and formatting comes from YAML — avoid hardcoding values in Python.
- **Override system**: `formats.yaml` has a TypeName-level default and a field-name-based `overrides` list (substring match, case-insensitive). Same pattern used in `labels_custom.yaml` for label overrides.
- **Suffix for collision prevention**: Numeric suffix appended to all textbox/column names so multiple Tablixes can coexist in one SSRS report.
- **SSRS XML namespaces**: The `rd:` namespace (`xmlns:rd="http://schemas.microsoft.com/SQLServer/reporting/reportdesigner"`) must be present on Fields elements; `fields_parser.py` injects it if missing.
