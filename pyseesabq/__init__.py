"""
PySeesAbq - Internal company tool for converting Abaqus .inp files to OpenSeesPy Python scripts.

CONFIDENTIAL AND PROPRIETARY
This software contains confidential and proprietary information of RAPID-CLIO.
Unauthorized copying, distribution, or use is strictly prohibited.

This package provides both a command-line interface and Python API for converting
Abaqus finite element models to OpenSeesPy format for internal company use only.
"""

__version__ = "1.0.0"
__author__ = "Omer Jauhar"
__email__ = "omer.jauhar@rapid-clio.com"
__license__ = "Proprietary"
__copyright__ = "Copyright (c) 2025 RAPID-CLIO. All Rights Reserved."

# Confidentiality notice
__confidential__ = True
__internal_use_only__ = True

from .converter import AbaqusToOpenSeesConverter
from .parser import AbaqusParser
from .core import convert, convert_file

__all__ = [
    "AbaqusToOpenSeesConverter",
    "AbaqusParser", 
    "convert",
    "convert_file",
    "__version__",
]
