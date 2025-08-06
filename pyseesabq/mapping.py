"""
Mapping module for Abaqus to OpenSeesPy conversions.
"""

"""
Mapping module for Abaqus to OpenSeesPy conversions.

This module provides comprehensive mapping tables and functions for converting
Abaqus element types, material properties, and section definitions to their
OpenSeesPy equivalents.
"""

from typing import Dict, Optional


# Element type mapping from Abaqus to OpenSeesPy
ELEMENT_TYPE_MAPPING: Dict[str, str] = {
    # Shell elements
    'S4': 'ShellMITC4',
    'S4R': 'ShellMITC4',
    'S4R5': 'ShellMITC4', 
    'S3': 'ShellDKGT',
    'S3R': 'ShellDKGT',
    'STRI3': 'ShellDKGT',
    'STRI65': 'ShellDKGT',
    
    # Solid elements
    'C3D8': 'stdBrick',
    'C3D8R': 'stdBrick',
    'C3D8I': 'stdBrick',
    'C3D8H': 'stdBrick',
    'C3D20': 'stdBrick',
    'C3D20R': 'stdBrick',
    'C3D4': 'FourNodeTetrahedron',
    'C3D10': 'TenNodeTetrahedron',
    'C3D6': 'stdBrick',  # Wedge element, approximate with brick
    'C3D15': 'stdBrick', # 15-node wedge, approximate with brick
    
    # Beam/truss elements  
    'B31': 'elasticBeamColumn',
    'B31R': 'elasticBeamColumn',
    'B32': 'elasticBeamColumn',
    'B33': 'elasticBeamColumn',
    'T3D2': 'truss',
    'T3D3': 'truss',
    'T2D2': 'truss',
    'T2D3': 'truss',
    
    # Frame elements
    'FRAME3D': 'elasticBeamColumn',
    'PIPE31': 'elasticBeamColumn',
    'PIPE32': 'elasticBeamColumn',
    
    # Membrane elements
    'M3D3': 'tri31',
    'M3D4': 'quad4n',
    'M3D4R': 'quad4n',
    'M3D6': 'tri31',
    'M3D8': 'quad4n',
}

# Material type mapping
MATERIAL_TYPE_MAPPING: Dict[str, str] = {
    'ELASTIC': 'ElasticIsotropic',
    'PLASTIC': 'J2Plasticity',
    'HYPERELASTIC': 'ElasticIsotropic',  # Simplified mapping
    'CONCRETE': 'Concrete01',
    'STEEL': 'Steel01',
}

# Section type mapping
SECTION_TYPE_MAPPING: Dict[str, str] = {
    'SHELL': 'ElasticMembranePlateSection',
    'SOLID': 'ElasticIsotropic',
    'BEAM': 'ElasticBeamColumn',
    'PIPE': 'ElasticBeamColumn',
    'GENERAL': 'ElasticBeamColumn',
}

# DOF mapping for boundary conditions
DOF_MAPPING: Dict[int, int] = {
    1: 1,  # UX -> UX  
    2: 2,  # UY -> UY
    3: 3,  # UZ -> UZ
    4: 4,  # ROTX -> ROTX
    5: 5,  # ROTY -> ROTY  
    6: 6,  # ROTZ -> ROTZ
}


def get_opensees_element_type(abaqus_type: str) -> str:
    """
    Get the equivalent OpenSeesPy element type for an Abaqus element.
    
    Args:
        abaqus_type: Abaqus element type (e.g., 'S4R', 'C3D8')
        
    Returns:
        Corresponding OpenSeesPy element type
    """
    # Normalize the input (remove spaces, convert to uppercase)
    normalized_type = abaqus_type.strip().upper()
    
    # Direct mapping lookup
    if normalized_type in ELEMENT_TYPE_MAPPING:
        return ELEMENT_TYPE_MAPPING[normalized_type]
    
    # Fallback mappings based on element family
    if normalized_type.startswith('S'):
        return 'ShellMITC4'  # Default shell element
    elif normalized_type.startswith('C3D'):
        return 'stdBrick'    # Default solid element  
    elif normalized_type.startswith(('B', 'PIPE')):
        return 'elasticBeamColumn'  # Default beam element
    elif normalized_type.startswith('T'):
        return 'truss'       # Default truss element
    elif normalized_type.startswith('M'):
        return 'quad4n'      # Default membrane element
    else:
        # Ultimate fallback
        return 'ShellMITC4'


