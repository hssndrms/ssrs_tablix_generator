<!-- Generated: 2026-05-18 | Files scanned: 4 | Token estimate: ~350 -->

# Data (Config Schemas)

No database. All state is stored in YAML files under `config/`.

## config/labels.yaml — Default translations

```yaml
TR:
  FieldName: "Türkçe Etiket"
  Amount: "Tutar"
  # ~45 entries
EN:
  FieldName: "English Label"
  Amount: "Amount"
```

## config/labels_custom.yaml — User overrides

Same schema as labels.yaml. Merged at runtime: custom values win over defaults.
Currently 3 entries: Balance, Credit, Debit.

## config/formats.yaml — Format rules by TypeName

```yaml
System.Decimal:
  format: N2
  width: 25mm
  align: Right
  overrides:
    exchangerate:          # substring match on lowercased field name
      format: N4
    kur:
      format: N4

System.DateTime:
  format: dd/MM/yyyy
  width: 20mm
  align: Left

System.String:
  width: 25mm
  align: Left
  overrides:
    description:
      width: 75mm
    storecode:
      width: 15mm
```

Supported TypeNames: System.Boolean, Byte, Char, DateTime, Decimal, Double, Guid, Int16, Int32, Int64, Object, SByte, Single, String.

## config/tablix.yaml — Visual settings

```yaml
dataset_name: Main
tablix_name:  Tablix1
header_height: 6mm
row_height:    6mm
top:  17mm
left: 0mm
textsize: 9pt
bckcolor: '#4682B4'   # header background
txtcolor: '#ffffff'   # header text
brdcolor: '#D9D9D9'   # border
brdsize:  1pt
zindex:   1
width_per_column_default: 25mm
```
