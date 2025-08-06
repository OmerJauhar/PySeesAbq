# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-06

### Added
- Initial release of PySeesAbq
- Complete Abaqus .inp file parser
- OpenSeesPy script generator
- Command-line interface with convert, info, and batch commands
- Support for nodes, elements, materials, sections, boundary conditions, and loads
- Professional error handling and logging
- Rich CLI output with progress bars and colored text
- Comprehensive test suite
- Detailed documentation and examples

### Features
- **Elements**: S4R, S4, S3, C3D8, C3D4, B31, T3D2, T2D2 and more
- **Materials**: Elastic isotropic materials with E, nu, rho
- **Boundary Conditions**: Fixed DOF constraints
- **Loads**: Concentrated nodal loads
- **Sets**: Element sets and node sets
- **Analysis**: Basic static analysis setup

### CLI Commands
- `pyseesabq convert <file.inp>` - Convert single file
- `pyseesabq batch <directory>` - Convert all .inp files in directory
- `pyseesabq info <file.inp>` - Show file information
- `pyseesabq --version` - Show version

### Python API
- `convert_file()` - High-level file conversion
- `convert()` - Get script as string
- `AbaqusParser` - Parse .inp files
- `AbaqusToOpenSeesConverter` - Generate OpenSeesPy scripts
