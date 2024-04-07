# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module for checking and updating environment's state/status file(s).

"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Union

from .paths import get_env_path

logger = logging.getLogger(__name__)


def install_status_codes(slug: str) -> Dict[str, Union[int, str]]:
    """Return environment's install status codes."""

    def read_from_json(file_path: Path) -> Dict[str, Union[int, str]]:
        try:
            with file_path.open("r", encoding="utf-8") as file:
                json_data = json.load(file)
                return json_data.get("install", {})
        except (IOError, json.JSONDecodeError) as err:
            logger.error("Error reading state.json: %s", err)
            return {}

    def read_from_txt(file_path: Path) -> Dict[str, Union[int, str]]:
        data = {}
        try:
            with file_path.open("r", encoding="utf-8") as file:
                lines = file.readlines()
                for line in lines:
                    key, value = line.split(":", 1)
                    if key in ["complete", "success"]:
                        data[key] = int(value.strip())
                    elif key == "message":
                        data[key] = value.strip()
        except IOError as err:
            logger.error("Error reading install_status.txt: %s", err)
        return data

    slug_path = get_env_path(slug)
    status_json_path = slug_path / "state.json"
    status_txt_path = slug_path / "install_status.txt"

    data = {"complete": 1, "success": 1, "message": ""}

    if status_json_path.is_file():
        data.update(read_from_json(status_json_path))
    elif status_txt_path.is_file():
        data.update(read_from_txt(status_txt_path))

    return data


def update_install_status(
    slug_path: Union[str, Path], complete: int, success: int, message: Optional[str] = None
) -> None:
    """Update environment's install status values in a JSON file.
    Truth table values: 0 = False, 1 = True, -1 = Unknown
    """
    message = message.replace("\n", " ") if message else ""

    # Convert slug_path to Path if it's not already
    slug_path = Path(slug_path) if isinstance(slug_path, str) else slug_path
    state_json_path = slug_path / "state.json"

    data = {"install": {}}

    # Read existing data if file exists
    if state_json_path.exists():
        # r+ mode for reading and writing
        with state_json_path.open("r+", encoding="utf-8") as file:
            try:
                data = json.load(file)
                file.seek(0)  # Reset file position to the beginning
            except json.JSONDecodeError as err:
                # Keep default data if JSON is invalid
                logger.error("Error opening state.json: %s", err)

            # Update the data
            data["install"]["complete"] = complete
            data["install"]["success"] = success
            data["install"]["message"] = message

            # Write updated data back to state.json
            json.dump(data, file, indent=2, ensure_ascii=False)
            file.truncate()  # Remove leftover data
    else:
        # File doesn't exist, just create a new one with the data
        data["install"] = {
            "complete": complete,
            "success": success,
            "message": message,
        }
        with state_json_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
