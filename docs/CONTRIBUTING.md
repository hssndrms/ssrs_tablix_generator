# Contributing

## Setup

**Prerequisites**: Python 3.8+

```bash
pip install -r requirements.txt
streamlit run Tablix_Generator.py
```

The app opens at `http://localhost:8501`.

<!-- AUTO-GENERATED: commands-table -->
## Commands

| Command | Description |
|---|---|
| `streamlit run Tablix_Generator.py` | Start the app |
| `pip install -r requirements.txt` | Install dependencies (streamlit, pyyaml) |
<!-- END AUTO-GENERATED -->

## Extending the App

### Add a field translation
Edit `config/labels_custom.yaml` directly, or use the **Alan Çevirileri** settings page. Custom values override defaults from `labels.yaml`.

```yaml
TR:
  MyNewField: "Yeni Alan Adı"
EN:
  MyNewField: "New Field Name"
```

### Add a format rule for a new TypeName
Edit `config/formats.yaml`. Each entry is keyed by the full `System.*` TypeName:

```yaml
System.TimeSpan:
  format: hh:mm
  width: 20mm
  align: Left
```

### Add a field-name-based override
Under an existing TypeName entry, add to `overrides`. Keys are lowercased substrings of the field name:

```yaml
System.Decimal:
  overrides:
    rate:
      format: N4
      width: 20mm
```

### Add a Streamlit settings page
Create `pages/N_PageName.py`. Streamlit picks it up automatically. Follow the pattern in existing pages: read the relevant YAML, display an editor widget, write back on save.

## Architecture

See [`docs/CODEMAPS/architecture.md`](CODEMAPS/architecture.md) for the full data flow.
