"""
Debug entry point.
"""


# imports
from formats.inline_runtime.v1 import IRTPC_v1
from formats.runtime.v1.rtpc_v1 import RTPC_v1
from misc import utils as u


# config
BASE_PATH: str = "E:/Projects/Just Cause Tools/Apex Engine Tools/tests"
IRTPC_v1_FILE_PATH: str = f"{BASE_PATH}/irtpc/jc4/jc4_world"
RTPC_v1_FILE_PATH: str = f"{BASE_PATH}/rtpc/jc3/global"


# functions
def deserialize(file_path: str, file_class):
	supported_file: file_class = file_class(file_path, "./dbs/global.db")
	print(f"DEBUG|Deserialize: Loading...")
	supported_file.load()
	# print(f"DEBUG|Deserialize: Sorting...")
	# supported_file.sort()
	print(f"DEBUG|Deserialize: Exporting...")
	supported_file.export()
	print(f"DEBUG|Deserialize: Complete")


def serialize(file_path: str, file_class):
	print(f"DEBUG|Serialize: Loading...")
	file_raw = u.load_xml(file_path)
	root = file_raw.getroot()
	file = file_class(file_path)
	print(f"DEBUG|Serialize: Importing...")
	file.import_(root=root)
	print(f"DEBUG|Serialize: Serializing...")
	file.serialize(f"{file.get_file_path_short()}_serial")
	print(f"DEBUG|Serialize: Complete")


# main
if __name__ == "__main__":
	test: str = input(f"Which test to run? 1 for deserialize, 2 for serialize, 3 for both: ")
	if test == '1':
		deserialize(f"{RTPC_v1_FILE_PATH}.blo", RTPC_v1)
	elif test == '2':
		serialize(f"{RTPC_v1_FILE_PATH}.xml", RTPC_v1)
	elif test == '3':
		deserialize(f"{IRTPC_v1_FILE_PATH}.bin", IRTPC_v1)
		serialize(f"{IRTPC_v1_FILE_PATH}.xml", IRTPC_v1)
	else:
		print(f"Invalid option, aborting...")
	
