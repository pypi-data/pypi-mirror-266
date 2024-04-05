# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

# pylint: skip-file

"""
Script to verify qBraid copyright file headers

"""
import os
import sys
from typing import List, Optional

# ANSI escape codes
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

DEFAULT_HEADER = """# Copyright (c) 2024, qBraid Development Team
# All rights reserved.
"""

DEFAULT_HEADER_GPL = """# Copyright (C) 2024 qBraid
#
# This file is part of the qBraid-SDK
#
# The qBraid-SDK is free software released under the GNU General Public License v3
# or later. You can redistribute and/or modify it under the terms of the GPL v3.
# See the LICENSE file in the project root or <https://www.gnu.org/licenses/gpl-3.0.html>.
#
# THERE IS NO WARRANTY for the qBraid-SDK, as per Section 15 of the GPL v3.
"""


def verify_headers(
    src_paths: List[str],
    header_type: str = "default",
    skip_files: Optional[List[str]] = None,
    fix: bool = False,
) -> None:
    if header_type == "default":
        header = DEFAULT_HEADER
    elif header_type == "gpl":
        header = DEFAULT_HEADER_GPL
    else:
        raise ValueError("Invalid header type")

    header_2023 = header.replace("2024", "2023")

    skip_files = skip_files or []

    failed_headers = []
    fixed_headers = []

    def should_skip(file_path: str, content: str) -> bool:
        if file_path in skip_files:
            return True

        if os.path.basename(file_path) == "__init__.py":
            return not content.strip()

        skip_header_tag = "# qbraid: skip-header"
        line_number = 0

        for line in content.splitlines():
            line_number += 1
            if 5 <= line_number <= 30 and skip_header_tag in line:
                return True
            if line_number > 30:
                break

        return False

    def replace_or_add_header(file_path: str, fix: bool = False) -> None:
        with open(file_path, "r", encoding="ISO-8859-1") as f:
            content = f.read()

        if (
            content.startswith(header)
            or content.startswith(header_2023)
            or should_skip(file_path, content)
        ):
            return

        if not fix:
            failed_headers.append(file_path)
            return

        # Add or replace the header
        lines = content.splitlines()
        first_non_comment_line_index = next(
            (i for i, line in enumerate(lines) if not line.strip().startswith("#")), None
        )

        new_content_lines = [header.rstrip("\r\n")] + (
            lines[first_non_comment_line_index:] if first_non_comment_line_index is not None else []
        )
        new_content = "\n".join(new_content_lines) + "\n"

        with open(file_path, "w", encoding="ISO-8859-1") as f:
            f.write(new_content)

        fixed_headers.append(file_path)
        return

    def process_files_in_directory(directory: str, fix: bool = False) -> int:
        count = 0
        if not os.path.isdir(directory):
            return count
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    replace_or_add_header(file_path, fix)
                    count += 1
        return count

    checked = 0
    for item in src_paths:
        if os.path.isdir(item):
            checked += process_files_in_directory(item, fix)
        elif os.path.isfile(item) and item.endswith(".py"):
            replace_or_add_header(item, fix)
            checked += 1
        else:
            failed_headers.append(item)
            print(f"Directory not found: {item}")

    if not fix:
        if failed_headers:
            for file in failed_headers:
                print(f"failed {os.path.relpath(file)}")
            num_failed = len(failed_headers)
            s1, s2 = ("", "s") if num_failed == 1 else ("s", "")
            sys.stderr.write(f"\n{num_failed} file header{s1} need{s2} updating.\n")
        else:
            print("All file header checks passed!")

    else:
        for file in fixed_headers:
            print(f"fixed {os.path.relpath(file)}")
        num_fixed = len(fixed_headers)
        num_ok = checked - num_fixed
        s_fixed = "" if num_fixed == 1 else "s"
        s_ok = "" if num_ok == 1 else "s"
        print("\nAll done! ✨ 🚀 ✨")
        print(f"{num_fixed} header{s_fixed} fixed, {num_ok} header{s_ok} left unchanged.")


def display_help() -> None:
    help_message = """
    Usage: python verify_headers.py SRC [OPTIONS] ...

    This script checks for copyright headers at the specified path.
    If no flags are passed, it will indicate which files would be
    modified without actually making any changes.
    
    Options:
    --help      Display this help message and exit.
    --fix       Adds/modifies file headers as necessary.
    """
    print(help_message)
    sys.exit(0)


if __name__ == "__main__":
    if "--help" in sys.argv:
        display_help()

    # Check if at least two arguments are provided and the first argument is not a flag
    if len(sys.argv) < 2 or sys.argv[1].startswith("--"):
        print("Usage: python verify_headers.py SRC [OPTIONS] ...")
        sys.exit(1)

    skip_files = ["qbraid_core/_version.py"]
    script_directory = os.path.dirname(os.path.abspath(__file__))
    project_directory = os.path.abspath(os.path.join(script_directory, ".."))
    skip_files = [os.path.join(project_directory, file_path) for file_path in skip_files]

    fix = "--fix" in sys.argv
    files_and_dirs = [arg for arg in sys.argv[1:] if arg != "--fix"]
    verify_headers(files_and_dirs, fix=fix, skip_files=skip_files)
