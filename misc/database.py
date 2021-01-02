"""
Database commands.
"""


# imports
import sqlite3 as sql
import os.path

from misc.hash_functions import hash_jenkins


# settings
TO_ADD_FILE_PATH: str = os.path.abspath('../databases/private_properties_JC3.txt')
DB_FILE_PATH: str = os.path.abspath("../databases/global.db")


# functions
def add_file_to_database(database_file_path: str, to_add_file_path: str):
	if not os.path.exists(database_file_path):
		raise FileNotFoundError("Cannot find database_file_path")
	if not os.path.exists(to_add_file_path):
		raise FileNotFoundError("Cannot find database_file_path")
	
	to_add = []
	with open(to_add_file_path, "r") as f:
		contents = f.read()
		split = contents.split("\n")
		for line in split:
			value = line
			val_hash_int, val_hash_hex = hash_jenkins(value)
			to_add.append((value, val_hash_int))
	query = "INSERT INTO properties(value, hash) " \
	        "VALUES " + ", ".join(map(str, to_add))
	conn = sql.connect(database_file_path)
	c = conn.cursor()
	c.execute(query)
	conn.commit()
	conn.close()


# main
if __name__ == "__main__":
	add_file_to_database(DB_FILE_PATH, TO_ADD_FILE_PATH)
	pass
