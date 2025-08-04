"""
Tests for the Abaqus to OpenSeesPy converter module.
"""
import unittest
import os
import tempfile
from abaqus2openseespy.parser import AbaqusParser
from abaqus2openseespy.converter import AbaqusToOpenSeesConverter, convert

class TestAbaqusToOpenSeesConverter(unittest.TestCase):
    """Test cases for the AbaqusToOpenSeesConverter class."""
    
    def setUp(self):
        # Create a temporary Abaqus .inp file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.inp')
        self.temp_file.write(b"""**
** Sample Abaqus input file for testing
**
*Node
1, 0.0, 0.0, 0.0
2, 10.0, 0.0, 0.0
3, 10.0, 10.0, 0.0
4, 0.0, 10.0, 0.0
*Element, type=S4R
1, 1, 2, 3, 4
*Material, name=Steel
*Elastic
210000.0, 0.3
*Density
7.85e-9
*Shell Section, elset=AllElements, material=Steel
0.01
*Elset, elset=AllElements
1
*Boundary
1, 1, 6, 0.0
2, 1, 6, 0.0
*Cload
4, 3, -1000.0
""")
        self.temp_file.close()
        
        # Parse the temporary file
        parser = AbaqusParser()
        self.parser_data = parser.parse(self.temp_file.name)
        
        # Create the converter
        self.converter = AbaqusToOpenSeesConverter(self.parser_data)
    
    def tearDown(self):
        # Clean up the temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_convert(self):
        """Test the conversion process."""
        script = self.converter.convert()
        
        # Check for essential OpenSeesPy components in the script
        self.assertIn("from openseespy.opensees import *", script)
        self.assertIn("wipe()", script)
        self.assertIn("model('basic', '-ndm', 3, '-ndf', 6)", script)
        
        # Check that nodes are properly converted
        self.assertIn("node(1, 0.0, 0.0, 0.0)", script)
        self.assertIn("node(4, 0.0, 10.0, 0.0)", script)
        
        # Check that material is properly converted
        self.assertIn("nDMaterial('ElasticIsotropic'", script)
        self.assertIn("210000", script)
        self.assertIn("0.3", script)
        
        # Check that element is properly converted
        self.assertIn("element('ShellMITC4'", script)
        
        # Check that boundary conditions are properly converted
        self.assertIn("fix(1, ", script)
        
        # Check that load is properly converted
        self.assertIn("load(4, ", script)
        self.assertIn("-1000.0", script)
        
        # Check that analysis setup is included
        self.assertIn("analysis('Static')", script)
    
    def test_convert_utility_function(self):
        """Test the convert utility function."""
        # Test conversion to string
        script = convert(self.temp_file.name, return_string=True)
        self.assertIsInstance(script, str)
        self.assertIn("from openseespy.opensees import *", script)
        
        # Test saving to file
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.py').name
        convert(self.temp_file.name, output_file)
        
        # Check that the output file exists and contains the script
        self.assertTrue(os.path.exists(output_file))
        with open(output_file, 'r') as f:
            content = f.read()
        self.assertIn("from openseespy.opensees import *", content)
        
        # Clean up output file
        if os.path.exists(output_file):
            os.unlink(output_file)

if __name__ == '__main__':
    unittest.main()