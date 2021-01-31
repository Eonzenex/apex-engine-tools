"""
Entry point for the program
"""


# imports
from formats.manager import manage_xml, manage_binary
import argparse as ap
import os.path
import sys
from typing import List
import configparser as cp

from misc.errors import ApexEngineError, FileDoesNotExist


# settings
VERSION: str = "0.3.3"
THIS_PATH: str = os.path.split(sys.argv[0])[0]
DB_FILEPATH: str = f"{THIS_PATH}\\global.db"
AUTO_CLOSE: bool = False
DEBUG: bool = False


# functions
if __name__ == "__main__":
    """ Entry point for program. """
    config = cp.ConfigParser()
    abs_config_path: str = f"{THIS_PATH}\\config.ini"
    if DEBUG:
        print(f"THIS_PATH: {THIS_PATH}")
    
    # TODO: Separate config defaults
    if not os.path.exists(abs_config_path):
        config["DEFAULT"] = {}
        config["DEFAULT"]["DatabaseAbsolutePath"] = DB_FILEPATH
        config["DEFAULT"]["AutoCloseOnComplete"] = str(int(AUTO_CLOSE))
        config["DEFAULT"]["Debug"] = str(int(DEBUG))
        with open(abs_config_path, "w") as config_f:
            config.write(config_f)
    config.read(abs_config_path)
    DB_FILEPATH = config["DEFAULT"]["DatabaseAbsolutePath"]
    AUTO_CLOSE = bool(int(config["DEFAULT"]["AutoCloseOnComplete"]))
    DEBUG = bool(int(config["DEFAULT"]["Debug"]))
    
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
                if path[-3:] == "xml":
                    manage_xml(path, DB_FILEPATH)
                else:
                    manage_binary(path, DB_FILEPATH)
            else:
                # process_folder(path)
                print(f"DEBUG: Folder processing is WIP")
        except ApexEngineError as aee:
            print(aee)
        print(f"[{i + 1}/{len(paths)}] Path/s completed '{path}'")
    
    if not AUTO_CLOSE:
        input("Press any key to continue...")



















