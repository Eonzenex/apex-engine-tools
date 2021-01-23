"""

"""


# import
from typing import Dict

from files.file import BinaryFile


# class
class XML_Manager:
    VERSIONS: Dict = {}
    
    def __init__(self, **kwargs):
        pass
    
    def preprocess(self, **kwargs):
        pass
    
    def do(self, **kwargs):
        self.preprocess()


class Binary_Manager:
    VERSIONS: Dict = {}
    
    def __init__(self, **kwargs):
        super().__init__()
        self.file_path: str = kwargs.get("file_path")
        self.version: int = 0
    
    def load_header(self):
        f: BinaryFile = BinaryFile(open(self.file_path, "rb"))
        four_cc: bytes = f.read_strl(4)
        self.version = f.read_u32()
    
    def preprocess(self, **kwargs):
        self.load_header()
    
    def do(self, **kwargs):
        self.preprocess()
