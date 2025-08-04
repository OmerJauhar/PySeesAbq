"""
Parser module for Abaqus .inp files.
"""

class AbaqusParser:
    """
    Parser for Abaqus .inp files.
    
    This class extracts nodes, elements, materials, sections, boundary conditions,
    loads, element sets, and node sets from Abaqus input files.
    """
    
    def __init__(self):
        self.nodes = {}          # {node_id: [x, y, z]}
        self.elements = {}       # {element_id: {"type": type, "nodes": [node_ids]}}
        self.materials = {}      # {material_name: {property: value}}
        self.sections = {}       # {section_name: {property: value}}
        self.boundaries = {}     # {node_id: [dof_constraints]}
        self.loads = {}          # {node_id: [Fx, Fy, Fz, Mx, My, Mz]}
        self.element_sets = {}   # {set_name: [element_ids]}
        self.node_sets = {}      # {set_name: [node_ids]}
        self.material_mapping = {}  # {section_name: material_name}
        
        # State tracking during parsing
        self.current_section = None
        self.current_material = None
        self.current_elset = None
        self.current_nset = None
        
    def parse(self, inp_file_path):
        """
        Parse the Abaqus .inp file.
        
        Args:
            inp_file_path (str): Path to the Abaqus .inp file.
            
        Returns:
            self: The parser instance with parsed data.
        """
        with open(inp_file_path, 'r') as f:
            lines = f.readlines()
            
        line_index = 0
        while line_index < len(lines):
            line = lines[line_index].strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('**'):
                line_index += 1
                continue
            
            # Handle section keywords
            if line.startswith('*'):
                self._parse_keyword(lines, line_index)
                
            line_index += 1
                
        return self
    
    def _parse_keyword(self, lines, start_index):
        """
        Parse a keyword section from the Abaqus file.
        
        Args:
            lines (list): All lines in the file.
            start_index (int): Starting index for the keyword section.
            
        Returns:
            int: Next line index to process.
        """
        line = lines[start_index].strip()
        keyword = line.split(',')[0].strip().lower()
        
        # Parse different keyword sections
        if keyword == '*node':
            return self._parse_nodes(lines, start_index)
        elif keyword.startswith('*element'):
            return self._parse_elements(lines, start_index)
        elif keyword == '*material':
            return self._parse_material(lines, start_index)
        elif keyword in ['*elastic', '*density']:
            return self._parse_material_property(lines, start_index, keyword[1:])
        elif keyword == '*shell section' or keyword == '*solid section':
            return self._parse_section(lines, start_index)
        elif keyword == '*boundary':
            return self._parse_boundary(lines, start_index)
        elif keyword == '*cload':
            return self._parse_load(lines, start_index)
        elif keyword == '*elset':
            return self._parse_elset(lines, start_index)
        elif keyword == '*nset':
            return self._parse_nset(lines, start_index)
        
        # Skip unknown keywords
        return start_index + 1
    
    def _parse_nodes(self, lines, start_index):
        """Parse node definitions."""
        line_index = start_index + 1
        while line_index < len(lines):
            line = lines[line_index].strip()
            if not line or line.startswith('*') or line.startswith('**'):
                break
                
            parts = line.split(',')
            if len(parts) >= 4:
                node_id = int(parts[0])
                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])
                self.nodes[node_id] = [x, y, z]
            
            line_index += 1
            
        return line_index
    
    def _parse_elements(self, lines, start_index):
        """Parse element definitions."""
        line = lines[start_index].strip()
        parts = line.split(',')
        
        # Extract element type
        element_type = None
        for part in parts:
            if part.strip().lower().startswith('type='):
                element_type = part.split('=')[1].strip()
                break
        
        line_index = start_index + 1
        while line_index < len(lines):
            line = lines[line_index].strip()
            if not line or line.startswith('*') or line.startswith('**'):
                break
                
            parts = line.split(',')
            if len(parts) >= 2:
                element_id = int(parts[0])
                node_ids = [int(node_id.strip()) for node_id in parts[1:] if node_id.strip()]
                self.elements[element_id] = {"type": element_type, "nodes": node_ids}
            
            line_index += 1
            
        return line_index
    
    def _parse_material(self, lines, start_index):
        """Parse material definition."""
        line = lines[start_index].strip()
        parts = line.split(',')
        
        material_name = None
        for part in parts:
            if part.strip().lower().startswith('name='):
                material_name = part.split('=')[1].strip()
                break
        
        if material_name:
            self.current_material = material_name
            self.materials[material_name] = {}
            
        return start_index + 1
    
    def _parse_material_property(self, lines, start_index, property_type):
        """Parse material properties like elastic, density, etc."""
        if not self.current_material:
            return start_index + 1
            
        line_index = start_index + 1
        while line_index < len(lines):
            line = lines[line_index].strip()
            if not line or line.startswith('*') or line.startswith('**'):
                break
                
            parts = line.split(',')
            if property_type.lower() == 'elastic' and len(parts) >= 2:
                self.materials[self.current_material]['E'] = float(parts[0].strip())
                self.materials[self.current_material]['nu'] = float(parts[1].strip())
            elif property_type.lower() == 'density' and len(parts) >= 1:
                self.materials[self.current_material]['rho'] = float(parts[0].strip())
                
            line_index += 1
            
        return line_index
    
    def _parse_section(self, lines, start_index):
        """Parse section definitions."""
        line = lines[start_index].strip()
        parts = line.split(',')
        
        section_name = None
        material_name = None
        thickness = None
        
        for part in parts:
            key_value = part.strip().lower().split('=')
            if len(key_value) == 2:
                key, value = key_value
                if key == 'elset':
                    section_name = value
                elif key == 'material':
                    material_name = value
        
        line_index = start_index + 1
        while line_index < len(lines):
            line = lines[line_index].strip()
            if not line or line.startswith('*') or line.startswith('**'):
                break
                
            parts = line.split(',')
            if len(parts) >= 1:
                thickness = float(parts[0].strip())
                
            line_index += 1
        
        if section_name and material_name:
            self.sections[section_name] = {"material": material_name}
            if thickness is not None:
                self.sections[section_name]["thickness"] = thickness
            self.material_mapping[section_name] = material_name
            
        return line_index
    
    def _parse_boundary(self, lines, start_index):
        """Parse boundary condition definitions."""
        line_index = start_index + 1
        while line_index < len(lines):
            line = lines[line_index].strip()
            if not line or line.startswith('*') or line.startswith('**'):
                break
                
            parts = line.split(',')
            if len(parts) >= 3:
                node_id = int(parts[0])
                first_dof = int(parts[1])
                last_dof = int(parts[2])
                value = 0.0
                if len(parts) >= 4 and parts[3].strip():
                    value = float(parts[3])
                    
                if node_id not in self.boundaries:
                    # Initialize with free DOFs
                    self.boundaries[node_id] = [0, 0, 0, 0, 0, 0]
                    
                # Mark constrained DOFs (1 = fixed, 0 = free)
                for dof in range(first_dof-1, last_dof):
                    if dof < 6:  # Ensure we don't exceed 6 DOFs
                        self.boundaries[node_id][dof] = 1
                
            line_index += 1
            
        return line_index
    
    def _parse_load(self, lines, start_index):
        """Parse load definitions."""
        line_index = start_index + 1
        while line_index < len(lines):
            line = lines[line_index].strip()
            if not line or line.startswith('*') or line.startswith('**'):
                break
                
            parts = line.split(',')
            if len(parts) >= 3:
                node_id = int(parts[0])
                dof = int(parts[1])
                value = float(parts[2])
                
                if node_id not in self.loads:
                    # Initialize with zero loads
                    self.loads[node_id] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                    
                # Apply load at the specified DOF (1-indexed in Abaqus)
                if 1 <= dof <= 6:
                    self.loads[node_id][dof-1] = value
                
            line_index += 1
            
        return line_index
    
    def _parse_elset(self, lines, start_index):
        """Parse element set definitions."""
        line = lines[start_index].strip()
        parts = line.split(',')
        
        set_name = None
        for part in parts:
            if part.strip().lower().startswith('elset='):
                set_name = part.split('=')[1].strip()
                break
        
        if set_name:
            self.current_elset = set_name
            self.element_sets[set_name] = []
            
            line_index = start_index + 1
            while line_index < len(lines):
                line = lines[line_index].strip()
                if not line or line.startswith('*') or line.startswith('**'):
                    break
                    
                parts = line.split(',')
                for part in parts:
                    if part.strip():
                        try:
                            element_id = int(part.strip())
                            self.element_sets[set_name].append(element_id)
                        except ValueError:
                            pass
                    
                line_index += 1
                
            return line_index
        
        return start_index + 1
    
    def _parse_nset(self, lines, start_index):
        """Parse node set definitions."""
        line = lines[start_index].strip()
        parts = line.split(',')
        
        set_name = None
        for part in parts:
            if part.strip().lower().startswith('nset='):
                set_name = part.split('=')[1].strip()
                break
        
        if set_name:
            self.current_nset = set_name
            self.node_sets[set_name] = []
            
            line_index = start_index + 1
            while line_index < len(lines):
                line = lines[line_index].strip()
                if not line or line.startswith('*') or line.startswith('**'):
                    break
                    
                parts = line.split(',')
                for part in parts:
                    if part.strip():
                        try:
                            node_id = int(part.strip())
                            self.node_sets[set_name].append(node_id)
                        except ValueError:
                            pass
                    
                line_index += 1
                
            return line_index
        
        return start_index + 1