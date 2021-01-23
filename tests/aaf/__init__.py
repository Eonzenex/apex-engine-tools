"""
Testing package for AAF files
"""


# imports
from formats.aaf.v1.aaf_v1 import AAF_v1


# config
BASE_PATH: str = "E:/Projects/Just Cause Tools/Apex Engine Tools"
AAF_v1_FILE_PATH: str = f"{BASE_PATH}/tests/aaf/jc3/w011_pistol_u_pozhar_98.ee"
CONV_FILE_PATH: str = f"{BASE_PATH}/tests/aaf/jc3/w011_pistol_u_pozhar_98_serial"


# main
if __name__ == "__main__":
    # file: AAF_v1 = AAF_v1(AAF_v1_FILE_PATH)
    #
    # print(f"DEBUG: AAF loading...")
    # file.load()
    #
    # print(f"DEBUG: AAF exporting...")
    # file.export()

    file: AAF_v1 = AAF_v1(CONV_FILE_PATH)

    print(f"DEBUG: AAF serialization...")
    file.load_converted()
    
    print(f"DEBUG: Done.")
