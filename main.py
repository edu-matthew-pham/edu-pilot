#!/usr/bin/env python

import os.path
import sys

def get_user_choice():
    while True:
        choice = input("Choose mode (CLI/GUI): ").strip().lower()
        if choice in ['cli', 'gui']:
            return choice
        print("Invalid choice. Please enter 'CLI' or 'GUI'.")

try:
    # Get user's choice
    mode = get_user_choice()

    # Choose between CLI and GUI based on user input
    if mode == 'gui':
        from edu.gui.main import run_pythagora
    else:
        from edu.cli.main import run_pythagora
except ImportError as err:
    pythagora_root = os.path.dirname(__file__)
    venv_path = os.path.join(pythagora_root, "venv")
    requirements_path = os.path.join(pythagora_root, "requirements.txt")
    if sys.prefix == sys.base_prefix:
        venv_python_path = os.path.join(venv_path, "scripts" if sys.platform == "win32" else "bin", "python")
        print(f"Python environment for Pythagora is not set up: module `{err.name}` is missing.", file=sys.stderr)
        print(f"Please create Python virtual environment: {sys.executable} -m venv {venv_path}", file=sys.stderr)
        print(
            f"Then install the required dependencies with: {venv_python_path} -m pip install -r {requirements_path}",
            file=sys.stderr,
        )
    else:
        print(
            f"Python environment for Pythagora is not completely set up: module `{err.name}` is missing",
            file=sys.stderr,
        )
        print(
            f"Please run `{sys.executable} -m pip install -r {requirements_path}` to finish Python setup, and rerun Pythagora.",
            file=sys.stderr,
        )
    sys.exit(255)

sys.exit(run_pythagora())
