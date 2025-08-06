#!/usr/bin/env python3
"""
Development setup script for PySeesAbq.

This script helps set up the development environment and run common tasks.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔧 {description}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def install_dev():
    """Install package in development mode."""
    return run_command([sys.executable, "-m", "pip", "install", "-e", ".[dev]"], 
                      "Installing package in development mode")


def run_tests():
    """Run the test suite."""
    return run_command([sys.executable, "-m", "pytest", "tests/", "-v"], 
                      "Running test suite")


def format_code():
    """Format code with black."""
    success = True
    success &= run_command([sys.executable, "-m", "black", "pyseesabq/"], 
                          "Formatting code with black")
    success &= run_command([sys.executable, "-m", "black", "tests/"], 
                          "Formatting tests with black")
    return success


def lint_code():
    """Lint code with flake8."""
    return run_command([sys.executable, "-m", "flake8", "pyseesabq/"], 
                      "Linting code with flake8")


def type_check():
    """Run type checking with mypy."""
    return run_command([sys.executable, "-m", "mypy", "pyseesabq/"], 
                      "Type checking with mypy")


def build_package():
    """Build the package."""
    success = True
    success &= run_command([sys.executable, "-m", "pip", "install", "build"], 
                          "Installing build tools")
    success &= run_command([sys.executable, "-m", "build"], 
                          "Building package")
    return success


def clean():
    """Clean build artifacts."""
    import shutil
    
    print("\n🧹 Cleaning build artifacts")
    
    # Remove build directories
    for dir_name in ["build", "dist", "*.egg-info"]:
        for path in Path(".").glob(dir_name):
            if path.is_dir():
                print(f"Removing {path}")
                shutil.rmtree(path)
    
    # Remove __pycache__ directories
    for path in Path(".").rglob("__pycache__"):
        if path.is_dir():
            print(f"Removing {path}")
            shutil.rmtree(path)
    
    # Remove .pyc files
    for path in Path(".").rglob("*.pyc"):
        print(f"Removing {path}")
        path.unlink()
    
    print("✅ Cleanup completed")
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="PySeesAbq development tools")
    parser.add_argument("command", choices=[
        "install", "test", "format", "lint", "typecheck", "build", "clean", "all"
    ], help="Command to run")
    
    args = parser.parse_args()
    
    print(f"🚀 PySeesAbq Development Tools")
    print(f"Command: {args.command}")
    
    success = True
    
    if args.command == "install":
        success = install_dev()
    elif args.command == "test":
        success = run_tests()
    elif args.command == "format":
        success = format_code()
    elif args.command == "lint":
        success = lint_code()
    elif args.command == "typecheck":
        success = type_check()
    elif args.command == "build":
        success = build_package()
    elif args.command == "clean":
        success = clean()
    elif args.command == "all":
        success = True
        success &= install_dev()
        success &= format_code()
        success &= lint_code()
        success &= run_tests()
        success &= build_package()
    
    if success:
        print(f"\n✅ {args.command.capitalize()} completed successfully!")
    else:
        print(f"\n❌ {args.command.capitalize()} failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
