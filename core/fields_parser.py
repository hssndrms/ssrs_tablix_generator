import xml.etree.ElementTree as ET
import re

NS_RD_URI = "http://schemas.microsoft.com/SQLServer/reporting/reportdesigner"
NS_RD = "{%s}" % NS_RD_URI


def add_rd_namespace_if_missing(xml_str: str) -> str:
    # Eğer rd namespace yoksa, Fields tag'ine ekle
    if "xmlns:rd" not in xml_str:
        xml_str = re.sub(
            r"<Fields(\s*>)",
            f'<Fields xmlns:rd="{NS_RD_URI}"\\1',
            xml_str,
            count=1
        )
    return xml_str


def parse_fields(fields_xml: str):
    fields_xml = add_rd_namespace_if_missing(fields_xml)

    root = ET.fromstring(fields_xml)
    fields = []

    for field in root.findall("Field"):
        name = field.get("Name")
        type_name = field.find(f"{NS_RD}TypeName").text
        fields.append((name, type_name))

    return fields
