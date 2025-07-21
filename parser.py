import xml.etree.ElementTree as ET
import json
import sys

def parse_des_xml(xml_file, json_file):
    
    # Read the XML file
    with open(xml_file, 'r') as f:
        content = f.read()
    
    # Extract just the structure part
    start = content.find('<structure>')
    end = content.find('</structure>') + len('</structure>')
    xml_content = content[start:end]
    
    # Parse XML
    root = ET.fromstring(xml_content)
    
    # Extract variables from definitions
    variables = {}
    for def_elem in root.findall('.//def'):
        name = def_elem.find('name').text.strip()
        value = def_elem.find('val').text.strip()
        variables[name] = value
    
    # Write JSON file
    with open(json_file, 'w') as f:
        json.dump(variables, f,indent=1)
    print(f"Converted {xml_file} -> {json_file}")

xml_file = sys.argv[1]
json_file = sys.argv[2]
parse_des_xml(xml_file, json_file)
