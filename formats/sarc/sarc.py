"""
Base SARC file to allow AAF -> Unpacked SARC
"""


# imports
from typing import Optional
import os.path

from files.file import BinaryFile, SharedHeader
from formats.sarc.v2.sarc_v2_types import SARC_Header_v2


# class
class SARC:
    def __init__(self, file_path: str = ""):
        self.header_type = SARC_Header_v2
        self.file_path: str = file_path
        self.file_name: str = ""
        self.extension: str = ""
        self.header: Optional[SharedHeader] = None
        self.version: int = 2
    
    def get_file_details(self, file_path: str):
        file_path = os.path.abspath(file_path)
        self.file_path, filename = os.path.split(file_path)
        self.file_name, self.extension = os.path.splitext(filename)
        self.extension = self.extension[1:]

    def get_header(self):
        """ Returns the file's header. """
        if "" in [self.file_path, self.file_name, self.extension]:
            raise ValueError("File information is none, need to run 'get_file_details' first")
    
        with BinaryFile(open(self.file_path, "rb")) as f:
            self.header = self.header_type()
            self.header.deserialize(f)
    
    def four_cc(self) -> bytes:
        return self.header.four_cc
    
    def get_file_path_short(self) -> str:
        return os.path.join(self.file_path, f"{self.file_name}")
    
    def load_converted(self, **kwargs):
        pass

    def deserialize(self, **kwargs):
        pass

    def export(self, **kwargs):
        pass

    def import_(self, **kwargs):
        pass

    def serialize(self, **kwargs) -> BinaryFile:
        pass
