# Contributing to PySeesAbq

Thank you for your interest in contributing to PySeesAbq! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/PySeesAbq.git
   cd PySeesAbq
   ```

2. **Install in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Run tests to verify setup**
   ```bash
   pytest tests/
   ```

## 🛠️ Development Workflow

### Code Style
- Follow PEP 8 guidelines
- Use type hints for function signatures
- Add docstrings for all public functions and classes
- Use meaningful variable names

### Code Formatting
Run before committing:
```bash
black pyseesabq/ tests/
flake8 pyseesabq/
```

### Testing
- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for good test coverage

```bash
pytest tests/ -v
pytest tests/ --cov=pyseesabq
```

### Development Script
Use the provided development script for common tasks:
```bash
python dev.py format    # Format code
python dev.py lint      # Lint code
python dev.py test      # Run tests
python dev.py all       # Run all checks
```

## 📝 How to Contribute

### Reporting Bugs
1. Check if the bug is already reported in [Issues](https://github.com/OmerJauhar/PySeesAbq/issues)
2. Create a new issue with:
   - Clear bug description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information
   - Sample .inp file if applicable

### Suggesting Features
1. Check existing feature requests in Issues
2. Create a new issue with:
   - Feature description
   - Use case and motivation
   - Proposed implementation (optional)

### Submitting Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**
   ```bash
   python dev.py all
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## 🎯 Areas for Contribution

### High Priority
- Support for additional Abaqus element types
- Advanced material models (plasticity, hyperelastic)
- Contact and interaction support
- Performance optimization for large models

### Medium Priority
- Additional analysis types (modal, dynamic)
- Better section handling
- Support for assemblies and instances
- Improved error messages

### Low Priority
- GUI interface
- Visualization capabilities
- Integration with other FE software
- Documentation improvements

## 🧪 Testing

### Test Structure
```
tests/
├── test_parser.py      # Parser functionality
├── test_converter.py   # Converter functionality
├── test_cli.py         # CLI functionality
└── test_integration.py # End-to-end tests
```

### Adding Tests
- Create test files in the `tests/` directory
- Use pytest fixtures for common setup
- Test both success and failure cases
- Include edge cases and boundary conditions

### Test Examples
```python
def test_parse_nodes():
    parser = AbaqusParser()
    # Test implementation
    assert len(parser.nodes) == expected_count

def test_convert_elements():
    # Test element conversion
    pass
```

## 📚 Documentation

### Code Documentation
- Use Google-style docstrings
- Include type hints
- Document parameters and return values
- Provide usage examples

### README Updates
- Update feature lists
- Add new CLI examples
- Update installation instructions
- Keep examples current

## 🔍 Code Review Process

### For Contributors
- Ensure CI tests pass
- Respond to reviewer feedback promptly
- Keep PRs focused and manageable
- Write clear commit messages

### For Reviewers
- Check code functionality
- Verify test coverage
- Review documentation updates
- Test locally if needed

## 📋 Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No merge conflicts
- [ ] CI passes

## 🆘 Getting Help

- **Discord/Slack**: [Link if available]
- **GitHub Discussions**: For general questions
- **Issues**: For bugs and feature requests
- **Email**: [maintainer email]

## 📄 License

By contributing to PySeesAbq, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

Thank you for contributing to PySeesAbq! 🙏
