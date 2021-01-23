"""

"""


# imports
from typing import Dict
import xml.etree.ElementTree as et

from files.file import SharedFile, BinaryFile
from formats import XML_Manager, Binary_Manager
from formats.runtime.v1.rtpc_v1 import RTPC_v1
from misc.errors import MissingInvalidXMLVersion, UnsupportedXMLVersion, UnsupportedVersion


# class
class RTPC_XML_Manager(XML_Manager):
    VERSIONS: Dict = {
        1: RTPC_v1
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_path: str = kwargs.get("file_path")
        self.xml_root: et.Element = kwargs.get("xml_root")
        self.xml_version: int = kwargs.get("xml_version", 0)
        self.db_path: str = kwargs.get("db_path", "")
    
    def preprocess(self, **kwargs):
        super().preprocess(**kwargs)
        if self.xml_version == 0:
            xml_version_str: str = self.xml_root.attrib.get("version", "")
            try:
                xml_version: int = int(xml_version_str)
            except ValueError:
                raise MissingInvalidXMLVersion(xml_version_str, list(self.VERSIONS.keys()), self.file_path)
            self.xml_version = xml_version
        
        if self.xml_version not in self.VERSIONS:
            raise UnsupportedXMLVersion(str(self.xml_version), list(self.VERSIONS.keys()), self.file_path)
    
    def do(self, **kwargs):
        super().do(**kwargs)
        file: SharedFile = self.VERSIONS[self.xml_version](self.file_path, self.db_path)
        file.load_converted()


class RTPC_Manager(Binary_Manager):
    VERSIONS: Dict = {
        1: RTPC_v1
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_path: str = kwargs.get("file_path")
        self.db_path: str = kwargs.get("db_path", "")
        self.version: int = 0
    
    def load_header(self):
        f: BinaryFile = BinaryFile(open(self.file_path, "rb"))
        four_cc: bytes = f.read_strl(4)
        self.version = f.read_u32()
    
    def preprocess(self, **kwargs):
        super().preprocess(**kwargs)
        if self.version not in self.VERSIONS.keys():
            raise UnsupportedVersion(str(self.version), list(self.VERSIONS.keys()), self.file_path)
    
    def do(self, **kwargs):
        super().do(**kwargs)
        file: SharedFile = self.VERSIONS[self.version](self.file_path, self.db_path)
        file.load()
        file.export()
