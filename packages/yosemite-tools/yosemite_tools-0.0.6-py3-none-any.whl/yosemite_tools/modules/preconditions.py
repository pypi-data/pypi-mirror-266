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
            self.logger.info(f"Checking Directory: {path}")
        else:
            pass
        if not path:
            if self.logger:
                self.logger.critical("Path is Required!", module="Precondition Verifier")
            else:
                pass
            raise ValueError("Path is Required!")
        else:
            try:
                path = pathlib.Path(path)
                if not path.exists():
                    if self.logger:
                        self.logger.error(f"Path Not Found: {path}", module="Precondition Verifier")
                    else:
                        raise FileNotFoundError(f"Path Not Found: {path}")
                if not path.is_dir():
                    if self.logger:
                        self.logger.error(f"Path is not a directory: {path}", module="Precondition Verifier")
                    else:
                        raise ValueError(f"Path is not a directory: {path}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error Reading Path: {e}", module="Precondition Verifier")
                raise ValueError(f"Error Reading Path: {e}")
        if self.logger:
            self.logger.info(f"Directory Exists: {path}", module="Precondition Verifier")
        else:
            pass
        path = str(path)
        return path
    
    def check_file_exists(self, path: str):
        if self.logger:
            self.logger.info(message=f"Checking File: {path}", module="Precondition Verifier")
        else:
            pass
        if not path:
            if self.logger:
                self.logger.critical("Path is Required!", module="Precondition Verifier")
            else:
                pass
            raise ValueError("Path is Required!")
        try:
            path = pathlib.Path(path)
            if not path.exists():
                if self.logger:
                    self.logger.error(f"File Not Found: {path}", module="Precondition Verifier")
                else:
                    raise FileNotFoundError(f"File Not Found: {path}")
            if not path.is_file():
                if self.logger:
                    self.logger.error(f"Path is not a file: {path}", module="Precondition Verifier")
                else:
                    raise ValueError(f"Path is not a file: {path}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error Reading: {e}", module="Precondition Verifier")
            else:
                pass
            raise ValueError(f"Error Reading: {e}")
        if self.logger:
            self.logger.info(f"File Exists: {path}", module="Precondition Verifier")
        else:
            pass
        path = str(path)
        return path

    def create_path(self, path: str):
        if self.logger:
            self.logger.info(f"Creating Path: {path}")
        else:
            pass
        try:
            path = pathlib.Path(path)
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error Creating Path: {e}", module="Precondition Verifier")
            else:
                pass
            raise ValueError(f"Error Creating Path: {e}")
        if self.logger:
            self.logger.info(f"Path Created: {path}", module="Precondition Verifier")
        else:
            pass
        path = str(path)
        return path
    
if __name__ == "__main__":
    preconditions = Preconditions(logger=Logger("test", verbose=True))