<!-- Generated: 2026-05-18 | Files scanned: 2 | Token estimate: ~120 -->

# Dependencies

## Python Packages (requirements.txt)

| Package | Purpose |
|---|---|
| streamlit | Web UI framework — pages, widgets, layout |
| pyyaml | YAML config file read/write |

## Stdlib (no extra install)

| Module | Used in |
|---|---|
| xml.etree.ElementTree | fields_parser.py, tablix_builder.py, Tablix_Generator.py |
| xml.dom.minidom | Tablix_Generator.py — pretty-print output XML |
| pathlib.Path | All core/ modules — resolve config file paths |
| re | fields_parser.py — inject rd: namespace |

## External Systems

| System | Role |
|---|---|
| SSRS / RDL | Target consumer of generated XML — no direct integration |

No database, no API calls, no auth, no cloud services.
