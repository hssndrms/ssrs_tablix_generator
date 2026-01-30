import xml.etree.ElementTree as ET
from core.format_config import resolve_format
from core.label_provider import get_label
from core.tablix_config import load_tablix_config

NS_RD = "{http://schemas.microsoft.com/SQLServer/reporting/reportdesigner}"
ET.register_namespace("rd", NS_RD.strip("{}"))


def create_header_textbox(name, idx, suffix, lang="TR"):
    tb = ET.Element("Textbox", Name=f"hdr{name}{suffix}")
    ET.SubElement(tb, "CanGrow").text = "true"

    paragraphs = ET.SubElement(tb, "Paragraphs")
    paragraph = ET.SubElement(paragraphs, "Paragraph")
    runs = ET.SubElement(paragraph, "TextRuns")
    run = ET.SubElement(runs, "TextRun")

    ET.SubElement(run, "Value").text = get_label(name, lang)

    style = ET.SubElement(run, "Style")
    ET.SubElement(style, "FontFamily").text = "Tahoma"
    ET.SubElement(style, "FontSize").text = "9pt"
    ET.SubElement(style, "FontWeight").text = "Bold"
    ET.SubElement(style, "Color").text = "White"

    ET.SubElement(tb, NS_RD + "DefaultName").text = f"Textbox{10 + idx}"

    style2 = ET.SubElement(tb, "Style")
    ET.SubElement(style2, "BackgroundColor").text = "SteelBlue"

    return tb


def create_data_textbox(name, type_name, idx, suffix):
    cfg = resolve_format(name, type_name)

    tb = ET.Element("Textbox", Name=name + suffix)

    paragraphs = ET.SubElement(tb, "Paragraphs")
    paragraph = ET.SubElement(paragraphs, "Paragraph")
    runs = ET.SubElement(paragraph, "TextRuns")
    run = ET.SubElement(runs, "TextRun")

    ET.SubElement(run, "Value").text = f"=Fields!{name}.Value"

    style = ET.SubElement(run, "Style")
    ET.SubElement(style, "FontFamily").text = "Tahoma"
    ET.SubElement(style, "FontSize").text = "9pt"

    if cfg.get("format"):
        ET.SubElement(style, "Format").text = cfg["format"]

    ET.SubElement(tb, NS_RD + "DefaultName").text = name
    return tb


def create_tablix(fields, suffix="10", lang="TR"):
    tcfg = load_tablix_config()

    tablix = ET.Element("Tablix", Name=tcfg["tablix_name"])
    body = ET.SubElement(tablix, "TablixBody")

    # --- Columns ---
    cols = ET.SubElement(body, "TablixColumns")
    for name, type_name in fields:
        cfg = resolve_format(name, type_name)
        col = ET.SubElement(cols, "TablixColumn")
        ET.SubElement(
            col,
            "Width"
        ).text = cfg.get("width", tcfg["width_per_column_default"])

    # --- Rows ---
    rows = ET.SubElement(body, "TablixRows")

    # Header row
    header = ET.SubElement(rows, "TablixRow")
    ET.SubElement(header, "Height").text = tcfg["header_height"]
    hcells = ET.SubElement(header, "TablixCells")

    for i, (name, _) in enumerate(fields):
        cell = ET.SubElement(hcells, "TablixCell")
        cont = ET.SubElement(cell, "CellContents")
        cont.append(create_header_textbox(name, i, suffix, lang))

    # Data row
    data = ET.SubElement(rows, "TablixRow")
    ET.SubElement(data, "Height").text = tcfg["row_height"]
    dcells = ET.SubElement(data, "TablixCells")

    for i, (name, type_name) in enumerate(fields):
        cell = ET.SubElement(dcells, "TablixCell")
        cont = ET.SubElement(cell, "CellContents")
        cont.append(create_data_textbox(name, type_name, i, suffix))

    # --- Dataset ---
    ET.SubElement(tablix, "DataSetName").text = tcfg["dataset_name"]

    # --- Column Hierarchy (ZORUNLU) ---
    col_hier = ET.SubElement(tablix, "TablixColumnHierarchy")
    col_members = ET.SubElement(col_hier, "TablixMembers")
    for _ in fields:
        ET.SubElement(col_members, "TablixMember")

    # --- Row Hierarchy (ZORUNLU) ---
    row_hier = ET.SubElement(tablix, "TablixRowHierarchy")
    row_members = ET.SubElement(row_hier, "TablixMembers")

    header_member = ET.SubElement(row_members, "TablixMember")
    ET.SubElement(header_member, "KeepWithGroup").text = "After"
    ET.SubElement(header_member, "RepeatOnNewPage").text = "true"

    detail_member = ET.SubElement(row_members, "TablixMember")
    ET.SubElement(detail_member, "Group", Name="Details" + suffix)

    # --- Position ---
    ET.SubElement(tablix, "Top").text = tcfg["top"]
    ET.SubElement(tablix, "Left").text = tcfg["left"]
    ET.SubElement(tablix, "ZIndex").text = str(tcfg.get("zindex", 1))

    return tablix
