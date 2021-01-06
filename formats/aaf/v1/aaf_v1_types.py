"""
Avalanche Archive Format v1 types
"""


# imports
import zlib

from files.file import SharedHeader, BinaryFile


# class
class AAF_Header_v1(SharedHeader):
    def __init__(self):
        super().__init__()
        self.length: int = 4 + 4 + 8 + 16 + 16  # 48
        self.comment: bytes = b""
        self.uncompressed_size: int = 0
        self.compressed_size: int = 0
        self.block_count: int = 0

    def __str__(self):
        return f"AAF_Header: {self.four_cc} version {self.version} comment {self.comment}"

    def deserialize(self, f: BinaryFile):
        super().deserialize(f)
        self.comment = f.read_strl(8 + 16 + 4)  # 28
        self.uncompressed_size = f.read_u32()
        self.compressed_size = f.read_u32()
        self.block_count = f.read_u32()


class AAF_Block_v1:
    BLOCK_FOUR_CC: bytes = b"EWAM"

    def __init__(self):
        self.compressed_size: int = 0
        self.uncompressed_size: int = 0
        self.data_offset: int = 0
        self.four_cc: bytes = b""
        self.data: bytes = b""

    def deserialize(self, f: BinaryFile):
        original_pos: int = f.tell()
        self.compressed_size = f.read_u32()
        self.uncompressed_size = f.read_u32()
        self.data_offset = f.tell()
        next_block_offset = f.read_u32()
        self.four_cc = f.read_strl(4)
        if self.four_cc != self.BLOCK_FOUR_CC:
            raise ValueError(f"Block magic does not match: {self.four_cc} != {self.BLOCK_FOUR_CC}")

        c_buffer = f.read(self.compressed_size)
        uc_buffer = zlib.decompress(c_buffer, -15)
        uc_len: int = len(uc_buffer)
        if uc_len != self.uncompressed_size:
            raise Exception(f"Given uncompressed size != actual: {self.uncompressed_size} vs {uc_len}")

        self.data = uc_buffer
        f.seek(original_pos + next_block_offset)
