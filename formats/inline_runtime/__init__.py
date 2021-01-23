"""

"""

# imports
from typing import Dict

from formats import Binary_Manager
from formats.inline_runtime.v1.irtpc_v1 import IRTPC_v1
from formats.runtime import RTPC_XML_Manager


# class
class IRTPC_XML_Manager(RTPC_XML_Manager):
    VERSIONS: Dict = {
        1: IRTPC_v1
    }


# TODO: Implement this properly
class IRTPC_Manager(Binary_Manager):
    pass
