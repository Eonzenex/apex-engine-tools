"""
Runtime Container v3
"""


# imports
import xml.etree.ElementTree as et
import os.path
import sqlite3 as sql

from misc import utils
from files.file import SharedFile, BinaryFile
from formats.runtime_container.v3.rtpc_v3_types import RT_Header_v3, RT_Container_v3


# classes
class RTPC_v3(SharedFile):
	def __init__(self, file_path: str = "", db_path: str = ""):
		super().__init__()
		self.container = RT_Container_v3()
		self.header_type = RT_Header_v3
		if db_path == "":
			self.db = os.path.abspath("./databases/global.db")
		else:
			self.db = db_path
		if file_path != "":
			self.get_file_details(file_path)
	
	def __str__(self):
		return f"RTPC_v3: {self.header.magic} version {self.header.version}"
	
	def sort(self, property_recurse: bool = True, container_recurse: bool = True):
		""" Sort each container. """
		self.container.sort_properties(property_recurse)
		self.container.sort_containers(container_recurse)
	
	# io
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
		
		def get_file_info(elem: et.Element):
			self.header = self.header_type()
			self.header.version = int(elem.attrib['version'])
			self.header.container_count = utils.get_container_count(elem)
			self.extension = elem.attrib['extension']
		
		get_file_info(root)
		self.container.import_(elem=root[0])
	
	def serialize(self, file_name: str = ""):
		if file_name != "":
			self.file_name = file_name
		file_path = self.get_file_path()
		with BinaryFile(open(file_path, 'wb')) as f:
			self.header.serialize(f)
			self.container.serialize_header(f)
			self.container.serialize(f)
