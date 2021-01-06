"""
Runtime Container v1 types
"""


# imports
import struct
from typing import Dict, Optional, List, Any
from enum import IntEnum
import xml.etree.ElementTree as et

from files.file import SharedHeader, BinaryFile
from misc import utils as u


# enums
class RT_MetaType_v1(IntEnum):
    Unassigned = 0
    UInteger32 = 1
    Float32 = 2
    String = 3
    Vec2 = 4
    Vec3 = 5
    Vec4 = 6
    Mat3x3 = 7
    Mat4x4 = 8
    UInteger32Array = 9
    Float32Array = 10
    ByteArray = 11
    Deprecated = 12
    ObjectID = 13
    Event = 14
    Total = 15


# dicts
RT_v1_MetaType_String: Dict = {
    RT_MetaType_v1.Unassigned: 'none',
    RT_MetaType_v1.UInteger32: 'uint32',
    RT_MetaType_v1.Float32: 'f32',
    RT_MetaType_v1.String: 'str',
    RT_MetaType_v1.Vec2: 'vec2',
    RT_MetaType_v1.Vec3: 'vec3',
    RT_MetaType_v1.Vec4: 'vec4',
    RT_MetaType_v1.Mat3x3: 'mat3',
    RT_MetaType_v1.Mat4x4: 'mat4',
    RT_MetaType_v1.UInteger32Array: 'a[uint32]',
    RT_MetaType_v1.Float32Array: 'a[f32]',
    RT_MetaType_v1.ByteArray: 'a[bytes]',
    RT_MetaType_v1.Deprecated: 'dep',
    RT_MetaType_v1.ObjectID: 'o_id',
    RT_MetaType_v1.Event: 'event',
    RT_MetaType_v1.Total: 'total',
}
RT_v1_String_MetaType: Dict = { value: key for key, value in RT_v1_MetaType_String.items() }


# class
class RT_Header_v1(SharedHeader):
    """
    1) Four CC
    2) Version (1)
    """
    def __init__(self):
        super().__init__()
        self.length = 8
        self.four_cc = "RTPC"
    
    def __str__(self):
        return f"RTPC_Header_v1: {self.four_cc} version {self.version}"


