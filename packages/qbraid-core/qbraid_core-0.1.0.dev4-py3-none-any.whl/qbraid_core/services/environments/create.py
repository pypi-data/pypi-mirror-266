# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module for creating custom environments.

"""
import logging
import subprocess
import sys
from pathlib import Path
from typing import Union

from qbraid_core.system import replace_str

from .state import update_install_status

logger = logging.getLogger(__name__)


def create_local_venv(slug_path: Union[str, Path], prompt: str) -> None:
    """Create virtual environment and swap PS1 display name."""
    try:
        # Ensure slug_path is a Path object
        slug_path = Path(slug_path)
        venv_path = slug_path / "pyenv"
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)

        # Determine the correct directory for activation scripts based on the operating system
        if sys.platform == "win32":
            scripts_path = venv_path / "Scripts"
            activate_files = ["activate.bat", "Activate.ps1"]
        else:
            scripts_path = venv_path / "bin"
            activate_files = ["activate", "activate.csh", "activate.fish"]

        for file in activate_files:
            file_path = scripts_path / file
            replace_str("(pyenv)", f"({prompt})", str(file_path))

        update_install_status(slug_path, 1, 1)
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.error("Error creating virtual environment: %s", err)
        update_install_status(slug_path, 1, 0, message=str(err))
