"""
Generic file
"""


# import
import xml.etree.ElementTree as et
import os.path
from typing import Union, Optional
import struct


# class
class BinaryFile:
    def __init__(self, file):
        self.file = file
    
    def __enter__(self):
        self.file = self.file.__enter__()
        return self
    
    def __exit__(self, t, value, traceback):
        self.file.__exit__(t, value, traceback)
    
    # in-built
    def seek(self, pos):
        return self.file.seek(pos)
    
    def tell(self):
        return self.file.tell()
    
    def read(self, n: int = None):
        return self.file.read(n)
    
    def write(self, blk):
        return self.file.write(blk)
    
    def align(self):
        self.seek(self.tell() + (4 - (self.tell() % 4)) % 4)
    
    def write_align(self, delim: bytes = b"", force: bool = False):
        off_by: int = (4 - (self.tell() % 4)) % 4
        if force and off_by == 0:
            self.pad(4, delim=delim)
        else:
            self.pad(off_by, delim=delim)
    
    # read
    def read_all(self) -> bytes:
        self.file.seek(0)
        return self.file.read1()
    
    def read_fmt(self, fmt: str, length: int, num: int = 1):
        """ Read 'x' bytes 'y' amount of times then format """
        total_len: int = length * num
        buffer: bytes = self.read(total_len)
        if len(buffer) != total_len:
            return None
        
        if num != 1:
            return struct.unpack(fmt * num, buffer)
        return struct.unpack(fmt, buffer)[0]
    
    def read_strz(self, delimiter: bytes = b'\00'):
        """ Read till delimiter reached """
        buffer: bytes = b''
        while True:
            this: bytes = self.read(1)
            if len(this) == 0:
                break
            elif this == delimiter:
                break
            else:
                buffer += this
        return buffer
    
    def read_c8(self, num: int = 1):
        """ Read a single char """
        return self.read_fmt('c', 1, num)
    
    def read_strl(self, num: int = 1):
        """ Read a list of chars (str) """
        val = self.read_c8(num)
        if isinstance(val, tuple):
            bytes_val = [bytes(x) for x in val]
            return b''.join(bytes_val)
        return val
    
    def read_strl_u32(self, num: int = 1):
        """ Read multiple strings? """
        results: list = []
        for i in range(num):
            strl = self.read_strl(self.read_u32())
            results.append(strl)
        
        return results
    
    def read_s8(self, num: int = 1):
        """ Signed char """
        return self.read_fmt('b', 1, num)
    
    def read_u8(self, num: int = 1):
        """ Unsigned char """
        return self.read_fmt('B', 1, num)
    
    def read_s16(self, num: int = 1):
        """ Signed short """
        return self.read_fmt('h', 2, num)
    
    def read_u16(self, num: int = 1):
        """ Unsigned short """
        return self.read_fmt('H', 2, num)
    
    def read_s32(self, num: int = 1):
        """ Signed int32 """
        return self.read_fmt('i', 4, num)
    
    def read_u32(self, num: int = 1):
        """ Unsigned int32 """
        return self.read_fmt('I', 4, num)
    
    def read_s64(self, num: int = 1):
        """ Signed int64 """
        return self.read_fmt('q', 8, num)
    
    def read_u64(self, num: int = 1):
        """ Unsigned int64 """
        return self.read_fmt('Q', 8, num)
    
    def read_f32(self, num: int = 1):
        """ Float """
        return self.read_fmt('f', 4, num)
    
    def read_f64(self, num: int = 1):
        """ Double """
        return self.read_fmt('d', 8, num)
    
    # write
    def pad(self, num: int = 1, delim: bytes = b""):
        """ Pad the file by a variable amount. """
        if delim == b"":
            pad_bytes = [bytes("P", 'utf-8') for _ in range(num)]
        else:
            pad_bytes = [delim for _ in range(num)]
        buffer = struct.pack('c' * num, *pad_bytes)
        self.file.write(buffer)
    
    def write_fmt(self, fmt: str, data):
        """ Write formatted bytes. """
        if isinstance(data, list) or isinstance(data, tuple):
            buffer = struct.pack(fmt * len(data), *data)
        else:
            buffer = struct.pack(fmt, data)
        
        self.file.write(buffer)
    
    def write_c8(self, data):
        """ Write a single char """
        return self.write_fmt('c', data)
    
    def write_strl(self, data: str, delim: bool = False, delimiter: bytes = b'\00'):
        """ A string """
        data_ = [bytes(c, 'utf-8') for c in data]
        self.write_c8(data_)
        if delim:
            self.write_fmt('c', delimiter)
    
    def write_s8(self, data):
        """ Signed char """
        return self.write_fmt('b', data)
    
    def write_u8(self, data):
        """ Unsigned char """
        return self.write_fmt('B', data)
    
    def write_s16(self, data):
        """ Signed short """
        return self.write_fmt('h', data)
    
    def write_u16(self, data):
        """ Unsigned short """
        return self.write_fmt('H', data)
    
    def write_s32(self, data):
        """ Signed int32 """
        return self.write_fmt('i', data)
    
    def write_u32(self, data):
        """ Unsigned int32 """
        return self.write_fmt('I', data)
    
    def write_s64(self, data):
        """ Signed int64 """
        return self.write_fmt('q', data)
    
    def write_u64(self, data):
        """ Unsigned int64 """
        return self.write_fmt('Q', data)
    
    def write_f32(self, data):
        """ Float """
        return self.write_fmt('f', data)
    
    def write_f64(self, data):
        """ Double """
        return self.write_fmt('d', data)


