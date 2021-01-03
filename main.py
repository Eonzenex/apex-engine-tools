"""
Entry point for the program
"""


# imports
from formats.manager import manage_xml
import argparse as ap
import os.path
from typing import List


# settings
VERSION: str = "0.3.0"
DB_FILEPATH: str = "./dbs/global.db"
SUPPORTED_FILETYPES: List[str] = ["xml", "blo", "epe", "flo"]


# functions
def entry():
	""" Entry point for program. """
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
			manage_xml(path, DB_FILEPATH)
		else:
			# process_folder(path)
			print(f"DEBUG: Folder processing is WIP")


# entry point
if __name__ == "__main__":
	entry()



















