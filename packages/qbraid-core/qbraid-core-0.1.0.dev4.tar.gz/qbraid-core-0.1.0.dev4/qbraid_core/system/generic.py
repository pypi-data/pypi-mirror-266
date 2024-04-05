# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module containing generic system utilities i.e. not specific to qBraid.

"""

import datetime
from pathlib import Path
from typing import Optional, Union


def replace_str(target: str, replacement: str, file_path: Union[str, Path]) -> None:
    """Replace all instances of string in file."""
    file_path = Path(file_path)

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    content = content.replace(target, replacement)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def echo_log(message: str, log_file_path: Optional[Union[Path, str]] = None) -> None:
    """Write message to log file."""
    if log_file_path is None:
        home_dir = Path.home()
        log_file_path = home_dir / ".qbraid" / "log.txt"
    else:
        log_file_path = Path(log_file_path)

    log_file_path.parent.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")
