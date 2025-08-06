#!/usr/bin/env python3
"""
Example script demonstrating PySeesAbq usage.

This script shows how to use PySeesAbq both programmatically and via CLI.
"""

import os
import tempfile
from pathlib import Path

# Example Abaqus .inp content
EXAMPLE_INP_CONTENT = """**
** Simple beam example for PySeesAbq demonstration
** A cantilever beam with a tip load
**
*Node
1, 0.0, 0.0, 0.0
2, 1.0, 0.0, 0.0
3, 2.0, 0.0, 0.0
4, 3.0, 0.0, 0.0
5, 4.0, 0.0, 0.0
*Element, type=B31
1, 1, 2
2, 2, 3
3, 3, 4
4, 4, 5
*Material, name=Steel
*Elastic
200000, 0.3
*Density
7850
*Beam Section, elset=Beam, material=Steel
0.01, 0.001
*Elset, elset=Beam
1, 2, 3, 4
*Boundary
1, 1, 6, 0.0
*Cload
5, 2, -1000.0
**
** End of input file
"""


def create_example_file():
    """Create an example .inp file."""
    example_dir = Path("examples")
    example_dir.mkdir(exist_ok=True)
    
    inp_file = example_dir / "cantilever_beam.inp"
    with open(inp_file, 'w') as f:
        f.write(EXAMPLE_INP_CONTENT)
    
    print(f"Created example file: {inp_file}")
    return inp_file


def demonstrate_api_usage(inp_file):
    """Demonstrate the Python API."""
    print("\n" + "="*50)
    print("Python API Demonstration")
    print("="*50)
    
    try:
        # Method 1: Using the high-level convert_file function
        from pyseesabq import convert_file
        
        print("\n1. Using convert_file():")
        output_path = convert_file(inp_file, verbose=True)
        print(f"   Generated: {output_path}")
        
        # Method 2: Using the convert function to get script as string
        from pyseesabq import convert
        
        print("\n2. Using convert() to get script as string:")
        script_content = convert(inp_file, return_string=True)
        print(f"   Script length: {len(script_content)} characters")
        print("   First few lines:")
        for i, line in enumerate(script_content.split('\n')[:5]):
            print(f"   {i+1}: {line}")
        
        # Method 3: Using classes directly for more control
        from pyseesabq import AbaqusParser, AbaqusToOpenSeesConverter
        
        print("\n3. Using classes directly:")
        parser = AbaqusParser()
        data = parser.parse(inp_file)
        
        print(f"   Parsed nodes: {len(data.nodes)}")
        print(f"   Parsed elements: {len(data.elements)}")
        print(f"   Parsed materials: {len(data.materials)}")
        
        converter = AbaqusToOpenSeesConverter(data)
        script = converter.convert()
        
        # Save with custom name
        custom_output = inp_file.with_name("custom_output.py")
        with open(custom_output, 'w') as f:
            f.write(script)
        print(f"   Saved custom output: {custom_output}")
        
    except Exception as e:
        print(f"Error in API demonstration: {e}")


def demonstrate_cli_usage(inp_file):
    """Demonstrate the CLI usage."""
    print("\n" + "="*50)
    print("CLI Demonstration")
    print("="*50)
    
    import subprocess
    import sys
    
    try:
        # Show version
        print("\n1. Checking version:")
        result = subprocess.run([sys.executable, "-m", "pyseesabq", "--version"], 
                              capture_output=True, text=True)
        print(f"   {result.stdout.strip()}")
        
        # Show file info
        print("\n2. Getting file information:")
        result = subprocess.run([sys.executable, "-m", "pyseesabq", "info", str(inp_file)], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   " + result.stdout.replace('\n', '\n   '))
        else:
            print(f"   Error: {result.stderr}")
        
        # Convert file
        print("\n3. Converting file:")
        output_file = inp_file.with_suffix('.converted.py')
        result = subprocess.run([
            sys.executable, "-m", "pyseesabq", "convert", 
            str(inp_file), "-o", str(output_file), "--verbose"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   " + result.stdout.replace('\n', '\n   '))
            print(f"   Generated: {output_file}")
        else:
            print(f"   Error: {result.stderr}")
            
    except Exception as e:
        print(f"Error in CLI demonstration: {e}")


def show_generated_output(inp_file):
    """Show the generated OpenSeesPy output."""
    print("\n" + "="*50)
    print("Generated OpenSeesPy Script")
    print("="*50)
    
    py_file = inp_file.with_suffix('.py')
    if py_file.exists():
        with open(py_file, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        print(f"\nShowing first 30 lines of {py_file}:")
        print("-" * 40)
        
        for i, line in enumerate(lines[:30], 1):
            print(f"{i:2d}: {line}")
        
        if len(lines) > 30:
            print(f"... ({len(lines) - 30} more lines)")
        
        print("-" * 40)
        print(f"Total lines: {len(lines)}")
    else:
        print(f"Generated file {py_file} not found")


def main():
    """Main demonstration function."""
    print("PySeesAbq Example and Demonstration")
    print("="*50)
    
    # Create example file
    inp_file = create_example_file()
    
    # Demonstrate API usage
    demonstrate_api_usage(inp_file)
    
    # Demonstrate CLI usage  
    demonstrate_cli_usage(inp_file)
    
    # Show generated output
    show_generated_output(inp_file)
    
    print("\n" + "="*50)
    print("Demonstration completed!")
    print("Check the 'examples/' directory for generated files.")
    print("="*50)


if __name__ == "__main__":
    main()
