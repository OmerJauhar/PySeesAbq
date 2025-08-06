"""
Core functionality for PySeesAbq package.

This module provides the main high-level functions for converting Abaqus files.
"""

import os
from pathlib import Path
from typing import Optional, Union

from .parser import AbaqusParser
from .converter import AbaqusToOpenSeesConverter


def convert_file(
    input_file: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    overwrite: bool = False,
    verbose: bool = False
) -> str:
    """
    Convert an Abaqus .inp file to OpenSeesPy Python script.
    
    Args:
        input_file: Path to the input Abaqus .inp file
        output_file: Path to the output Python file. If None, uses input filename with .py extension
        overwrite: Whether to overwrite existing output file
        verbose: Whether to print verbose output
        
    Returns:
        str: Path to the generated OpenSeesPy script
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        FileExistsError: If output file exists and overwrite is False
        ValueError: If input file is not a .inp file
    """
    input_path = Path(input_file)
    
    # Validate input file
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if input_path.suffix.lower() != '.inp':
        raise ValueError(f"Input file must have .inp extension, got: {input_path.suffix}")
    
    # Determine output file path
    if output_file is None:
        output_path = input_path.with_suffix('.py')
    else:
        output_path = Path(output_file)
    
    # Check if output file exists
    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"Output file already exists: {output_path}. Use --overwrite to replace it."
        )
    
    if verbose:
        print(f"Converting {input_path} to {output_path}")
    
    # Parse and convert
    parser = AbaqusParser()
    parsed_data = parser.parse(str(input_path))
    
    converter = AbaqusToOpenSeesConverter(parsed_data)
    opensees_script = converter.convert()
    
    # Write output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(opensees_script)
    
    if verbose:
        print(f"Conversion completed successfully!")
        print(f"Generated: {output_path}")
        print(f"Nodes: {len(parsed_data.nodes)}")
        print(f"Elements: {len(parsed_data.elements)}")
        print(f"Materials: {len(parsed_data.materials)}")
    
    return str(output_path)


def convert(
    input_file: Union[str, Path],
    return_string: bool = False
) -> Union[str, None]:
    """
    Convert an Abaqus .inp file to OpenSeesPy Python script.
    
    Args:
        input_file: Path to the input Abaqus .inp file
        return_string: If True, return the script as string instead of writing to file
        
    Returns:
        str or None: The OpenSeesPy script if return_string=True, otherwise None
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Parse and convert
    parser = AbaqusParser()
    parsed_data = parser.parse(str(input_path))
    
    converter = AbaqusToOpenSeesConverter(parsed_data)
    opensees_script = converter.convert()
    
    if return_string:
        return opensees_script
    else:
        output_path = input_path.with_suffix('.py')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(opensees_script)
        return str(output_path)
