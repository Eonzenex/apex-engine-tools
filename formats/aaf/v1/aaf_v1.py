"""
Avalanche Archive Format v1
"""


# imports
import io

from files.file import SharedFile, BinaryFile
from formats.aaf.v1.aaf_v1_types import AAF_Header_v1, AAF_Block_v1
from formats.sarc.v2.sarc_v2 import SARC_v2


# class
# TODO: Link AAF processors to a SARC parent to allow AAF -> Unpacked SARC
class AAF_v1(SharedFile):
    """
    Decompresses to a SARC file.
    """

    def __init__(self, file_path: str = ""):
        super().__init__(file_path)
        self.version = 1
        self.header_type = AAF_Header_v1
        self.stream: bytes = b""
        self.sarc_type = SARC_v2
        self.sarc_processor = self.sarc_type(file_path)

        if file_path != "":
            self.get_file_details(file_path)

    def __str__(self):
        return f"AAF_v1: {self.header.four_cc} version {self.header.version}"
    
    def get_file_path(self) -> str:
        return f"{self.get_file_path_short()}.{self.sarc_processor.extension}"

    # io
    def deserialize(self, **kwargs):
        f: BinaryFile = kwargs.get("file")
        for i in range(self.header.block_count):
            block: AAF_Block_v1 = AAF_Block_v1()
            block.deserialize(f)
            self.stream += block.data
        
        f: BinaryFile = BinaryFile(io.BytesIO(self.stream))
        self.sarc_processor.load_stream(file=f)

    def export(self, **kwargs):
        file_path: str = kwargs.get("file_path", "")
        self.sarc_processor.export(file_path=file_path)

    def load_converted(self, **kwargs):
        load_sarc: bool = kwargs.get("load_sarc", False)
        if load_sarc:
            self.import_()
        else:
            self.stream = self.sarc_processor.load_converted()
        self.serialize()
    
    def import_(self, **kwargs):
        with BinaryFile(open(self.get_file_path(), "rb")) as f:
            self.stream = f.read_all()

    def serialize(self, **kwargs):
        # TODO: Not quite correct
        file_name: str = kwargs.get("file_name", "")
        if file_name != "":
            self.file_name = file_name
        file_path = self.get_file_path()
        self.header = self.header_type()
        stream_file: BinaryFile = BinaryFile(io.BytesIO(self.stream))
        self.header.update(len(self.stream))
        
        total_compressed_size: int = 0
        with BinaryFile(open(file_path, "wb")) as aaf_file:
            self.header.serialize(aaf_file)
            chunk: bytes = stream_file.read(self.header.max_block_size)
            while chunk:
                block: AAF_Block_v1 = AAF_Block_v1()
                block.data = chunk
                block.serialize(aaf_file)
                total_compressed_size += block.compressed_size
                chunk = stream_file.read(self.header.max_block_size)

            self.header.compressed_size = total_compressed_size
            self.header.write(aaf_file)
