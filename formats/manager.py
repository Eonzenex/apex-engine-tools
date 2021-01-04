"""
TODO
"""


# imports
import xml.etree.ElementTree as et
import os.path
from typing import Dict, List

from files.file import SharedFile, SharedHeader
from formats.inline_runtime.v1.irtpc_v1 import IRTPC_v1
from formats.inline_runtime.v1.irtpc_v1_types import IRT_Header_v1
from formats.runtime.v1.rtpc_v1 import RTPC_v1
from formats.runtime.v1.rtpc_v1_types import RT_Header_v1
from misc.errors import UnsupportedXMLTag, MalformedXMLDoc, MissingInvalidXMLVersion, UnsupportedXMLVersion


# XML classes
class XML_Manager:
	VERSIONS: Dict = {}
	
	def __init__(self, **kwargs):
		pass
	
	def preprocess(self, **kwargs):
		pass
	
	def do(self, **kwargs):
		self.preprocess()


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
		file.load_xml()


class IRTPC_XML_Manager(RTPC_XML_Manager):
	VERSIONS: Dict = {
		1: IRTPC_v1
	}


# Binary classes
class Binary_Manager:
	VERSIONS: Dict = {}
	
	def __init__(self, **kwargs):
		pass
	
	def preprocess(self, **kwargs):
		pass
	
	def do(self, **kwargs):
		self.preprocess()


# functions
def manage_xml(file_path: str, db_path: str):
	""" Manage XML files and process them. """
	XML_TAGS: List = ["rtpc", "irtpc"]
	base_path, filename = os.path.split(file_path)
	
	try:
		xml_file: et.ElementTree = et.parse(file_path)
	except et.ParseError:
		raise MalformedXMLDoc(filename, file_path)
		
	xml_root: et.Element = xml_file.getroot()
	tag: str = xml_root.tag
	
	if tag not in XML_TAGS:
		raise UnsupportedXMLTag(tag, XML_TAGS, file_path)
	
	xml_manage: XML_Manager = XML_Manager()
	if tag == "rtpc":
		xml_manage = RTPC_XML_Manager(file_path=file_path, xml_root=xml_root, db_path=db_path)
	elif tag == "irtpc":
		xml_manage = IRTPC_XML_Manager(file_path=file_path, xml_root=xml_root, db_path=db_path)
	xml_manage.do()


def manage_binary(file_path: str, db_path: str):
	""" Manage binary files and process them. """
	FOUR_CC: Dict = {
		RT_Header_v1().four_cc: RTPC_v1
	}
	base_path, filename = os.path.split(file_path)
	pre_file: SharedFile = SharedFile(file_path)
	pre_file.get_header()
	
	if pre_file.header.four_cc not in FOUR_CC:
		file: SharedFile = IRTPC_v1(file_path, db_path)
	else:
		file: SharedFile = FOUR_CC[pre_file.header.four_cc](file_path, db_path)
