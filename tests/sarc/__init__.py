"""
Testing package for SARC files
"""


# imports
from formats.sarc.v2.sarc_v2 import SARC_v2


# config
BASE_PATH: str = "E:/Projects/Just Cause Tools/Apex Engine Tools"
SARC_v2_FILE_PATH: str = f"{BASE_PATH}/tests/sarc/jc3/w011_pistol_u_pozhar_98.sarc"
CONV_FILE_PATH: str = f"{BASE_PATH}/tests/sarc/jc3/w011_pistol_u_pozhar_98"


# main
if __name__ == "__main__":
    # file: SARC_v2 = SARC_v2(SARC_v2_FILE_PATH)
    #
    # print(f"DEBUG: SARC loading...")
    # file.load()
    #
    # print(f"DEBUG: SARC exporting...")
    # file.export()

    file: SARC_v2 = SARC_v2(CONV_FILE_PATH)

    print(f"DEBUG: SARC serialization...")
    file.load_converted()
    
    print(f"DEBUG: Done.")

