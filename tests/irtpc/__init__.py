"""
Testing package for IRTPC files
"""


# imports
from formats.inline_runtime.v1.irtpc_v1 import IRTPC_v1


# config
BASE_PATH: str = "E:/Projects/Just Cause Tools/Apex Engine Tools"
IRTPC_v1_FILE_PATH: str = f"{BASE_PATH}/tests/irtpc/jc3/jc3_world.bin"
CONV_FILE_PATH: str = f"{BASE_PATH}/tests/irtpc/jc3/jc3_world_serial.xml"


# main
if __name__ == "__main__":
    # file: IRTPC_v1 = IRTPC_v1(IRTPC_v1_FILE_PATH)
    #
    # print(f"DEBUG: IRTPC loading...")
    # file.load()
    #
    # print(f"DEBUG: IRTPC exporting...")
    # file.export()
    
    file: IRTPC_v1 = IRTPC_v1(CONV_FILE_PATH)

    print(f"DEBUG: IRTPC serialization...")
    file.load_converted()
    
    print(f"DEBUG: Done.")

