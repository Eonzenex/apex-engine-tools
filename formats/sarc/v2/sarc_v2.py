"""
Streamed Archive v2
"""

# imports
import os.path
from typing import List
import xml.etree.ElementTree as et

from files.file import SharedFile, BinaryFile
from formats.sarc.v2.sarc_v2_types import SARC_Header_v2, SARC_Entry_v2
from misc.errors import MalformedXMLDoc, UnsupportedXMLTag, MissingInvalidXMLVersion, UnsupportedXMLVersion
import misc.utils as u


# class
class SARC_v2(SharedFile):
    XML_TAG: str = "sarc"
    
    def __init__(self, file_path: str = None):
        super().__init__()
        self.version = 2
        self.header_type = SARC_Header_v2
        self.files: List[SARC_Entry_v2] = []
        
        if file_path is not None:
            self.get_file_details(file_path)
    
    def __str__(self):
        return f"SARC_v2: {self.header.four_cc} version {self.header.version}"
    
    # io
    def load_converted(self):
        folder_path: str = self.get_file_path_short()
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
        self.serialize()
    
    def deserialize(self, file: BinaryFile):
        start_pos: int = file.tell()
        end_pos: int = start_pos + self.header.size
        index: int = 0
        while file.tell() + 12 <= end_pos:
            entry: SARC_Entry_v2 = SARC_Entry_v2()
            entry.deserialize(file)
            self.files.append(entry)
            index += 1
    
    def export(self, file_path: str = ""):
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
        
        for child in root:
            if child.tag == "file":
                entry: SARC_Entry_v2 = SARC_Entry_v2()
                entry.import_(base_path=base_path, elem=child)
                self.files.append(entry)
    
    def serialize(self, file_name: str = ""):
        if file_name != "":
            self.file_name = file_name
        file_path = f"{self.get_file_path_short()}_serial.sarc"
        with BinaryFile(open(file_path, 'wb')) as f:
            self.header.serialize(f)
            for file in self.files:
                file.serialize(f)
            self.header.write(f)
            for i, file in enumerate(self.files):
                file.write(f)
                if i+1 < len(self.files):
                    f.write_align(delim=b"\00")























