"""

"""


# imports
import argparse as ap
import os.path
from typing import List


# functions
def entry():
	parser = ap.ArgumentParser(description=f"Apex Engine Tools v0.3.0")
	parser.add_argument('process', metavar='path', type=str, nargs='+', help='process each file/folder')
	
	args = parser.parse_args()
	paths: List = []
	for path in args.process:
		paths.append(os.path.normpath(path))
	print(f"Drag and drop WIP")
	print(f"Path/s dragged: '{', '.join(paths)}'")


# entry point
if __name__ == "__main__":
	entry()
