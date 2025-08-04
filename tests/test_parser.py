"""
Tests for the Abaqus parser module.
"""
import unittest
import os
import tempfile
from abaqus2openseespy.parser import AbaqusParser

class TestAbaqusParser(unittest.TestCase):
    """Test cases for the AbaqusParser class."""
    
    def setUp(self):
        self.parser = AbaqusParser()
        
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
    
    def tearDown(self):
        # Clean up the temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_parse_nodes(self):
        """Test parsing of nodes."""
        self.parser.parse(self.temp_file.name)
        self.assertEqual(len(self.parser.nodes), 4)
        self.assertEqual(self.parser.nodes[1], [0.0, 0.0, 0.0])
        self.assertEqual(self.parser.nodes[3], [10.0, 10.0, 0.0])
    
    def test_parse_elements(self):
        """Test parsing of elements."""
        self.parser.parse(self.temp_file.name)
        self.assertEqual(len(self.parser.elements), 1)
        self.assertEqual(self.parser.elements[1]['type'], 'S4R')
        self.assertEqual(self.parser.elements[1]['nodes'], [1, 2, 3, 4])
    
    def test_parse_materials(self):
        """Test parsing of materials."""
        self.parser.parse(self.temp_file.name)
        self.assertTrue('Steel' in self.parser.materials)
        self.assertEqual(self.parser.materials['Steel']['E'], 210000.0)
        self.assertEqual(self.parser.materials['Steel']['nu'], 0.3)
        self.assertEqual(self.parser.materials['Steel']['rho'], 7.85e-9)
    
    def test_parse_section(self):
        """Test parsing of sections."""
        self.parser.parse(self.temp_file.name)
        self.assertTrue('AllElements' in self.parser.sections)
        self.assertEqual(self.parser.sections['AllElements']['material'], 'Steel')
        self.assertEqual(self.parser.sections['AllElements']['thickness'], 0.01)
    
    def test_parse_boundaries(self):
        """Test parsing of boundary conditions."""
        self.parser.parse(self.temp_file.name)
        self.assertTrue(1 in self.parser.boundaries)
        self.assertTrue(2 in self.parser.boundaries)
        self.assertEqual(self.parser.boundaries[1], [1, 1, 1, 1, 1, 1])
    
    def test_parse_loads(self):
        """Test parsing of loads."""
        self.parser.parse(self.temp_file.name)
        self.assertTrue(4 in self.parser.loads)
        self.assertEqual(self.parser.loads[4][2], -1000.0)  # Z-direction load

if __name__ == '__main__':
    unittest.main()