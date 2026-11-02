"""Convenient local entry point; install Pillow first if it is unavailable."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from shorts_editor.cli import main

if __name__ == "__main__":
    main()

