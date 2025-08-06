import json
import sys
import os
import re
import xml.etree.ElementTree as ET


class Parser():
    def __init__(self, sourceDir="structs", outDir="parsed"):
        self.sourceDir = sourceDir
        self.outDir = outDir
    
    def convert(self, filename):
        variables = self.parse(filename)
        jsonFile = os.path.join(self.outDir, filename[:-4] + ".json")
        with open(jsonFile, 'w') as f:
            json.dump(variables, f, indent=1)
    
    def getDependencies(self, filename):
        filepath = os.path.join(self.sourceDir, filename)
        try:
            with open(filepath, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return set()

        # Extract content between <structure> tags
        start = content.find("<structure>")
        end = content.find("</structure>")
    
        if start == -1 or end == -1:
            return set()
    
        structure_content = content[start + len("<structure>"):end]
    
        # Remove XML tags from structure content
        text_content = re.sub(r'<[^>]+>', ' ', structure_content)
        text_content = re.sub(r'\s+', ' ', text_content)
    
        refs = set()
        pattern = r'(?<![0-9.])\b([a-zA-Z_][a-zA-Z0-9_-]*)\.[\w\[\]()\/,-]+'
    
        for match in re.finditer(pattern, text_content):
            identifier = match.group(1)
            # Skip system.* references regardless of case
            if identifier.lower() == "system":
                continue
            refs.add(identifier)
        
        return refs    
    
    def parseDef(self, element):
        out = {}
        calls = []
        
        for child in element:
            if child.tag == "def":
                name_elem = child.find("name")
                val_elem = child.find("val")
                if name_elem is not None and val_elem is not None:
                    name = name_elem.text.strip() if name_elem.text else ""
                    value = val_elem.text.strip() if val_elem.text else ""
                    out[name] = value
                    
            elif child.tag == "call":
                call_name = child.text.strip() if child.text else ""
                if call_name:
                    calls.append(call_name)
                    
            elif child.tag == "block":
                name_element = child.find("name")
                if name_element is not None:
                    name = name_element.text.strip() if name_element.text else ""
                    value = self.parseDef(child)
                    out[name] = value
        
        # Add calls to output if any were found
        if calls:
            out["CALLS"] = calls
                    
        return out

    def parse(self, filename):
        filepath = os.path.join(self.sourceDir, filename)
        try:
            with open(filepath, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return {}

        # Extract content between <structure> tags
        start = content.find("<structure>")
        end = content.find("</structure>")
        if start == -1 or end == -1:
            print(f"No <structure> tags found in {filepath}")
            return {}
            
        structure_content = content[start:end+len("</structure>")]
        
        def escape_ampersands(s):
            # Replace & not followed by one of the valid XML entities
            return re.sub(r'&(?!amp;|lt;|gt;|apos;|quot;|#\d+;|#x[0-9A-Fa-f]+;)', '&amp;', s)
        
        structure_content = escape_ampersands(structure_content)
        
        try:
            root = ET.fromstring(structure_content)
        except ET.ParseError as e:
            print(f"XML Parse Error in {filepath}: {e}")
            print("Content that failed to parse:")
            print(structure_content)
            return {}

        # Parse variables section
        variables = {}
        variables_section = root.find("variables")
        if variables_section is not None:
            for var in variables_section:
                if var.tag in ["var", "parm"]:
                    name_elem = var.find("name")
                    val_elem = var.find("val")
                    if name_elem is not None:
                        name = name_elem.text.strip() if name_elem.text else ""
                        if val_elem is not None:
                            value = val_elem.text.strip() if val_elem.text else ""
                            variables[name] = {"type": var.tag, "value": value}
                        else:
                            variables[name] = {"type": var.tag, "value": None}

        # Parse functions section
        functions = {}
        functions_section = root.find("functions")
        if functions_section is not None:
            for func in functions_section:
                if func.tag == "curve":
                    name_elem = func.find("name")
                    if name_elem is not None:
                        name = name_elem.text.strip() if name_elem.text else ""
                        points = []
                        for point in func.findall("point"):
                            x_elem = point.find("x")
                            y_elem = point.find("y")
                            slope_elem = point.find("slope")
                            if x_elem is not None and y_elem is not None and slope_elem is not None:
                                x = x_elem.text.strip() if x_elem.text else ""
                                y = y_elem.text.strip() if y_elem.text else ""
                                slope = slope_elem.text.strip() if slope_elem.text else ""
                                points.append(f"({x},{y},{slope})")
                        functions[name] = f"<CURVE({','.join(points)})>"

        # Parse definitions section
        definitions = {}
        definitions_section = root.find("definitions")
        if definitions_section is not None:
            definitions = self.parseDef(definitions_section)

        # Combine all parsed data
        result = {}
        if variables:
            result["variables"] = variables
        if functions:
            result["functions"] = functions
        if definitions:
            result["definitions"] = definitions
            
        return result


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python parser.py sourceDir outDir")
        sys.exit(1)
    sourceDir = sys.argv[1]
    outDir = sys.argv[2]
    parser = Parser()
    parser.sourceDir = sourceDir
    parser.outDir = outDir
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    for filename in os.listdir(sourceDir):
        if filename.endswith(".DES"):
            print(f"Parsing {filename}...")
            parser.convert(filename)