def get_opensees_material_type(abaqus_material_type: str) -> str:
    """
    Get the equivalent OpenSeesPy material type for an Abaqus material.
    
    Args:
        abaqus_material_type: Abaqus material behavior type
        
    Returns:
        Corresponding OpenSeesPy material type
    """
    normalized_type = abaqus_material_type.strip().upper()
    return MATERIAL_TYPE_MAPPING.get(normalized_type, 'ElasticIsotropic')


def get_opensees_section_type(abaqus_section_type: str) -> str:
    """
    Get the equivalent OpenSeesPy section type for an Abaqus section.
    
    Args:
        abaqus_section_type: Abaqus section type
        
    Returns:
        Corresponding OpenSeesPy section type
    """
    normalized_type = abaqus_section_type.strip().upper()
    return SECTION_TYPE_MAPPING.get(normalized_type, 'ElasticMembranePlateSection')


def map_dof_constraints(abaqus_dofs: list) -> list:
    """
    Map Abaqus DOF constraints to OpenSeesPy format.
    
    Args:
        abaqus_dofs: List of Abaqus DOF numbers to constrain
        
    Returns:
        List of OpenSeesPy constraint values (0=free, 1=fixed)
    """
    # Initialize all 6 DOFs as free (0)
    constraints = [0, 0, 0, 0, 0, 0]
    
    # Set constrained DOFs to 1
    for dof in abaqus_dofs:
        if 1 <= dof <= 6:
            constraints[dof - 1] = 1  # Convert 1-based to 0-based indexing
            
    return constraints


def get_element_node_count(element_type: str) -> int:
    """
    Get the expected number of nodes for an element type.
    
    Args:
        element_type: Abaqus element type
        
    Returns:
        Expected number of nodes for the element
    """
    node_counts = {
        # Shell elements
        'S3': 3, 'S3R': 3, 'STRI3': 3,
        'S4': 4, 'S4R': 4, 'S4R5': 4,
        'S6': 6, 'S8R': 8, 'STRI65': 6,
        
        # Solid elements
        'C3D4': 4, 'C3D10': 10,
        'C3D6': 6, 'C3D15': 15,
        'C3D8': 8, 'C3D8R': 8, 'C3D8I': 8, 'C3D8H': 8,
        'C3D20': 20, 'C3D20R': 20,
        
        # Beam/truss elements
        'B31': 2, 'B31R': 2, 'B32': 3, 'B33': 2,
        'T3D2': 2, 'T3D3': 3, 'T2D2': 2, 'T2D3': 3,
        
        # Membrane elements
        'M3D3': 3, 'M3D4': 4, 'M3D4R': 4,
        'M3D6': 6, 'M3D8': 8,
    }
    
    return node_counts.get(element_type.upper(), 4)  # Default to 4 nodes
    return ELEMENT_TYPE_MAPPING.get(abaqus_type.upper(), 'ShellMITC4')

def get_opensees_material_type(abaqus_type):
    """
    Get the equivalent OpenSeesPy material type.
    
    Args:
        abaqus_type (str): Abaqus material type
        
    Returns:
        str: OpenSeesPy material type or default
    """
    return MATERIAL_TYPE_MAPPING.get(abaqus_type.upper(), 'ElasticIsotropic')

def get_opensees_section_type(abaqus_type):
    """
    Get the equivalent OpenSeesPy section type.
    
    Args:
        abaqus_type (str): Abaqus section type
        
    Returns:
        str: OpenSeesPy section type or default
    """
    return SECTION_TYPE_MAPPING.get(abaqus_type.upper(), 'ElasticMembranePlateSection')