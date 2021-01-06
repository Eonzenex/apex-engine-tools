"""
Import XML files created by these tools.
"""


# imports
import argparse as ap
import xml.etree.ElementTree as et
import os.path


# settings
from typing import Optional, List, Dict

from files.file import SharedFile
from formats.runtime_property_container.inline_v4.v4_irtpc import IRTPC_v1
from formats.runtime_property_container.v3.v3_rtpc import RTPC_v1

RTPC_v1_FILE_PATH: str = os.path.abspath("../tests/rtpc/jc3/heat.xml")
IRTPC_v1_FILE_PATH: str = os.path.abspath("../tests/irtpc/jc4/world.xml")


# functions
def setup_argparser() -> ap.ArgumentParser:
    argparser = ap.ArgumentParser(description="Importer for Apex Engine tools v0.2")
    argparser.add_argument("files", type=str, nargs="+", help="A list of files to import and serialize.")

    return argparser


def load_converted(file_path: str) -> et.ElementTree:
    """ Safe XML import. """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Cannot find file: {file_path}")
    
    return et.parse(file_path)


def import_xml(file_path: str):
    etree = load_converted(file_path)
    root = etree.getroot()

    file_data: Dict = {
        "rtpc": {
            "version_attrib": "version",
            "supported_versions": {
                "1": RTPC_v1
            },
        },
        "irtpc": {
            "version_attrib": "version_02",
            "supported_versions": {
                "4": IRTPC_v1
            },
        }
    }

    file_info: Dict = {}
    try:
        file_info: Dict = file_data[root.tag]
    except KeyError:
        raise KeyError(f"Unsupported file type: {root.tag} (Supported: {file_data.keys()})")

    version: str = ""
    v_attrib: str = file_info["version_attrib"]
    try:
        version: str = root.attrib[v_attrib]
    except KeyError:
        raise KeyError(f"Expected version attribute '{v_attrib}', got '{root.tag}'")

    supported_versions: Dict = file_info["supported_versions"]
    try:
        file_type = supported_versions[version]
    except KeyError:
        raise KeyError(f"Unsupported version for {root.tag}: {version} (Supported: {', '.join(supported_versions.keys())})")

    file: SharedFile = file_type(file_path)
    file.import_file(root=root)
    file.serialize(f"{file.get_file_path_short()}_serial")


def import_file(file_path: str):
    extension: str = os.path.splitext(file_path)[1][1:]

    if extension == "xml":
        import_xml(file_path)
    elif extension == "aaf":
        pass
    elif extension == "sarc":
        pass
    else:
        raise ValueError(f"Unsupported file extension: {extension}")


# main
if __name__ == "__main__":
    parser = setup_argparser()
    args = parser.parse_args()
    for filepath in args.files:
        import_file(filepath)


