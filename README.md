# Abaqus to OpenSeesPy Converter

A Python tool for converting Abaqus `.inp` files to OpenSeesPy Python scripts.

## Features

- Converts Abaqus nodes to OpenSeesPy node definitions
- Maps Abaqus elements (S4R, S3, C3D8, etc.) to appropriate OpenSeesPy elements
- Translates materials, sections, boundary conditions, and loads
- Handles element sets and node sets
- Sets up a basic static analysis framework

## Installation

```bash
pip install abaqus2openseespy
```

Or install from source:

```bash
git clone https://github.com/username/abaqus2openseespy.git
cd abaqus2openseespy
pip install -e .
```

## Usage

### Command Line Interface

```bash
abaqus2openseespy input.inp -o output.py
```

### Python API

```python
from abaqus2openseespy import convert

# Convert Abaqus to OpenSeesPy
convert("input.inp", "output.py")

# Or get the OpenSeesPy script as a string
opensees_script = convert("input.inp", return_string=True)
```

## How It Works

The conversion process follows these main steps:

### 1. Parsing the Abaqus Input File

The `AbaqusParser` class in `parser.py` reads and interprets the Abaqus `.inp` file:

- It processes the file line by line, recognizing Abaqus keywords (like `*Node`, `*Element`, etc.)
- For each keyword section, specialized parsing methods extract the relevant data
- Data is stored in structured Python dictionaries for nodes, elements, materials, etc.
- The parser maintains relationships between entities (e.g., which material is used by which section)

For example, when parsing nodes:
```python
def _parse_nodes(self, lines, start_index):
    line_index = start_index + 1
    while line_index < len(lines):
        line = lines[line_index].strip()
        if not line or line.startswith('*'):
            break
            
        parts = line.split(',')
        node_id = int(parts[0])
        x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
        self.nodes[node_id] = [x, y, z]
        
        line_index += 1
    return line_index
```

### 2. Converting to OpenSeesPy

The `AbaqusToOpenSeesConverter` class in `converter.py` transforms the parsed data into OpenSeesPy commands:

- It generates Python code strings for each OpenSeesPy command
- It maps Abaqus entities to their OpenSeesPy equivalents using the mappings in `mapping.py`
- It maintains consistent IDs and tags across the conversion
- It builds the script in sections: nodes, materials, sections, elements, etc.

For example, when converting nodes:
```python
def _process_nodes(self):
    self.opensees_script.append("# Nodes")
    for node_id, coords in self.parser_data.nodes.items():
        x, y, z = coords
        self.opensees_script.append(f"node({node_id}, {x}, {y}, {z})")
```

### 3. Element Type Mapping

The `mapping.py` module contains dictionaries that define how Abaqus element types map to OpenSeesPy:

```python
ELEMENT_TYPE_MAPPING = {
    'S4': 'ShellMITC4',
    'S4R': 'ShellMITC4',
    'C3D8': 'stdBrick',
    # etc.
}
```

When the converter encounters an Abaqus element type, it looks up the appropriate OpenSeesPy element type.

### 4. Generating Analysis Commands

After translating the model components, the converter adds commands to set up a basic static analysis:
- Constraint handlers
- Numberers
- System of equations
- Solution algorithm
- Integration scheme
- Analysis type

### 5. Complete Workflow

1. The user calls `convert()` with an input file path
2. An `AbaqusParser` instance parses the file
3. An `AbaqusToOpenSeesConverter` instance is created with the parsed data
4. The converter generates OpenSeesPy commands for each component
5. The commands are combined into a complete script
6. The script is either returned as a string or written to a file

## Example

Input (Abaqus .inp):
```
*Node
1, 0.0, 0.0, 0.0
2, 10.0, 0.0, 0.0
...
```

Output (OpenSeesPy .py):
```python
# Translated OpenSeesPy Model
from openseespy.opensees import *

# Start Model
wipe()
model('basic', '-ndm', 3, '-ndf', 6)

# Nodes
node(1, 0.0, 0.0, 0.0)
node(2, 10.0, 0.0, 0.0)
...
```

## Documentation

For detailed documentation, visit [docs](docs/README.md).

## License

MIT License