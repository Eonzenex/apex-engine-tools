"""
Runtime Container v1
"""


# imports
import xml.etree.ElementTree as et
import os.path
import sqlite3 as sql

from misc import utils
from misc.errors import UnsupportedXMLTag, MissingInvalidXMLVersion, UnsupportedXMLVersion
from files.file import SharedFile, BinaryFile
from formats.runtime.v1.rtpc_v1_types import RT_Header_v1, RT_Container_v1


# classes
class RTPC_v1(SharedFile):
    """
    1) RTPC v1 header
    2) Container header
    3) Container content
    """
    XML_TAG: str = "rtpc"
    
    def __init__(self, file_path: str = "", db_path: str = ""):
        super().__init__()
        self.version = 1
        self.container = RT_Container_v1()
        self.header_type = RT_Header_v1
        if db_path == "":
            self.db = os.path.abspath("./dbs/global.db")
        else:
            self.db = db_path
        if file_path != "":
            self.get_file_details(file_path)
    
    def __str__(self):
        return f"RTPC_v1: {self.header.four_cc} version {self.header.version}"
    
    def sort(self, property_recurse: bool = True, container_recurse: bool = True):
        """ Sort each container. """
        self.container.sort_properties(property_recurse)
        self.container.sort_containers(container_recurse)
    
    # io
    def load_converted(self):
        if self.file_path == "" or self.file_name == "" or self.extension == "":
            raise ValueError(f"Load XML failed, missing file details.")
        
        file_path: str = self.get_file_path()
        xml_file: et.ElementTree = et.parse(file_path)
        xml_root: et.Element = xml_file.getroot()
        
        if xml_root.tag != self.XML_TAG:
            raise UnsupportedXMLTag(xml_root.tag, self.XML_TAG, file_path)
        
        xml_version_str: str = xml_root.attrib.get("version", "")
        try:
            xml_version_int: int = int(xml_version_str)
        except ValueError:
            raise MissingInvalidXMLVersion(xml_version_str, str(self.version), file_path)
        
        if xml_version_int != self.version:
            raise UnsupportedXMLVersion(xml_version_str, str(self.version), file_path)
        
        self.import_(root=xml_root)
        self.serialize()
    
    def deserialize(self, f: BinaryFile):
        """ Recursive containers deserialize each other. """
        conn = sql.connect(self.db)
        c = conn.cursor()
        self.container.deserialize(f, c)
    
    def export(self, file_path: str = ""):
        if file_path == "":
            file_path = f"{self.get_file_path_short()}.xml"
        else:
            file_path = os.path.abspath(file_path)
        rtpc = et.Element('rtpc')
        rtpc.attrib['extension'] = self.extension
        rtpc.attrib['version'] = str(self.header.version)
        rtpc.append(self.container.export())
        utils.indent(rtpc)
        
        root = et.ElementTree(rtpc)
        root.write(file_path, encoding='utf-8', xml_declaration=True)
    
    def import_(self, **kwargs):
        root = kwargs.get("root")
        
        self.header = self.header_type()
        self.header.version = int(root.attrib['version'])
        self.header.container_count = utils.get_container_count(root)
        self.extension = root.attrib['extension']
        self.container.import_(elem=root[0])
    
    def serialize(self, file_name: str = ""):
        if file_name != "":
            self.file_name = file_name
        file_path = self.get_file_path()
        with BinaryFile(open(file_path, 'wb')) as f:
            self.header.serialize(f)
            self.container.serialize_header(f)
            self.container.serialize(f)
