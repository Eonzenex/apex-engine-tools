"""
Streamed Archive v2 types
"""

# imports
import os.path
import xml.etree.ElementTree as et

from files.file import SharedHeader, BinaryFile
import misc.utils as u
from misc.errors import FileDoesNotExist, IncorrectFileSize


# class
class SARC_Header_v2(SharedHeader):
    """
    1) 4-byte header length
    2) SARC FourCC
    3) SARC version (2)
    4) SARC file contents data offset (Relative to end of header)
    """
    SARC_FOUR_CC: bytes = b"SARC"
    
    def __init__(self):
        super().__init__()
        self.length: int = 0
        self.size: int = 0
        self.base_pos: int = 0
    
    def __str__(self):
        return f"SARC_Header: {self.four_cc} version {self.version}"
    
    def deserialize(self, f: BinaryFile):
        # Measured in 4 bytes
        self.length = f.read_u32() * 4
        self.four_cc = f.read_strl(4)
        if self.four_cc != self.SARC_FOUR_CC:
            raise ValueError(f"Block magic does not match: {self.four_cc} != {self.SARC_FOUR_CC}")
        self.version = f.read_u32()
        self.size = f.read_u32()
    
    def serialize(self, f: BinaryFile):
        f.write_u32(4)
        f.write(self.SARC_FOUR_CC)
        f.write_u32(2)
        self.base_pos = f.tell()
        f.write(b"FFFF")
    
    def write(self, f: BinaryFile):
        new_pos: int = f.tell()
        f.seek(self.base_pos)
        # Offset accounts for len(header), code takes the pos of len(header) - 4
        f.write_u32(new_pos - (self.base_pos + 4))
        f.seek(new_pos)


class SARC_Entry_v2:
    """
    1) Path length including alignment
    2) File path
    3) Data offset (If 0, file is a reference to another global file)
    4) File size
    """
    def __init__(self):
        self.name_length: int = 0
        self.name: str = ""
        self.data_offset: int = 0
        self.size: int = 0
        self.data: bytes = b""
        self.ref: bool = False

        self.base_path: str = ""
        self.base_pos: int = 0
    
    def deserialize(self, f: BinaryFile):
        self.name_length = f.read_u32()
        rel_file_path: bytes = f.read_strl(self.name_length)
        self.name = rel_file_path.strip(b"\00").decode("utf-8")
        self.data_offset = f.read_u32()
        self.size = f.read_u32()
        
        if self.data_offset == 0:
            self.ref = True
        else:
            original_pos: int = f.tell()
            f.seek(self.data_offset)
            self.data = f.read(self.size)
            f.seek(original_pos)
    
    def export(self, folder_path: str):
        file_path: str = os.path.join(folder_path, self.name)
        full_folder_path: str = os.path.split(file_path)[0]
        os.makedirs(full_folder_path, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(self.data)
    
    def import_(self, **kwargs):
        self.base_path = kwargs.get("base_path")
        elem: et.Element = kwargs.get("elem")
        self.name = elem.text

        file_path: str = os.path.join(self.base_path, self.name)
        if not os.path.exists(file_path):
            raise FileDoesNotExist(file_path)
        
        # Name length is temporary and suspected to include the align that occurs at the end of the string write
        self.name_length = len(self.name)
        self.ref = bool(int(elem.attrib.get("ref", "1")))
        self.size = int(elem.attrib.get("size", "0"))
        if not self.ref:
            with open(os.path.join(self.base_path, self.name), "rb") as f:
                self.data = f.read()
            file_size: int = len(self.data)
            if self.size != file_size:
                raise IncorrectFileSize(file_size, self.size, file_path)
            self.size = len(self.data)
    
    def serialize(self, f: BinaryFile):
        """
        Old formula. Suspect that +4 is not required as it shouldn't change the 4-byte align.
        str_end_aligned: int = u.align(f.tell() + 4 + len(self.name))
        """
        str_end_aligned: int = u.align(f.tell() + len(self.name))
        f.write_u32(len(self.name) + str_end_aligned)
        f.write_strl(self.name)
        f.write_align(delim=b"\00")
        if self.ref:
            f.write_u32(0)
        else:
            self.base_pos = f.tell()
            f.write(b"FFFF")
        f.write_u32(self.size)
    
    def write(self, f: BinaryFile):
        if not self.ref:
            new_pos: int = f.tell()
            f.seek(self.base_pos)
            f.write_u32(new_pos)
            f.seek(new_pos)
            f.write(self.data)
        
