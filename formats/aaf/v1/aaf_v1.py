"""
Avalanche Archive Format v1
"""


# imports
import os.path

from files.file import SharedFile, BinaryFile
from formats.aaf.v1.aaf_v1_types import AAF_Header_v1, AAF_Block_v1


# class
class AAF_v1(SharedFile):
    """ Decompresses to a SARC file. """
    def __init__(self, file_path: str = ""):
        super().__init__(file_path)
        self.version = 1
        self.header_type = AAF_Header_v1
        self.stream: bytes = b""

        if file_path != "":
            self.get_file_details(file_path)

    def __str__(self):
        return f"AAF_v1: {self.header.four_cc} version {self.header.version}"

    # io
    def deserialize(self, file: BinaryFile):
        for i in range(self.header.block_count):
            block: AAF_Block_v1 = AAF_Block_v1()
            block.deserialize(file)
            self.stream += block.data

    def export(self, file_path: str = ""):
        if file_path == "":
            file_path = f"{self.get_file_path_short()}.sarc"
        else:
            file_path = os.path.abspath(file_path)

        with open(file_path, "wb") as f:
            f.write(self.stream)

    def import_(self, **kwargs):
        # TODO: 'AAF_v1' 'import_'
        f: BinaryFile = kwargs.get("file")
        self.header = self.header_type()

    def serialize(self, file_name: str = ""):
        # TODO: 'AAF_v1' 'serialize'
        if file_name != "":
            self.file_name = file_name
        file_path = self.get_file_path()
