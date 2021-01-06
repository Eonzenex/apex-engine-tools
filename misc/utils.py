"""
Utility functions
"""


# imports
import os.path
import struct
import xml.etree.ElementTree as et


# functions
def safe_hex(val, fmt: str = 'I', switch: bool = False) -> str:
    if switch:
        fmt = f"<{fmt}"
    else:
        fmt = f">{fmt}"
    new = struct.pack(fmt, val).hex().upper()
    
    return new


def safe_dehex(val, fmt: str = 'I', switch: bool = False) -> int:
    if not isinstance(val, int):
        if isinstance(val, str):
            val = bytes.fromhex(val.lower())
        else:
            val = bytes(val)
    if switch:
        fmt = f"<{fmt}"
    else:
        fmt = f">{fmt}"
    new = struct.unpack(fmt, val)[0]
    
    return new


def align(position: int) -> int:
    return (4 - (position % 4)) % 4


def hex_str_to_int(val: str, big_endian: bool = True) -> int:
    """ Hex string to int. """
    if not big_endian:
        ba = bytearray.fromhex(val)
        ba.reverse()
        s = "".join(format(x, "02x") for x in ba)
        val = s.upper()
    val_bytes: bytes = val.lower().encode("utf-8")
    return int(val_bytes, 16)


def f32_fmt(val: float) -> str:
    if val.is_integer():
        return "{}".format(int(val))
    return "{:.4f}".format(val)


def load_converted(file_path: str) -> et.ElementTree:
    """ Safe XML import. """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Cannot find file: {file_path}")
    
    return et.parse(file_path)


def indent(elem, level=0, symbol: str = "\t"):
    """ Pretty print an et.Element (XML). """
    i = "\n" + level * symbol
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + symbol
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def get_container_count(elem: et.Element):
    count = 0
    for _ in elem:
        count += 1
    return count