class RT_Property_v1:
    """
    Simple types:
    1) Name hash
    2) Property value
    3) Property type
    
    Complex type:
    1) Name hash
    2) Data offset
    3) Property type
    
    Complex type content
    1) Property data
    """
    def __init__(self):
        self.name: str = ''
        self.name_hash: int = 0
        self.data_offset: int = 0
        self.raw_data: Any = None
        self.type: RT_MetaType_v1 = RT_MetaType_v1.Unassigned
        self.value: Any = None
        
        self.simple_type: bool = False
        self.base_pos: int = 0
    
    def get_type_str(self) -> str:
        return RT_v1_MetaType_String[self.type]

    def deserialize_complex_array(self, f: BinaryFile):
        """ Complex array deserialize. """
        if self.type == RT_MetaType_v1.Vec2:
            self.value = list(f.read_f32(2))
        elif self.type == RT_MetaType_v1.Vec3:
            self.value = list(f.read_f32(3))
        elif self.type == RT_MetaType_v1.Vec4:
            self.value = list(f.read_f32(4))
        elif self.type == RT_MetaType_v1.Mat3x3:
            self.value = list(f.read_f32(9))
        elif self.type == RT_MetaType_v1.Mat4x4:
            self.value = list(f.read_f32(16))
        else:
            raise ValueError(f"RT_MetaType_v1 not a complex array: {self.type}")

    def preprocess_data(self, raw_data: str):
        if self.type == RT_MetaType_v1.UInteger32:
            self.value = int(raw_data)
        elif self.type == RT_MetaType_v1.Float32:
            self.value = float(raw_data)
        elif self.type == RT_MetaType_v1.String:
            self.value = str(raw_data)
        elif self.type == RT_MetaType_v1.ObjectID:
            self.value = int(u.safe_dehex(raw_data, fmt="Q", switch=True))
        elif self.type in [RT_MetaType_v1.Vec2, RT_MetaType_v1.Vec3, RT_MetaType_v1.Vec4,
                           RT_MetaType_v1.Mat3x3, RT_MetaType_v1.Mat4x4]:
            self.value = []
            for x in raw_data.split(" "):
                for y in x.split(","):
                    self.value.append(float(y))
        elif self.type in [RT_MetaType_v1.UInteger32Array, RT_MetaType_v1.Float32Array]:
            if raw_data != "":
                py_type_func = float if self.type == RT_MetaType_v1.Float32Array else int
                self.value = [ py_type_func(number) for number in raw_data.split(",") ]
            else:
                self.value = []
        elif self.type == RT_MetaType_v1.ByteArray:
            self.value = [ single_byte.encode("utf-8") for single_byte in raw_data.split(",") ]
        elif self.type == RT_MetaType_v1.Event:
            self.value = []
            if len(raw_data) > 0:
                pairs = raw_data.split(", ")
                for pair in pairs:
                    first, second = pair.split("=")
                    self.value.append((u.safe_dehex(first), u.safe_dehex(second)))
        else:
            raise ValueError("RT_MetaType_v1 not found.")

    # io
    def deserialize(self, f: BinaryFile, db_cursor=None):
        self.name_hash = f.read_s32()
        if db_cursor is not None:
            db_cursor.execute(f"SELECT value FROM properties WHERE hash = {self.name_hash}")
            value = db_cursor.fetchone()
            if value is not None:
                self.name = value[0]
        self.raw_data = f.read_u32()
        self.type = RT_MetaType_v1(f.read_u8())
        
        # Base data types
        # Simple types
        if self.type in [RT_MetaType_v1.Unassigned, RT_MetaType_v1.UInteger32, RT_MetaType_v1.Float32]:
            if self.type == RT_MetaType_v1.Unassigned:
                return None
            self.raw_data = struct.pack('I', self.raw_data)
            if self.type == RT_MetaType_v1.UInteger32:
                fmt = 'I'
            elif self.type == RT_MetaType_v1.Float32:
                fmt = 'f'
            else:
                raise KeyError("RT_MetaType_v1 not found.")
            self.value = struct.unpack(fmt, self.raw_data)[0]
            return None
        
        # Deferred/pointer types
        original_position = f.tell()
        f.seek(self.raw_data)
        if self.type == RT_MetaType_v1.String:
            self.value = f.read_strz()
        elif self.type == RT_MetaType_v1.ObjectID:
            self.value = f.read_u64()
        elif self.type in [RT_MetaType_v1.Vec2, RT_MetaType_v1.Vec3, RT_MetaType_v1.Vec4,
                           RT_MetaType_v1.Mat3x3, RT_MetaType_v1.Mat4x4]:
            self.deserialize_complex_array(f)
        elif self.type in [RT_MetaType_v1.UInteger32Array, RT_MetaType_v1.Float32Array]:
            count = f.read_u32()
            type_func = f.read_u32 if self.type == RT_MetaType_v1.UInteger32 else f.read_f32
            if count > 0:
                self.value = [type_func(count)] if count == 1 else list(type_func(count))
        elif self.type == RT_MetaType_v1.ByteArray:
            count = f.read_u32()
            if count > 0:
                self.value = []
                if count > 1:
                    self.value.extend(f.read_u8(count))
        # self.value = list(map(safe_hex, self.value, ['B' for _ in range(count)]))
        elif self.type == RT_MetaType_v1.Event:
            count = f.read_u32()
            self.value = []
            for i in range(count):
                self.value.append(f.read_u32(2))
        else:
            raise ValueError("RT_MetaType_v1 not found.")
        f.seek(original_position)
    
    def export(self):
        elem = et.Element('property')
        elem.attrib['hash'] = u.safe_hex(self.name_hash, fmt='i')
        elem.attrib['type'] = f"{self.get_type_str()}"
        elem.attrib['name'] = self.name
        
        if self.value is None:
            return elem
        
        if self.type == RT_MetaType_v1.String:
            elem.text = self.value.decode('utf-8')
        elif self.type == RT_MetaType_v1.Float32:
            elem.text = u.f32_fmt(self.value)
        elif self.type in [RT_MetaType_v1.Vec2, RT_MetaType_v1.Vec3, RT_MetaType_v1.Vec4]:
            elem.text = ",".join(map(u.f32_fmt, self.value))
        elif self.type == RT_MetaType_v1.Mat3x3:
            by_three = [
                ",".join(map(u.f32_fmt, self.value[:3])),
                ",".join(map(u.f32_fmt, self.value[3:6])),
                ",".join(map(u.f32_fmt, self.value[6:]))
            ]
            elem.text = " ".join(by_three)
        elif self.type == RT_MetaType_v1.Mat4x4:
            by_four = [
                ",".join(map(u.f32_fmt, self.value[:4])),
                ",".join(map(u.f32_fmt, self.value[4:8])),
                ",".join(map(u.f32_fmt, self.value[8:12])),
                ",".join(map(u.f32_fmt, self.value[12:]))
            ]
            elem.text = " ".join(by_four)
        elif self.type in [RT_MetaType_v1.UInteger32Array, RT_MetaType_v1.Float32Array]:
            elem.text = ",".join(map(str, self.value))
        elif self.type == RT_MetaType_v1.ByteArray:
            mapped = map(u.safe_hex, self.value, ['B' for _ in range(len(self.value))])
            elem.text = ",".join(list(mapped))
        elif self.type == RT_MetaType_v1.ObjectID:
            elem.text = u.safe_hex(self.value, 'Q', switch=True)
        elif self.type == RT_MetaType_v1.Event:
            values = []
            for pair in self.value:
                fmt_e01, fmt_e02 = u.safe_hex(pair[0]), u.safe_hex(pair[1])
                values.append(f"{fmt_e01}={fmt_e02}")
            elem.text = ", ".join(values)
        else:
            elem.text = f"{self.value}"
        
        return elem

    def import_(self, elem: et.Element):
        self.name = elem.attrib["name"]
        self.name_hash = u.safe_dehex(elem.attrib["hash"], fmt='i')
        self.type = RT_v1_String_MetaType[elem.attrib["type"]]
        raw_text = elem.text
        if raw_text is None:
            raw_data = ""
        else:
            raw_data = str(raw_text)
        self.preprocess_data(raw_data)

    def serialize(self, f: BinaryFile):
        f.write_s32(self.name_hash)
        if self.type in [RT_MetaType_v1.UInteger32, RT_MetaType_v1.Float32]:
            self.simple_type = True
            if self.type == RT_MetaType_v1.UInteger32:
                f.write_u32(int(self.value))
            elif self.type == RT_MetaType_v1.Float32:
                f.write_f32(float(self.value))
            f.write_u8(self.type)
            return None
        
        self.base_pos = f.tell()
        f.write(b"FFFF")
        f.write_u8(self.type)
        return None
    
    def write(self, f: BinaryFile) -> None:
        """
        RTPC requires the offset of a complex property that's based on prior complex properties.
        Naive implementation for now until I have time to work out a better solution.
        """
        if self.simple_type:
            return None
        deferred_offset: int = f.tell()
        if self.type == RT_MetaType_v1.Mat4x4:
            f.write_align(force=True)
        self.write_deferred(f)
        new_pos: int = f.tell()
        f.seek(self.base_pos)
        f.write_u32(deferred_offset)
        f.seek(new_pos)
        
        if self.type == RT_MetaType_v1.String:
            f.write_align()
        
        return None
    
    def write_deferred(self, f: BinaryFile):
        if self.type == RT_MetaType_v1.String:
            f.write_strl(str(self.value), delim=True)
        elif self.type == RT_MetaType_v1.ObjectID:
            f.write_u64(int(self.value))
        elif self.type in [RT_MetaType_v1.Vec2, RT_MetaType_v1.Vec3, RT_MetaType_v1.Vec4,
                           RT_MetaType_v1.Mat3x3, RT_MetaType_v1.Mat4x4]:
            f.write_f32(self.value)
        elif self.type in [RT_MetaType_v1.UInteger32Array, RT_MetaType_v1.Float32Array]:
            type_func = f.write_f32 if self.type == RT_MetaType_v1.Float32Array else f.write_u32
            f.write_u32(len(self.value))
            type_func(self.value)
        elif self.type == RT_MetaType_v1.ByteArray:
            f.write_u32(len(self.value))
            for x in self.value:
                y = int(x, 16)
                f.write_u8(y)
        elif self.type == RT_MetaType_v1.Event:
            f.write_u32(len(self.value))
            for pair in self.value:
                f.write_u32(pair[0])
                f.write_u32(pair[1])
        else:
            raise ValueError("RT_MetaType_v1 not found.")