class SharedHeader:
    def __init__(self):
        self.four_cc: bytes = b""
        self.version: int = 0
        self.length = 8
    
    def __str__(self):
        return f"SharedHeader: {self.four_cc} version {self.version}"
    
    def deserialize(self, f: BinaryFile):
        f.seek(0)
        self.four_cc = f.read_strl(4)
        # TODO: Change from 'get file header' to 'verify file header'
        self.version = f.read_u32()
    
    def serialize(self, f: BinaryFile):
        f.write(self.four_cc)
        f.write_u32(self.version)


class SharedFile:
    def __init__(self, file_path: str = ""):
        self.header_type = SharedHeader
        self.file_path: str = file_path
        self.file_name: str = ""
        self.extension: str = ""
        self.header: Optional[SharedHeader] = None
        self.version: int = 2
    
    def __str__(self):
        return f"SharedFile: '{self.file_name}.{self.extension}'"
    
    def get_file_path(self) -> str:
        return os.path.join(self.file_path, f"{self.file_name}.{self.extension}")
    
    def get_file_path_short(self) -> str:
        return os.path.join(self.file_path, f"{self.file_name}")
    
    def get_file_details(self, file_path: str):
        file_path = os.path.abspath(file_path)
        self.file_path, filename = os.path.split(file_path)
        self.file_name, self.extension = os.path.splitext(filename)
        self.extension = self.extension[1:]
    
    # io
    def get_header(self):
        """ Returns the file's header. """
        if None in [self.file_path, self.file_name, self.extension]:
            raise ValueError("File information is none, need to run 'get_file_details' first")
        
        with BinaryFile(open(self.get_file_path(), "rb")) as f:
            self.header = self.header_type()
            self.header.deserialize(f)

    def load(self):
        """ Safe deserialize. """
        if self.header is None:
            self.get_header()

        with BinaryFile(open(self.get_file_path(), 'rb')) as file:
            # Seek past header.
            file.seek(self.header.length)
            self.deserialize(file=file)

    def load_converted(self, **kwargs):
        """ Safe converted load. """
        raise NotImplementedError
    
    def deserialize(self, **kwargs):
        """ Deserialize the binary file. """
        raise NotImplementedError
    
    def export(self, **kwargs):
        """ Export as an XML. """
        raise NotImplementedError
    
    def import_(self, **kwargs):
        """ Import a file. """
        raise NotImplementedError
    
    def serialize(self, **kwargs):
        """ Serialize to a binary file. """
        raise NotImplementedError


# functions
def is_four_cc(header: Union[SharedHeader, bytes], four_cc: bytes) -> bool:
    """ Whether or not the data matches the given magic. """
    if isinstance(header, SharedHeader):
        return header.four_cc == four_cc
    elif isinstance(header, bytes):
        return header[:4] == four_cc
    else:
        raise TypeError(f"Supplied header was not a supported type.")
