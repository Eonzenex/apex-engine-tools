"""
Streamed Archive v2
"""

# imports
import io
import os.path
from typing import List
import xml.etree.ElementTree as et

from files.file import BinaryFile
from formats.sarc.sarc import SARC
from formats.sarc.v2.sarc_v2_types import SARC_Header_v2, SARC_Entry_v2
from misc.errors import MalformedXMLDoc, UnsupportedXMLTag, MissingInvalidXMLVersion, UnsupportedXMLVersion
import misc.utils as u


# class
# TODO: Create a parent for SARC processors
class SARC_v2(SARC):
    """
    1) Header
    2) File entry headers
    4) Files with alignment between them
    """
    XML_TAG: str = "sarc"
    
    def __init__(self, file_path: str = ""):
        super().__init__()
        self.version = 2
        self.header_type = SARC_Header_v2
        self.files: List[SARC_Entry_v2] = []
        
        if file_path != "":
            self.get_file_details(file_path)
    
    def __str__(self):
        return f"SARC_v2: {self.header.four_cc} version {self.header.version}"
    
    # io
    def load_converted(self, **kwargs) -> bytes:
        folder_path: str = self.get_file_path_short()
        export_sarc: bool = kwargs.get("export_sarc", False)
        xml_path: str = f"{folder_path}\\@files.xml"

        try:
            xml_file: et.ElementTree = et.parse(xml_path)
        except et.ParseError:
            raise MalformedXMLDoc(self.file_name, xml_path)
        xml_root: et.Element = xml_file.getroot()
        
        if xml_root.tag != self.XML_TAG:
            raise UnsupportedXMLTag(xml_root.tag, self.XML_TAG, xml_path)
    
        xml_version_str: str = xml_root.attrib.get("version", "")
        try:
            xml_version_int: int = int(xml_version_str)
        except ValueError:
            raise MissingInvalidXMLVersion(xml_version_str, str(self.version), xml_path)
    
        if xml_version_int != self.version:
            raise UnsupportedXMLVersion(xml_version_str, str(self.version), xml_path)
    
        self.import_(root=xml_root, base_path=folder_path)
        return self.serialize(export_sarc=export_sarc)
    
    def load_stream(self, **kwargs):
        f: BinaryFile = kwargs.get("file")
        self.header = self.header_type()
        self.header.deserialize(f)
        
        self.deserialize(file=f)
    
    def deserialize(self, **kwargs):
        f: BinaryFile = kwargs.get("file")
        start_pos: int = f.tell()
        end_pos: int = start_pos + self.header.size
        index: int = 0
        while f.tell() + 12 <= end_pos:
            entry: SARC_Entry_v2 = SARC_Entry_v2()
            entry.deserialize(f)
            self.files.append(entry)
            index += 1
    
    def export(self, **kwargs):
        file_path: str = kwargs.get("file_path", "")
        if file_path == "":
            file_path = self.get_file_path_short()
        else:
            file_path = os.path.abspath(file_path)
        
        os.makedirs(file_path, exist_ok=True)
        root = et.Element("sarc")
        root.attrib["extension"] = self.extension
        root.attrib["version"] = str(self.header.version)
        root.attrib["filename"] = self.file_name
        
        # export each file
        for entry in self.files:
            entry.export(file_path)
            elem = et.SubElement(root, "file")
            elem.attrib["ref"] = str(int(entry.ref))
            elem.attrib["size"] = str(entry.size)
            elem.text = entry.name
        
        # keep track of all the files to pack
        u.indent(root)
        xml_path: str = os.path.join(file_path, "@files.xml")
        etree = et.ElementTree(root)
        etree.write(xml_path, encoding='utf-8', xml_declaration=True)
    
    def import_(self, **kwargs):
        root: et.Element = kwargs.get("root")
        base_path: str = kwargs.get("base_path")
    
        self.header = self.header_type()
        self.header.version = int(root.attrib['version'])
        self.file_name = root.attrib['filename']
        self.extension = root.attrib['extension']
        
        for child in root:
            if child.tag == "file":
                entry: SARC_Entry_v2 = SARC_Entry_v2()
                entry.import_(base_path=base_path, elem=child)
                self.files.append(entry)
    
    def serialize(self, **kwargs) -> bytes:
        file_name: str = kwargs.get("file_name", "")
        export_sarc: bool = kwargs.get("export_sarc", False)
        if file_name != "":
            self.file_name = file_name
        file_path = f"{self.get_file_path_short()}_serial.sarc"
        
        f: BinaryFile = BinaryFile(io.BytesIO(b""))
        self.header.serialize(f)
        for file in self.files:
            file.serialize(f)
        self.header.write(f)
        for i, file in enumerate(self.files):
            file.write(f)
            if i+1 < len(self.files):
                f.write_align(delim=b"\00")
        
        if export_sarc:
            f.seek(0)
            with open(file_path, "wb") as sarc_file:
                sarc_file.write(f.read_all())
        
        return f.read_all()