class RT_Container_v1:
    """
    1) Container header.
    2) Property headers (Basic properties or deferred properties).
    3) Sub-container headers.
    4) Deferred property values.
    5) Sub-containers.
    """
    def __init__(self):
        self.name: str = ''
        self.name_hash: Optional[int] = None
        self.data_offset: Optional[int] = None
        self.property_count: Optional[int] = None
        self.instance_count: Optional[int] = None
        self.properties: List[RT_Property_v1] = []
        self.containers: List[RT_Container_v1] = []

        self.base_pos: int = 0
    
    # getters
    def get_property(self, name_hash, recurse: bool = True):
        """ Search for a property in the container. Optional recursion. """
        for child in self.properties:
            if child.name_hash == name_hash:
                return child
        
        if recurse:
            for child in self.containers:
                result = child.get_property(name_hash, recurse)
                if result is not None:
                    return result
        
        return None
    
    def get_container(self, name_hash, recurse: bool = True):
        """ Search for a container within this container. Optional recursion. """
        for child in self.containers:
            if child.name_hash == name_hash:
                return child
        
        if recurse:
            for child in self.containers:
                result = child.get_container(name_hash, recurse)
                if result is not None:
                    return result
        
        return None
    
    # sort
    def sort_properties(self, recurse: bool = True):
        """ Sort properties by name then name_hash. Optional recursion. """
        self.properties.sort(key=lambda x: (x.name == "", x.name.lower(), x.name_hash))
        
        if recurse:
            for child in self.containers:
                child.sort_properties(recurse)
    
    def sort_containers(self, recurse: bool = True):
        """ Sort containers by name then name_hash. Optional recursion. """
        self.containers.sort(key=lambda x: (x.name == "", x.name, x.name_hash))
        
        if recurse:
            for child in self.containers:
                child.sort_containers(recurse)
    
    # load
    def load_properties(self, f: BinaryFile, db_cursor=None):
        f.seek(self.data_offset)
        self.properties = [RT_Property_v1() for _ in range(self.property_count)]
        for i in range(self.property_count):
            self.properties[i].deserialize(f, db_cursor)
    
    def load_containers(self, f: BinaryFile, db_cursor=None):
        # Align to 4-byte boundary
        new_position = f.tell()
        f.seek(new_position + u.align(new_position))
        
        self.containers = [RT_Container_v1() for _ in range(self.instance_count)]
        for i in range(self.instance_count):
            self.containers[i].deserialize(f, db_cursor)
    
    # io
    def deserialize(self, f: BinaryFile, db_cursor=None):
        """ Deserialize a file. Optional sqlite3.cursor object for dehash. """
        self.name_hash = f.read_s32()
        if db_cursor is not None:
            db_cursor.execute(f"SELECT value FROM properties WHERE hash = {self.name_hash}")
            value = db_cursor.fetchone()
            if value is not None:
                self.name = value[0]
        self.data_offset = f.read_u32()
        self.property_count = f.read_u16()
        self.instance_count = f.read_u16()
        
        original_position = f.tell()
        self.load_properties(f, db_cursor)
        self.load_containers(f, db_cursor)
        f.seek(original_position)
    
    def export(self):
        elem = et.Element('container')
        elem.attrib['hash'] = u.safe_hex(self.name_hash, 'i')
        elem.attrib['name'] = self.name
        
        for prop in self.properties:
            elem.append(prop.export())
        
        for container in self.containers:
            elem.append(container.export())
        
        return elem
    
    def import_(self, **kwargs):
        elem: et.Element = kwargs.get("elem")
        
        self.name = elem.attrib["name"]
        self.name_hash = elem.attrib["hash"]
        
        for child in elem:
            if child.tag == "property":
                prop: RT_Property_v1 = RT_Property_v1()
                prop.import_(child)
                self.properties.append(prop)
            elif child.tag == "container":
                con: RT_Container_v1 = RT_Container_v1()
                con.import_(elem=child)
                self.containers.append(con)
        
        self.property_count = len(self.properties)
        self.instance_count = len(self.containers)
    
    def serialize(self, f: BinaryFile):
        deferred_offset: int = f.tell()
        f.seek(self.base_pos)
        f.write_u32(deferred_offset)
        f.seek(deferred_offset)
        
        for prop in self.properties:
            prop.serialize(f)
        f.write_align()
        
        for sub_con in self.containers:
            sub_con.serialize_header(f)

        for prop in self.properties:
            prop.write(f)
        
        f.align()
        for sub_con in self.containers:
            sub_con.serialize(f)
    
    def serialize_header(self, f: BinaryFile):
        f.write_s32(u.safe_dehex(self.name_hash, 'i'))
        self.base_pos = f.tell()
        f.write(b"FFFF")
        f.write_u16(self.property_count)
        f.write_u16(self.instance_count)










