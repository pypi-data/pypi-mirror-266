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

    def check_dir_exists(self, path: str):
        if self.logger:
            self.logger.info(f"[Precondition Verifier] Checking Directory: {path}")
        else:
            pass
        if not path:
            if self.logger:
                self.logger.critical("[Precondition Verifier] Path is Required!", module="Precondition Verifier")
            else:
                pass
            raise ValueError("Path is Required!")
        else:
            try:
                path = pathlib.Path(path)
                if not path.exists():
                    if self.logger:
                        self.logger.error(f"[Precondition Verifier] Path Not Found: {path}", module="Precondition Verifier")
                    else:
                        raise FileNotFoundError(f"Path Not Found: {path}")
                if not path.is_dir():
                    if self.logger:
                        self.logger.error(f"[Precondition Verifier] Path is not a directory: {path}")
                    else:
                        raise ValueError(f"Path is not a directory: {path}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"[Precondition Verifier] Error Reading Path: {e}")
                raise ValueError(f"Error Reading Path: {e}")
        if self.logger:
            self.logger.info(f"[Precondition Verifier] Directory Exists: {path}")
        else:
            pass
        path = str(path)
        return path
    
    def check_file_exists(self, path: str):
        if self.logger:
            self.logger.info(f"[Precondition Verifier] Checking File: {path}")
        else:
            pass
        if not path:
            if self.logger:
                self.logger.critical("[Precondition Verifier] Path is Required!")
            else:
                pass
            raise ValueError("Path is Required!")
        try:
            path = pathlib.Path(path)
            if not path.exists():
                if self.logger:
                    self.logger.error(f"[Precondition Verifier] File Not Found: {path}")
                else:
                    raise FileNotFoundError(f"File Not Found: {path}")
            if not path.is_file():
                if self.logger:
                    self.logger.error(f"[Precondition Verifier] Path is not a file: {path}")
                else:
                    raise ValueError(f"Path is not a file: {path}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"[Precondition Verifier] Error Reading: {e}")
            else:
                pass
            raise ValueError(f"Error Reading: {e}")
        if self.logger:
            self.logger.info(f"[Precondition Verifier] File Exists: {path}")
        else:
            pass
        path = str(path)
        return path

    def create_path(self, path: str):
        if self.logger:
            self.logger.info(f"[Precondition Verifier] Creating Path: {path}")
        else:
            pass
        try:
            path = pathlib.Path(path)
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            if self.logger:
                self.logger.error(f"[Precondition Verifier] Error Creating Path: {e}")
            else:
                pass
            raise ValueError(f"Error Creating Path: {e}")
        if self.logger:
            self.logger.info(f"[Precondition Verifier] Path Created: {path}")
        else:
            pass
        path = str(path)
        return path
    
if __name__ == "__main__":
    preconditions = Preconditions(logger=Logger("test", verbose=True))