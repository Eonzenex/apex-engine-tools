"""
Inline Runtime Container v4 types
"""


# imports
from enum import IntEnum
from typing import Dict, Optional, List
import xml.etree.ElementTree as et

from misc import utils
from files.file import SharedHeader, BinaryFile


# utils
class IRTPC_v4_MetaType(IntEnum):
	Unassigned = 0
	UInteger32 = 1
	Float32 = 2
	String = 3
	Vec2 = 4
	Vec3 = 5
	Vec4 = 6
	Mat3x4 = 8
	Event = 14


# dicts
IRTPC_v4_MetaType_String: Dict = {
	IRTPC_v4_MetaType.Unassigned: 'none',
	IRTPC_v4_MetaType.UInteger32: 'uint32',
	IRTPC_v4_MetaType.Float32: 'f32',
	IRTPC_v4_MetaType.String: 'str',
	IRTPC_v4_MetaType.Vec2: 'vec2',
	IRTPC_v4_MetaType.Vec3: 'vec3',
	IRTPC_v4_MetaType.Vec4: 'vec4',
	IRTPC_v4_MetaType.Mat3x4: 'mat3x4',
	IRTPC_v4_MetaType.Event: 'event',
}
IRTPC_v4_String_MetaType: Dict = { v: k for k, v in IRTPC_v4_MetaType_String.items() }


# class
class IRTPC_Header_v4(SharedHeader):
	def __init__(self):
		super().__init__()
		self.length: int = 0
		self.version_01: Optional[int] = None
		self.version_02: Optional[int] = None
		self.container_count: Optional[int] = None
	
	def __str__(self):
		return f"IRTPC_Header_v4: version {self.version} container count {self.container_count}"
	
	def deserialize(self, f: BinaryFile):
		f.seek(0)
		self.version_01 = f.read_u8()
		self.version_02 = f.read_u16()
		self.container_count = f.read_u16()


class IRTPC_Base_v4:
	""" Shared Runtime Container base. """
	def deserialize(self, f: BinaryFile, db_cursor=None):
		""" Deserialize a file. Optional sqlite3.cursor object for dehashing. """
		raise NotImplementedError
	
	def export(self):
		""" Export the container as an XML. """
		raise NotImplementedError
	
	def import_(self, elem: et.Element):
		""" Import an XML and convert to this object type. """
		raise NotImplementedError
	
	def serialize(self, f: BinaryFile):
		""" Export this type as an inline RTPC file. """
		raise NotImplementedError


