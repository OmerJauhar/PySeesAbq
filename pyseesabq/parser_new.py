"""
Parser module for Abaqus .inp files.

This module provides comprehensive parsing of Abaqus input files, extracting
nodes, elements, materials, sections, boundary conditions, loads, and sets.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Any


logger = logging.getLogger(__name__)


class AbaqusParser:
    """
    Parser for Abaqus .inp files.
    
    This class extracts nodes, elements, materials, sections, boundary conditions,
    loads, element sets, and node sets from Abaqus input files with comprehensive
    error handling and validation.
    """
    
    def __init__(self):
        """Initialize the parser with empty data structures."""
        self.nodes: Dict[int, List[float]] = {}          # {node_id: [x, y, z]}
        self.elements: Dict[int, Dict[str, Any]] = {}    # {element_id: {"type": type, "nodes": [node_ids]}}
        self.materials: Dict[str, Dict[str, float]] = {} # {material_name: {property: value}}
        self.sections: Dict[str, Dict[str, Any]] = {}    # {section_name: {property: value}}
        self.boundaries: Dict[int, List[int]] = {}       # {node_id: [dof_constraints]}
        self.loads: Dict[int, List[float]] = {}          # {node_id: [Fx, Fy, Fz, Mx, My, Mz]}
        self.element_sets: Dict[str, List[int]] = {}     # {set_name: [element_ids]}
        self.node_sets: Dict[str, List[int]] = {}        # {set_name: [node_ids]}
        self.material_mapping: Dict[str, str] = {}       # {section_name: material_name}
        
        # State tracking during parsing
        self.current_section: Optional[str] = None
        self.current_material: Optional[str] = None
        self.current_elset: Optional[str] = None
        self.current_nset: Optional[str] = None
        
    def parse(self, inp_file_path: Union[str, Path]) -> 'AbaqusParser':
        """
        Parse the Abaqus .inp file.
        
        Args:
            inp_file_path: Path to the Abaqus .inp file.
            
        Returns:
            The parser instance with parsed data.
            
        Raises:
            FileNotFoundError: If the input file doesn't exist.
            ValueError: If the file cannot be parsed.
        """
        file_path = Path(inp_file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
            
        logger.info(f"Parsing Abaqus file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
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
                line_index = self._parse_keyword(lines, line_index)
            else:
                line_index += 1
                
        logger.info(f"Parsing completed: {len(self.nodes)} nodes, {len(self.elements)} elements")
        return self
    
    def _parse_keyword(self, lines: List[str], start_index: int) -> int:
        """
        Parse a keyword section from the Abaqus file.
        
        Args:
            lines: All lines in the file.
            start_index: Starting index for the keyword section.
            
        Returns:
            Next line index to process.
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

    def _parse_nodes(self, lines: List[str], start_index: int) -> int:
        """Parse node definitions."""
        line_index = start_index + 1
        
        while line_index < len(lines):
            line = lines[line_index].strip()
            
            # Stop if we hit another keyword or empty line
            if not line or line.startswith('*'):
                break
                
            # Skip comments
            if line.startswith('**'):
                line_index += 1
                continue
            
            try:
                parts = [part.strip() for part in line.split(',')]
                if len(parts) >= 4:
                    node_id = int(parts[0])
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    self.nodes[node_id] = [x, y, z]
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse node at line {line_index + 1}: {line} - {e}")
            
            line_index += 1
            
        return line_index

    def _parse_elements(self, lines: List[str], start_index: int) -> int:
        """Parse element definitions."""
        line = lines[start_index].strip()
        parts = line.split(',')
        
        # Extract element type
        element_type = None
        for part in parts:
            if part.strip().lower().startswith('type='):
                element_type = part.strip().split('=')[1].strip()
                break
        
        if not element_type:
            logger.warning(f"No element type found in line: {line}")
            return start_index + 1
        
        line_index = start_index + 1
        while line_index < len(lines):
            line = lines[line_index].strip()
            
            # Stop if we hit another keyword or empty line
            if not line or line.startswith('*'):
                break
                
            # Skip comments
            if line.startswith('**'):
                line_index += 1
                continue
            
            try:
                parts = [part.strip() for part in line.split(',')]
                if len(parts) >= 2:
                    element_id = int(parts[0])
                    node_ids = [int(parts[i]) for i in range(1, len(parts))]
                    self.elements[element_id] = {
                        'type': element_type,
                        'nodes': node_ids
                    }
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse element at line {line_index + 1}: {line} - {e}")
            
            line_index += 1
            
        return line_index

    def _parse_material(self, lines: List[str], start_index: int) -> int:
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
            if material_name not in self.materials:
                self.materials[material_name] = {}
        
        return start_index + 1

    def _parse_material_property(self, lines: List[str], start_index: int, property_type: str) -> int:
        """Parse material property like elastic or density."""
        if not self.current_material:
            return start_index + 1
            
        line_index = start_index + 1
        while line_index < len(lines):
            line = lines[line_index].strip()
            
            if not line or line.startswith('*'):
                break
                
            if line.startswith('**'):
                line_index += 1
                continue
            
            try:
                parts = [part.strip() for part in line.split(',')]
                if property_type == 'elastic' and len(parts) >= 2:
                    self.materials[self.current_material]['E'] = float(parts[0])
                    self.materials[self.current_material]['nu'] = float(parts[1])
                elif property_type == 'density' and len(parts) >= 1:
                    self.materials[self.current_material]['rho'] = float(parts[0])
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse {property_type} at line {line_index + 1}: {line} - {e}")
            
            line_index += 1
            
        return line_index

    def _parse_section(self, lines: List[str], start_index: int) -> int:
        """Parse section definition."""
        line = lines[start_index].strip()
        parts = line.split(',')
        
        section_name = f"section_{len(self.sections) + 1}"
        material_name = None
        elset_name = None
        
        for part in parts:
            part = part.strip().lower()
            if part.startswith('material='):
                material_name = part.split('=')[1].strip()
            elif part.startswith('elset='):
                elset_name = part.split('=')[1].strip()
        
        line_index = start_index + 1
        thickness = 1.0
        
        if line_index < len(lines):
            line = lines[line_index].strip()
            if line and not line.startswith('*') and not line.startswith('**'):
                try:
                    thickness = float(line.split(',')[0])
                    line_index += 1
                except (ValueError, IndexError):
                    pass
        
        self.sections[section_name] = {
            'material': material_name,
            'thickness': thickness,
            'elset': elset_name
        }
        
        if material_name:
            self.material_mapping[section_name] = material_name
        
        return line_index

    def _parse_boundary(self, lines: List[str], start_index: int) -> int:
        """Parse boundary conditions."""
        line_index = start_index + 1
        
        while line_index < len(lines):
            line = lines[line_index].strip()
            
            if not line or line.startswith('*'):
                break
                
            if line.startswith('**'):
                line_index += 1
                continue
            
            try:
                parts = [part.strip() for part in line.split(',')]
                if len(parts) >= 3:
                    node_id = int(parts[0])
                    dof_start = int(parts[1])
                    dof_end = int(parts[2])
                    
                    # Create constraint array (1=fixed, 0=free)
                    constraints = [0, 0, 0, 0, 0, 0]
                    for dof in range(dof_start, dof_end + 1):
                        if 1 <= dof <= 6:
                            constraints[dof - 1] = 1
                    
                    self.boundaries[node_id] = constraints
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse boundary at line {line_index + 1}: {line} - {e}")
            
            line_index += 1
            
        return line_index

    def _parse_load(self, lines: List[str], start_index: int) -> int:
        """Parse concentrated loads."""
        line_index = start_index + 1
        
        while line_index < len(lines):
            line = lines[line_index].strip()
            
            if not line or line.startswith('*'):
                break
                
            if line.startswith('**'):
                line_index += 1
                continue
            
            try:
                parts = [part.strip() for part in line.split(',')]
                if len(parts) >= 3:
                    node_id = int(parts[0])
                    dof = int(parts[1])
                    magnitude = float(parts[2])
                    
                    # Initialize load array [Fx, Fy, Fz, Mx, My, Mz]
                    if node_id not in self.loads:
                        self.loads[node_id] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                    
                    # Apply load to appropriate DOF
                    if 1 <= dof <= 6:
                        self.loads[node_id][dof - 1] = magnitude
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse load at line {line_index + 1}: {line} - {e}")
            
            line_index += 1
            
        return line_index

    def _parse_elset(self, lines: List[str], start_index: int) -> int:
        """Parse element set definition."""
        line = lines[start_index].strip()
        parts = line.split(',')
        
        elset_name = None
        for part in parts:
            if part.strip().lower().startswith('elset='):
                elset_name = part.split('=')[1].strip()
                break
        
        if not elset_name:
            return start_index + 1
        
        line_index = start_index + 1
        element_ids = []
        
        while line_index < len(lines):
            line = lines[line_index].strip()
            
            if not line or line.startswith('*'):
                break
                
            if line.startswith('**'):
                line_index += 1
                continue
            
            try:
                parts = [part.strip() for part in line.split(',')]
                for part in parts:
                    if part:
                        element_ids.append(int(part))
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse elset at line {line_index + 1}: {line} - {e}")
            
            line_index += 1
        
        self.element_sets[elset_name] = element_ids
        return line_index

    def _parse_nset(self, lines: List[str], start_index: int) -> int:
        """Parse node set definition."""
        line = lines[start_index].strip()
        parts = line.split(',')
        
        nset_name = None
        for part in parts:
            if part.strip().lower().startswith('nset='):
                nset_name = part.split('=')[1].strip()
                break
        
        if not nset_name:
            return start_index + 1
        
        line_index = start_index + 1
        node_ids = []
        
        while line_index < len(lines):
            line = lines[line_index].strip()
            
            if not line or line.startswith('*'):
                break
                
            if line.startswith('**'):
                line_index += 1
                continue
            
            try:
                parts = [part.strip() for part in line.split(',')]
                for part in parts:
                    if part:
                        node_ids.append(int(part))
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse nset at line {line_index + 1}: {line} - {e}")
            
            line_index += 1
        
        self.node_sets[nset_name] = node_ids
        return line_index
