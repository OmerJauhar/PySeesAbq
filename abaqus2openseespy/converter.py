"""
Converter module for transforming Abaqus data to OpenSeesPy Python script.
"""
from .parser import AbaqusParser

class AbaqusToOpenSeesConverter:
    """
    Converter class for transforming Abaqus data to OpenSeesPy.
    """
    
    def __init__(self, parser_data=None):
        """
        Initialize converter with parsed Abaqus data.
        
        Args:
            parser_data (AbaqusParser, optional): Parsed Abaqus data. Defaults to None.
        """
        self.parser_data = parser_data
        self.opensees_script = []
        self.material_tags = {}  # Maps Abaqus material names to OpenSees material tags
        self.section_tags = {}   # Maps Abaqus section names to OpenSees section tags
        
    def convert(self, inp_file_path=None):
        """
        Convert Abaqus .inp file to OpenSeesPy script.
        
        Args:
            inp_file_path (str, optional): Path to Abaqus .inp file if parser_data not provided.
            
        Returns:
            str: OpenSeesPy Python script.
        """
        if inp_file_path and not self.parser_data:
            parser = AbaqusParser()
            self.parser_data = parser.parse(inp_file_path)
        
        if not self.parser_data:
            raise ValueError("No Abaqus data provided for conversion.")
        
        # Initialize script
        self._add_script_header()
        
        # Process model components
        self._process_nodes()
        self._process_materials()
        self._process_sections()
        self._process_elements()
        self._process_boundaries()
        self._process_loads()
        
        # Add analysis commands
        self._add_analysis_setup()
        
        return "\n".join(self.opensees_script)
    
    def _add_script_header(self):
        """Add script header and model initialization."""
        self.opensees_script.extend([
            "# Translated OpenSeesPy Model",
            "from openseespy.opensees import *",
            "",
            "# Start Model",
            "wipe()",
            "model('basic', '-ndm', 3, '-ndf', 6)",
            ""
        ])
    
    def _process_nodes(self):
        """Process nodes from Abaqus data."""
        self.opensees_script.append("# Nodes")
        for node_id, coords in self.parser_data.nodes.items():
            x, y, z = coords
            self.opensees_script.append(f"node({node_id}, {x}, {y}, {z})")
        self.opensees_script.append("")
    
    def _process_materials(self):
        """Process materials from Abaqus data."""
        self.opensees_script.append("# Materials")
        
        material_tag = 1
        for material_name, properties in self.parser_data.materials.items():
            E = properties.get('E', 1.0)  # Default elastic modulus
            nu = properties.get('nu', 0.3)  # Default Poisson's ratio
            rho = properties.get('rho', 0.0)  # Default density
            
            self.opensees_script.append(f"nDMaterial('ElasticIsotropic', {material_tag}, {E}, {nu}, {rho})")
            self.material_tags[material_name] = material_tag
            material_tag += 1
        
        self.opensees_script.append("")
    
    def _process_sections(self):
        """Process sections from Abaqus data."""
        self.opensees_script.append("# Sections")
        
        section_tag = 1
        for section_name, properties in self.parser_data.sections.items():
            material_name = properties.get('material')
            thickness = properties.get('thickness', 1.0)  # Default thickness
            
            if material_name in self.material_tags:
                material_tag = self.material_tags[material_name]
                material_props = self.parser_data.materials.get(material_name, {})
                E = material_props.get('E', 1.0)  # Default elastic modulus
                nu = material_props.get('nu', 0.3)  # Default Poisson's ratio
                
                self.opensees_script.append(
                    f"section('ElasticMembranePlateSection', {section_tag}, {E}, {nu}, {thickness}, {material_tag})"
                )
                self.section_tags[section_name] = section_tag
                section_tag += 1
        
        self.opensees_script.append("")
    
    def _process_elements(self):
        """Process elements from Abaqus data."""
        self.opensees_script.append("# Elements")
        
        # Group elements by type for batch processing
        elements_by_type = {}
        for element_id, element_data in self.parser_data.elements.items():
            element_type = element_data['type']
            if element_type not in elements_by_type:
                elements_by_type[element_type] = []
            elements_by_type[element_type].append((element_id, element_data['nodes']))
        
        # Process each element type
        for element_type, elements in elements_by_type.items():
            # Determine the OpenSeesPy element type
            opensees_element_type = self._map_element_type(element_type)
            
            # Find appropriate section tag for these elements
            # For simplicity, use the first available section tag
            section_tag = 1
            if self.section_tags:
                section_tag = list(self.section_tags.values())[0]
            
            # Create elements in OpenSeesPy
            for element_id, node_ids in elements:
                nodes_str = ", ".join(map(str, node_ids))
                self.opensees_script.append(
                    f"element('{opensees_element_type}', {element_id}, {nodes_str}, {section_tag})"
                )
        
        self.opensees_script.append("")
    
    def _map_element_type(self, abaqus_element_type):
        """
        Map Abaqus element types to OpenSeesPy element types.
        
        Args:
            abaqus_element_type (str): Abaqus element type.
            
        Returns:
            str: Equivalent OpenSeesPy element type.
        """
        element_mapping = {
            'S4': 'ShellMITC4',
            'S4R': 'ShellMITC4',
            'S3': 'ShellDKGT',
            'C3D8': 'stdBrick',
            'C3D8R': 'stdBrick',
            'C3D4': 'FourNodeTetrahedron',
            'T3D2': 'Truss',
            'B31': 'elasticBeamColumn',
        }
        
        return element_mapping.get(abaqus_element_type, 'ShellMITC4')  # Default to ShellMITC4
    
    def _process_boundaries(self):
        """Process boundary conditions from Abaqus data."""
        self.opensees_script.append("# Constraints")
        
        for node_id, constraints in self.parser_data.boundaries.items():
            constraints_str = ", ".join(map(str, constraints))
            self.opensees_script.append(f"fix({node_id}, {constraints_str})")
        
        self.opensees_script.append("")
    
    def _process_loads(self):
        """Process loads from Abaqus data."""
        if not self.parser_data.loads:
            return
            
        self.opensees_script.append("# Loads")
        self.opensees_script.append("pattern('Plain', 1, 1)")
        
        for node_id, loads in self.parser_data.loads.items():
            load_str = ", ".join(map(str, loads))
            self.opensees_script.append(f"load({node_id}, {load_str})")
        
        self.opensees_script.append("")
    
    def _add_analysis_setup(self):
        """Add analysis setup commands."""
        self.opensees_script.extend([
            "# Analysis",
            "constraints('Plain')",
            "numberer('Plain')",
            "system('BandGeneral')",
            "test('NormDispIncr', 1.0e-6, 10)",
            "algorithm('Newton')",
            "integrator('LoadControl', 1.0)",
            "analysis('Static')",
            "analyze(1)",
            "",
            "printModel()"
        ])

def convert(inp_file_path, output_file_path=None, return_string=False):
    """
    Convert Abaqus .inp file to OpenSeesPy Python script.
    
    Args:
        inp_file_path (str): Path to Abaqus .inp file.
        output_file_path (str, optional): Path to save the OpenSeesPy script. 
                                         If None, doesn't save to file.
        return_string (bool, optional): Whether to return the script as a string. 
                                       Default is False.
                                       
    Returns:
        str or None: OpenSeesPy script if return_string is True, else None.
    """
    parser = AbaqusParser()
    parser_data = parser.parse(inp_file_path)
    
    converter = AbaqusToOpenSeesConverter(parser_data)
    opensees_script = converter.convert()
    
    if output_file_path:
        with open(output_file_path, 'w') as f:
            f.write(opensees_script)
    
    if return_string:
        return opensees_script
    
    return None