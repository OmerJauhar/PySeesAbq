"""
Mapping module for Abaqus to OpenSeesPy conversions.
"""

# Element type mapping from Abaqus to OpenSeesPy
ELEMENT_TYPE_MAPPING = {
    # Shell elements
    'S4': 'ShellMITC4',
    'S4R': 'ShellMITC4',
    'S3': 'ShellDKGT',
    'S3R': 'ShellDKGT',
    'STRI3': 'ShellDKGT',
    
    # Solid elements
    'C3D8': 'stdBrick',
    'C3D8R': 'stdBrick',
    'C3D8I': 'stdBrick',
    'C3D4': 'FourNodeTetrahedron',
    
    # Beam/truss elements
    'B31': 'elasticBeamColumn',
    'B31R': 'elasticBeamColumn',
    'T3D2': 'truss',
    'T2D2': 'truss',
}

# Material type mapping
MATERIAL_TYPE_MAPPING = {
    'ELASTIC': 'ElasticIsotropic',
    'PLASTIC': 'ElasticIsotropic',  # Simplified mapping for now
    'HYPERELASTIC': 'ElasticIsotropic',  # Simplified mapping for now
}

# Section type mapping
SECTION_TYPE_MAPPING = {
    'SHELL': 'ElasticMembranePlateSection',
    'SOLID': 'ElasticIsotropic',
    'BEAM': 'ElasticBeamColumn',
}

def get_opensees_element_type(abaqus_type):
    """
    Get the equivalent OpenSeesPy element type.
    
    Args:
        abaqus_type (str): Abaqus element type
        
    Returns:
        str: OpenSeesPy element type or default
    """
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