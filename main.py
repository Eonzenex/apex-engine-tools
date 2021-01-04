"""
Entry point for the program
"""


# imports
from formats.manager import manage_xml
import argparse as ap
import os.path
from typing import List
import configparser as cp


# settings
from misc.errors import ApexEngineError, FileDoesNotExist

VERSION: str = "0.3.1"
DB_FILEPATH: str = os.path.abspath("./dbs/global.db")
AUTO_CLOSE: bool = False
SUPPORTED_FILETYPES: List[str] = ["xml", "blo", "epe", "flo"]


# functions
if __name__ == "__main__":
	""" Entry point for program. """
	config = cp.ConfigParser()
	abs_config_path: str = os.path.abspath(".\\config.ini")
	
	# TODO: Separate config defaults
	if not os.path.exists(abs_config_path):
		config["DEFAULT"] = {}
		config["DEFAULT"]["DatabaseAbsolutePath"] = DB_FILEPATH
		config["DEFAULT"]["AutoCloseOnComplete"] = str(int(AUTO_CLOSE))
		with open(abs_config_path, "w") as config_f:
			config.write(config_f)
	config.read(abs_config_path)
	DB_FILEPATH = config["DEFAULT"]["DatabaseAbsolutePath"]
	AUTO_CLOSE = bool(int(config["DEFAULT"]["AutoCloseOnComplete"]))
	
	parser = ap.ArgumentParser(description=f"Apex Engine Tools {VERSION}")
	parser.add_argument('process', metavar='path', type=str, nargs='+', help='process each file/folder')
	
	args = parser.parse_args()
	paths: List = []
	for path in args.process:
		if os.path.exists(path):
			paths.append(os.path.normpath(path))
			continue
		print(FileDoesNotExist(path))
	
	for i, path in enumerate(paths):
		try:
			if os.path.isfile(path):
				manage_xml(path, DB_FILEPATH)
			else:
				# process_folder(path)
				print(f"DEBUG: Folder processing is WIP")
		except ApexEngineError as aee:
			print(aee)
		print(f"[{i + 1}/{len(paths)}] Path/s completed '{path}'")
	
	if not AUTO_CLOSE:
		input("Press any key to continue...")



















