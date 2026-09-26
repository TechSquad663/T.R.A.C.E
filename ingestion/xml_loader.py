"""XML file loader for Bitcoin transaction metadata."""
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Union

logger = logging.getLogger("TRACE.XMLLoader")


def parse_xml_node(elem: ET.Element) -> Dict[str, Any]:
    """Recursively or flattened parse an XML transaction element."""
    record: Dict[str, Any] = {}
    
    # Extract element attributes if any
    for k, v in elem.attrib.items():
        record[k] = v

    # Extract child elements
    for child in elem:
        tag = child.tag.lower()
        # Check if this child has subchildren (e.g. <input_addresses><address>...</address></input_addresses>)
        if len(child) > 0:
            sub_items = []
            for sub in child:
                text = (sub.text or "").strip()
                if text:
                    sub_items.append(text)
                elif sub.attrib:
                    sub_items.append(sub.attrib.get("value") or sub.attrib.get("address") or sub.attrib.get("amount") or "")
            record[tag] = sub_items
        else:
            text = (child.text or "").strip()
            record[tag] = text

    return record


def load_xml_data(
    file_path: Union[str, Path],
    max_rows: Optional[int] = None,
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Load XML file into list of dictionaries.
    Returns (records, error_string_if_any).
    """
    path = Path(file_path)
    if not path.exists():
        return [], f"File not found: {path}"
    if path.stat().st_size == 0:
        return [], "File is empty (0 bytes)"

    records: List[Dict[str, Any]] = []

    try:
        tree = ET.parse(str(path))
        root = tree.getroot()

        # Target repeated children tags
        target_tags = ["transaction", "tx", "record", "item", "row", "observation", "entry"]
        candidate_nodes: List[ET.Element] = []

        for tag in target_tags:
            found = root.findall(f".//{tag}")
            if found:
                candidate_nodes = found
                break

        # If not found by specific tag, take direct children of root
        if not candidate_nodes:
            candidate_nodes = list(root)

        for i, elem in enumerate(candidate_nodes):
            if max_rows and i >= max_rows:
                break
            record = parse_xml_node(elem)
            if record:
                records.append(record)

        if not records:
            return [], "No transaction records found in XML structure"

        return records, None

    except ET.ParseError as pe:
        logger.error(f"Malformed XML in {path}: {pe}")
        return [], f"Malformed XML: {pe}"
    except Exception as e:
        logger.error(f"Error reading XML {path}: {e}", exc_info=True)
        return [], f"Failed to parse XML: {str(e)}"