class IRTPC_Property_v4(IRTPC_Base_v4):
	""" A property inside an Inline Runtime Container. """
	def __init__(self):
		self.name: str = ''
		self.name_hash: int = 0
		self.raw_data: Optional[bytes] = None
		self.type: Optional[IRTPC_v4_MetaType] = None
		self.value = None
	
	def __str__(self):
		return super().__str__()
	
	def get_type_str(self) -> str:
		return IRTPC_v4_MetaType_String[self.type]
	
	# io
	def deserialize(self, f: BinaryFile, db_cursor=None):
		self.name_hash = f.read_s32()
		if db_cursor is not None:
			db_cursor.execute(f"SELECT value FROM properties "
			                  f"WHERE hash = {self.name_hash}")
			value = db_cursor.fetchone()
			if value is not None:
				self.name = value[0]
		self.type = IRTPC_v4_MetaType(f.read_u8())
		
		# Base data types
		if self.type == IRTPC_v4_MetaType.UInteger32:
			self.value = f.read_u32()
		elif self.type == IRTPC_v4_MetaType.Float32:
			self.value = f.read_f32()
		elif self.type == IRTPC_v4_MetaType.String:
			length = f.read_u16()
			self.value = f.read_strl(length)
		elif self.type == IRTPC_v4_MetaType.Vec2:
			self.value = f.read_f32(2)
		elif self.type == IRTPC_v4_MetaType.Vec3:
			self.value = f.read_f32(3)
		elif self.type == IRTPC_v4_MetaType.Vec4:
			self.value = f.read_f32(4)
		elif self.type == IRTPC_v4_MetaType.Mat3x4:
			self.value = f.read_f32(12)
		elif self.type == IRTPC_v4_MetaType.Event:
			length = f.read_u32()
			self.value = []
			for i in range(length):
				self.value.append(f.read_u32(2))
		else:
			raise ValueError(f"Invalid IRTPC_v4_MetaType: {self.type}")

	def export(self):
		elem = et.Element('property')
		elem.attrib['hash'] = utils.safe_hex(self.name_hash, fmt='i')
		elem.attrib['type'] = f"{self.get_type_str()}"
		if self.name is None:
			elem.attrib['name'] = 'none'
		else:
			elem.attrib['name'] = self.name
		
		if self.type == IRTPC_v4_MetaType.String:
			elem.text = self.value.decode('utf-8')
		elif self.type == IRTPC_v4_MetaType.Float32:
			elem.text = f"{utils.f32_fmt(self.value)}"
		elif self.type in [IRTPC_v4_MetaType.Vec2, IRTPC_v4_MetaType.Vec3, IRTPC_v4_MetaType.Vec4]:
			elem.text = ",".join(map(utils.f32_fmt, self.value))
		elif self.type == IRTPC_v4_MetaType.Mat3x4:
			by_four = [
				",".join(map(utils.f32_fmt, self.value[:3])),
				",".join(map(utils.f32_fmt, self.value[3:6])),
				",".join(map(utils.f32_fmt, self.value[6:9])),
				",".join(map(utils.f32_fmt, self.value[9:]))
			]
			elem.text = " ".join(by_four)
		elif self.type == IRTPC_v4_MetaType.Event:
			values = []
			for pair in self.value:
				fmt_e01, fmt_e02 = utils.safe_hex(pair[0]), utils.safe_hex(pair[1])
				values.append(f"{fmt_e01}={fmt_e02}")
			elem.text = ", ".join(values)
		else:
			elem.text = f"{self.value}"
		
		return elem
	
	def import_(self, elem: et.Element):
		self.name = elem.attrib['name']
		self.name_hash = elem.attrib['hash']
		self.type = IRTPC_v4_String_MetaType[elem.attrib['type']]
		value = elem.text
		if value is None:
			self.value = None
			return None
		
		if self.type == IRTPC_v4_MetaType.UInteger32:
			self.value = int(value)
		elif self.type == IRTPC_v4_MetaType.Float32:
			self.value = float(value)
		elif self.type == IRTPC_v4_MetaType.String:
			self.value = value
		elif self.type in [IRTPC_v4_MetaType.Vec2, IRTPC_v4_MetaType.Vec3, IRTPC_v4_MetaType.Vec4, IRTPC_v4_MetaType.Mat3x4]:
			if self.type in [IRTPC_v4_MetaType.Vec2, IRTPC_v4_MetaType.Vec3, IRTPC_v4_MetaType.Vec4]:
				self.value = [float(x) for x in value.split(",")]
			else:
				vectors = [x for x in value.split(" ")]
				values = []
				for vector in vectors:
					values.extend(vector.split(","))
				self.value = list(map(lambda x: float(x), values))
		elif self.type == IRTPC_v4_MetaType.Event:
			pairs = value.split(", ")
			values = []
			for pair in pairs:
				values.extend(pair.split("="))
			self.value = [int(x, 16) for x in values]
		
		return None

	def serialize(self, f: BinaryFile):
		f.write_s32(utils.safe_dehex(self.name_hash, 'i'))
		f.write_u8(self.type.value)
		if self.type == IRTPC_v4_MetaType.UInteger32:
			f.write_u32(self.value)
		elif self.type == IRTPC_v4_MetaType.Float32:
			f.write_f32(self.value)
		elif self.type == IRTPC_v4_MetaType.String:
			if self.value is None:
				f.write_u16(0)
			else:
				f.write_u16(len(self.value))
				f.write_strl(self.value)
		elif self.type in [IRTPC_v4_MetaType.Vec2, IRTPC_v4_MetaType.Vec3, IRTPC_v4_MetaType.Vec4, IRTPC_v4_MetaType.Mat3x4]:
			f.write_f32(self.value)
		elif self.type == IRTPC_v4_MetaType.Event:
			if self.value is None:
				f.write_u32(0)
			else:
				f.write_u32(len(self.value)//2)
				f.write_u32(self.value)


class IRTPC_Container_v4(IRTPC_Base_v4):
	""" A container that holds properties. """
	def __init__(self):
		self.name: str = ''
		self.name_hash: Optional[int] = None
		self.unknown_01: Optional[int] = None
		self.unknown_02: Optional[int] = None
		
		self.object_type = IRTPC_Property_v4
		self.object_count: int = 0
		self.objects: List = []
	
	def get_object(self, name_hash: int):
		""" Search for a property in the container. """
		for child in self.objects:
			if child.name_hash == name_hash:
				return child
		return None
	
	def sort_objects(self):
		""" Sort properties by name then name_hash. """
		self.objects.sort(key=lambda x: (x.name == "", x.name.lower(), x.name_hash))

	def load_objects(self, f: BinaryFile, db_cursor=None):
		objects = [self.object_type() for _ in range(self.object_count)]
		for i in range(self.object_count):
			objects[i].deserialize(f, db_cursor)
		self.objects = objects

	# io
	def deserialize(self, f: BinaryFile, db_cursor=None):
		self.name_hash = f.read_s32()
		if db_cursor is not None:
			db_cursor.execute(f"SELECT value FROM properties "
			                  f"WHERE hash = {self.name_hash}")
			value = db_cursor.fetchone()
			if value is not None:
				self.name = value[0]
		self.unknown_01 = f.read_u8()
		self.unknown_02 = f.read_u16()
		self.object_count = f.read_u16()
		self.load_objects(f, db_cursor=db_cursor)
	
	def export(self):
		elem = et.Element('container')
		elem.attrib['hash'] = utils.safe_hex(self.name_hash, 'i')
		if self.name is None:
			elem.attrib['name'] = 'none'
		else:
			elem.attrib['name'] = self.name
		
		elem.attrib['unk01'] = str(self.unknown_01)
		elem.attrib['unk02'] = str(self.unknown_02)
		
		for obj in self.objects:
			elem.append(obj.export())
		
		return elem
	
	def import_(self, elem: et.Element):
		self.name_hash = elem.attrib['hash']
		self.unknown_01 = int(elem.attrib['unk01'])
		self.unknown_02 = int(elem.attrib['unk02'])
		self.object_count = utils.get_container_count(elem)
		
		self.objects = [self.object_type() for _ in elem]
		for i, child in enumerate(elem):
			self.objects[i].import_(child)
	
	def serialize(self, f: BinaryFile):
		f.write_s32(utils.safe_dehex(self.name_hash, 'i'))
		f.write_u8(self.unknown_01)
		f.write_u16(self.unknown_02)
		f.write_u16(self.object_count)
		for child in self.objects:
			child.serialize(f)


class IRTPC_Root_v4(IRTPC_Container_v4):
	""" A container that holds containers. """
	def __init__(self):
		super().__init__()
		self.object_type = IRTPC_Container_v4
	
	def sort_objects(self):
		""" Sort the objects. """
		for obj in self.objects:
			obj.sort_objects()
	
	# io
	def deserialize(self, f: BinaryFile, db_cursor=None):
		self.unknown_01 = f.read_u8()
		self.unknown_02 = f.read_u16()
		self.object_count = f.read_u16()
		self.load_objects(f, db_cursor=db_cursor)
	
	def export(self):
		elem = et.Element('root')
		elem.attrib['unk01'] = str(self.unknown_01)
		elem.attrib['unk02'] = str(self.unknown_02)
		
		for obj in self.objects:
			elem.append(obj.export())
		
		return elem
	
	def import_(self, **kwargs):
		elem: et.Element = kwargs.get("elem")
		
		self.unknown_01 = int(elem.attrib['unk01'])
		self.unknown_02 = int(elem.attrib['unk02'])
		self.object_count = utils.get_container_count(elem)
		
		self.objects = [self.object_type() for _ in elem]
		for i, child in enumerate(elem):
			self.objects[i].import_(child)
	
	def serialize(self, f: BinaryFile):
		f.write_u8(self.unknown_01)
		f.write_u16(self.unknown_02)
		f.write_u16(self.object_count)
		for child in self.objects:
			child.serialize(f)

























