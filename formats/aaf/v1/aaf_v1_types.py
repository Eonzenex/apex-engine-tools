"""
Avalanche Archive Format v1 types
"""

# imports
import math
import zlib

from files.file import SharedHeader, BinaryFile

# class
from misc.errors import PropertyDoesNotMatch


class AAF_Header_v1(SharedHeader):
    """
    1) Four CC
    2) Version (1)
    3) Comment (length of 28)
    4) Uncompressed size
    5) Compressed size
    6) Block count
    """
    
    def __init__(self):
        super().__init__()
        self.four_cc = b"AAF\00"
        self.version = 1
        
        self.length: int = 4 + 4 + 8 + 16 + 16  # 48
        self.comment: bytes = b""
        self.uncompressed_size: int = 0
        self.compressed_size: int = 0
        self.block_count: int = 0
        # 33554432 is 32MB, the maximum size of a single block
        self.max_block_size: int = 33554432
        
        self.base_pos: int = 0
    
    def __str__(self):
        return f"AAF_Header: {self.four_cc} version {self.version} comment {self.comment}"
    
    def update(self, stream_len: int):
        self.uncompressed_size = stream_len
        self.block_count = math.ceil(stream_len / self.max_block_size)
    
    def deserialize(self, f: BinaryFile):
        super().deserialize(f)
        self.comment = f.read_strl(8 + 16 + 4)  # 28
        self.uncompressed_size = f.read_u32()
        self.compressed_size = f.read_u32()
        self.block_count = f.read_u32()
    
    def serialize(self, f: BinaryFile):
        super().serialize(f)
        f.write_strl("AVALANCHEARCHIVEFORMATISCOOL")
        f.write_u32(self.uncompressed_size)
        self.base_pos = f.tell()
        f.write(b"FFFF")
        f.write_u32(self.block_count)
    
    def write(self, f: BinaryFile):
        f.seek(self.base_pos)
        f.write_u32(self.compressed_size)


class AAF_Block_v1:
    """
    Each block is 32MB or less uncompressed.
    """
    
    def __init__(self):
        self.compressed_size: int = 0
        self.uncompressed_size: int = 0
        self.data_offset: int = 0
        self.four_cc: bytes = b"EWAM"
        self.data: bytes = b""
    
    def deserialize(self, f: BinaryFile):
        original_pos: int = f.tell()
        self.compressed_size = f.read_u32()
        self.uncompressed_size = f.read_u32()
        self.data_offset = f.tell()
        next_block_offset = f.read_u32()
        four_cc = f.read_strl(4)
        if four_cc != self.four_cc:
            raise PropertyDoesNotMatch(str(four_cc), str(self.four_cc), property_name="Block four cc")
        
        c_buffer = f.read(self.compressed_size)
        uc_buffer = zlib.decompress(c_buffer, -15)
        uc_len: int = len(uc_buffer)
        if uc_len != self.uncompressed_size:
            raise Exception(f"Given uncompressed size != actual: {self.uncompressed_size} vs {uc_len}")
        
        self.data = uc_buffer
        f.seek(original_pos + next_block_offset)
    
    def serialize(self, f: BinaryFile):
        c_buffer = zlib.compress(self.data, 6)
        self.compressed_size = len(c_buffer)
        f.write_u32(self.compressed_size)
        
        self.uncompressed_size = len(self.data)
        f.write_u32(self.uncompressed_size)

        self.data_offset = f.tell()
        f.write_u32(self.data_offset + self.compressed_size)
        f.write(self.four_cc)
        
        f.write(c_buffer)
