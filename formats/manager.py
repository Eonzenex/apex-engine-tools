"""
TODO: Doc string
"""


# imports
import xml.etree.ElementTree as et
from typing import Dict, List
import os.path

from files.file import BinaryFile
from formats import XML_Manager, Binary_Manager
from formats.inline_runtime import IRTPC_XML_Manager, IRTPC_Manager
from formats.runtime import RTPC_XML_Manager, RTPC_Manager
from formats.sarc import SARC_Manager
from misc.errors import UnsupportedXMLTag, MalformedXMLDoc


# functions
def manage_xml(file_path: str, db_path: str):
    """ Manage XML files and process them. """
    XML_TAGS: List = ["rtpc", "irtpc"]
    base_path, filename = os.path.split(file_path)
    
    try:
        xml_file: et.ElementTree = et.parse(file_path)
    except et.ParseError:
        raise MalformedXMLDoc(filename, file_path)
        
    xml_root: et.Element = xml_file.getroot()
    tag: str = xml_root.tag
    
    if tag not in XML_TAGS:
        raise UnsupportedXMLTag(tag, XML_TAGS, file_path)
    
    xml_manage: XML_Manager = XML_Manager()
    if tag == "rtpc":
        xml_manage = RTPC_XML_Manager(file_path=file_path, xml_root=xml_root, db_path=db_path)
    elif tag == "irtpc":
        xml_manage = IRTPC_XML_Manager(file_path=file_path, xml_root=xml_root, db_path=db_path)
    xml_manage.do()


def manage_binary(file_path: str, db_path: str):
    """ Manage binary files and process them. """
    FOUR_CC: Dict = {
        b"RTPC": RTPC_Manager,
        b"SARC": SARC_Manager,
    }
    base_path, filename = os.path.split(file_path)
    pre_file: BinaryFile = BinaryFile(open(file_path, "rb"))
    four_cc: bytes = pre_file.read(4)
    
    manager_class = Binary_Manager
    if four_cc not in FOUR_CC:
        four_cc = pre_file.read(4)
        if four_cc not in FOUR_CC:
            manager_class = IRTPC_Manager
        else:
            manager_class = FOUR_CC[four_cc]
    else:
        manager_class = FOUR_CC[four_cc]

    manager = manager_class(file_path=file_path, db_path=db_path)
    manager.do()
