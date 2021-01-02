"""

"""


# imports
import argparse as ap
import os.path
from typing import List
import xml.etree.ElementTree as et


# settings
VERSION: str = "0.3.0"


# functions
def process_file(file_path: str) -> None:
	base_path, filename = os.path.split(file_path)
	fn_wo_ext, ext = os.path.splitext(filename)
	if len(ext) < 2:
		print(f"ERROR: File extension too short - '{ext}' ('{file_path}')")
		return None
	
	if ext not in ["xml"]:
		print(f"ERROR: Unsupported file extension - '{ext}' ('{file_path}')")
		return None


def entry():
	parser = ap.ArgumentParser(description=f"Apex Engine Tools {VERSION}")
	parser.add_argument('process', metavar='path', type=str, nargs='+', help='process each file/folder')
	
	args = parser.parse_args()
	paths: List = []
	for path in args.process:
		paths.append(os.path.normpath(path))
	
	for path in paths:
		if not os.path.exists(path):
			print(f"ERROR: Path does not exist - '{path}'")
			continue
		if os.path.isfile(path):
			process_file(path)
		else:
			process_folder(path)
	
	print(f"Drag and drop WIP")
	print(f"Path/s dragged: '{', '.join(paths)}'")


# entry point
if __name__ == "__main__":
	entry()
