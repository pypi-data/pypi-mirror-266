# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module for efficient multi-threaded copying and removal of files and directories.

"""

import shutil
import threading
from pathlib import Path
from typing import List, Optional

from .exceptions import UnknownFileSystemObjectError


class FileManager:
    """Class for efficient multi-threaded copying and removal of files and directories."""

    def __init__(self):
        self._counter = 0

    def counter(self) -> int:
        """Return the number of threads invoked."""
        return self._counter

    def reset_counter(self):
        """Reset the counter to 0."""
        self._counter = 0

    def copy_async(self, src_path: Path, dst_path: Path):
        """Thread function for copying files and directories."""
        try:
            if src_path.is_dir():
                shutil.copytree(src_path, dst_path)
            elif src_path.is_file():
                shutil.copy(src_path, dst_path)
            else:
                pass
        except (FileExistsError, FileNotFoundError):
            pass

    def copy_tree(self, src_path: Path, dst_path: Path, skiplst: Optional[List[str]] = None):
        """Initiates threaded copying of files and directories."""
        skiplst = skiplst or []
        dirs_and_files_iter = [p for p in src_path.iterdir() if p.name not in skiplst]

        for dir_file in dirs_and_files_iter:
            srcp = dir_file
            dstp = dst_path / dir_file.name
            if dir_file.is_file():
                thread = threading.Thread(target=self.copy_async, args=(srcp, dstp))
                thread.daemon = True
                thread.start()
            elif dir_file.is_dir():
                dstp.mkdir(exist_ok=True)
                self.copy_tree(srcp, dstp)
            elif dir_file.is_symlink():
                linkto = srcp.readlink()
                dstp.symlink_to(linkto)
            else:
                raise UnknownFileSystemObjectError(
                    f"The path '{srcp}' is not a file, directory, or symbolic link."
                )

    def remove_async(self, path: Path):
        """Thread function for removing files, directories, and symbolic links."""
        try:
            self._counter += 1
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            elif path.is_file() or path.is_symlink():
                path.unlink()
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    def remove_tree(self, src_path: Path):
        """Initiates threaded removal of files, directories, and symbolic links."""
        if not src_path.is_dir():
            return

        for dir_file in src_path.iterdir():
            if dir_file.is_file() or dir_file.is_symlink() or dir_file.is_dir():
                thread = threading.Thread(target=self.remove_async, args=(dir_file,))
                thread.daemon = True
                thread.start()

        # Finally, remove the src_path directory itself in a new thread
        thread = threading.Thread(target=self.remove_async, args=(src_path,))
        thread.daemon = True
        thread.start()

    def join_threads(self):
        """Wait for all threads to finish."""
        main_thread = threading.current_thread()
        for thread in threading.enumerate():
            if thread is main_thread:
                continue
            thread.join()
