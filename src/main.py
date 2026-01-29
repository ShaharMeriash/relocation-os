#!/usr/bin/env python3
"""
Relocation OS - Main Entry Point
"""

import sys
from pathlib import Path

# Add the src directory to Python's path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from menu import run_menu


def main():
    """Main function - launches the interactive menu"""
    run_menu()


if __name__ == "__main__":
    main()