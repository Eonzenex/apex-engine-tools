"""
Inline Runtime Container v1
"""


# imports
import xml.etree.ElementTree as et
import os.path
import sqlite3 as sql

from misc import utils
from files.file import SharedFile, BinaryFile
from formats.inline_runtime.v1.irtpc_v1_types import IRT_Root_v4, IRT_Header_v1


# class
class IRTPC_v1(SharedFile):
    def __init__(self, file_path: str = "", db_path: str = ""):
        super().__init__()
        self.version = 1
        self.container = IRT_Root_v4()
        self.header_type = IRT_Header_v1
        if db_path == "":
            self.db = os.path.abspath("./dbs/global.db")
        else:
            self.db = db_path
        if file_path != '':
            self.get_file_details(file_path)
    
    def __str__(self):
        return f"IRTPC v1: '{self.file_name}.{self.extension}'"
    
    def sort(self):
        """ Sort the container. """
        self.container.sort_objects()
    
    # io
    def deserialize(self, f: BinaryFile):
        """ Recursive containers deserialize each other. """
        conn = sql.connect(self.db)
        db_cursor = conn.cursor()
        self.container.deserialize(f, db_cursor)
    
    def export(self, file_path: str = ''):
        """ Export the file as an XML. """
        if file_path == '':
            file_path = f"{self.get_file_path_short()}.xml"
        else:
            file_path = os.path.abspath(file_path)
        root = et.Element('irtpc')
        root.attrib['extension'] = self.extension
        root.attrib['version'] = str(self.header.version_01)
        root.attrib['version_02'] = str(self.header.version_02)
        root.append(self.container.export())
        utils.indent(root)
        
        root = et.ElementTree(root)
        root.write(file_path, encoding='utf-8', xml_declaration=True)
    
    def import_(self, **kwargs):
        root = kwargs.get("root")
        
        self.header = self.header_type()
        self.header.version_01 = int(root.attrib['version'])
        self.header.version_02 = int(root.attrib['version_02'])
        self.header.container_count = utils.get_container_count(root)
        self.extension = root.attrib['extension']
        
        self.container.import_(elem=root[0])
    
    def serialize(self, file_path: str = ""):
        if file_path != "":
            self.file_name = file_path
        file_path = self.get_file_path()
        with BinaryFile(open(file_path, 'wb')) as f:
            self.container.serialize(f)
