from yosemite_tools.modules.logger import Logger

import pathlib
from typing import Optional


class Preconditions:
    def __init__(self, logger : Optional[Logger] = None):
        self.logger = None
        if logger:
            self.logger = logger
        else:
            pass
        pass

    @staticmethod
    def check_dir_exists(self, path: str):
        if self.logger:
            self.logger.info(f"[Precondition Verifier] Checking Directory: {path}")
        if not path:
            if self.logger:
                self.logger.critical("[Precondition Verifier] Path is Required!")
            raise ValueError("Path is Required!")
        else:
            try:
                path = pathlib.Path(path)
                if not path.exists():
                    if self.logger:
                        self.logger.error(f"[Precondition Verifier] Path Not Found: {path}")
                    raise FileNotFoundError(f"Path Not Found: {path}")
                if not path.is_dir():
                    if self.logger:
                        self.logger.error(f"[Precondition Verifier] Path is not a directory: {path}")
                    raise ValueError(f"Path is not a directory: {path}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"[Precondition Verifier] Error Reading Path: {e}")
                raise ValueError(f"Error Reading Path: {e}")
        self.logger.info(f"[Precondition Verifier] Directory Exists: {path}")
        return path

    @staticmethod
    def check_file_exists(self, path: str):
        if self.logger:
            self.logger.info(f"[Precondition Verifier] Checking File: {path}")
        if not path:
            if self.logger:
                self.logger.critical("[Precondition Verifier] Path is Required!")
            raise ValueError("Path is Required!")
        try:
            path = pathlib.Path(path)
            if not path.exists():
                if self.logger:
                    self.logger.error(f"[Precondition Verifier] File Not Found: {path}")
                raise FileNotFoundError(f"File Not Found: {path}")
            if not path.is_file():
                if self.logger:
                    self.logger.error(f"[Precondition Verifier] Path is not a file: {path}")
                raise ValueError(f"Path is not a file: {path}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"[Precondition Verifier] Error Reading: {e}")
            raise ValueError(f"Error Reading: {e}")
        self.logger.info(f"[Precondition Verifier] File Exists: {path}")
        return path

    @staticmethod
    def create_path(self, path: str):
        if self.logger:
            self.logger.info(f"[Precondition Verifier] Creating Path: {path}")
        try:
            path = pathlib.Path(path)
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            if self.logger:
                self.logger.error(f"[Precondition Verifier] Error Creating Path: {e}")
            raise ValueError(f"Error Creating Path: {e}")
        self.logger.info(f"[Precondition Verifier] Path Created: {path}")
        return path