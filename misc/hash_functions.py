"""
Hash functions in a file
Ash Hamilton
26/02/2020
"""


# big boi hash jenkins
def mix_01(a, b, c):
    a &= 0xffffffff
    b &= 0xffffffff
    c &= 0xffffffff
    
    a -= c
    a &= 0xffffffff
    a ^= ((c << 4) + (c >> (32 - 4)))
    a &= 0xffffffff
    c += b
    c &= 0xffffffff
    b -= a
    b &= 0xffffffff
    b ^= ((a << 6) + (a >> (32 - 6)))
    b &= 0xffffffff
    a += c
    a &= 0xffffffff
    c -= b
    c &= 0xffffffff
    c ^= ((b << 8) + (b >> (32 - 8)))
    c &= 0xffffffff
    b += a
    b &= 0xffffffff
    a -= c
    a &= 0xffffffff
    a ^= ((c << 16) + (c >> (32 - 16)))
    a &= 0xffffffff
    c += b
    c &= 0xffffffff
    b -= a
    b &= 0xffffffff
    b ^= ((a << 19) + (a >> (32 - 19)))
    b &= 0xffffffff
    a += c
    a &= 0xffffffff
    c -= b
    c &= 0xffffffff
    c ^= ((b << 4) + (b >> (32 - 4)))
    c &= 0xffffffff
    b += a
    b &= 0xffffffff
    
    return a, b, c


def mix_02(a, b, c, i, length, byte_array):
    if i < length:
        a += byte_array[i]
        i += 1
    
    if i < length:
        a += byte_array[i] << 8
        i += 1
    
    if i < length:
        a += byte_array[i] << 16
        i += 1
    
    if i < length:
        a += byte_array[i] << 24
        i += 1
    
    if i < length:
        b += byte_array[i]
        i += 1
    
    if i < length:
        b += byte_array[i] << 8
        i += 1
    
    if i < length:
        b += byte_array[i] << 16
        i += 1
    
    if i < length:
        b += byte_array[i] << 24
        i += 1
    
    if i < length:
        c += byte_array[i]
        i += 1
    
    if i < length:
        c += byte_array[i] << 8
        i += 1
    
    if i < length:
        c += byte_array[i] << 16
        i += 1
    
    if i < length:
        c += byte_array[i] << 24
    
    return a, b, c


def mix_03(a, b, c):
    a &= 0xffffffff
    b &= 0xffffffff
    c &= 0xffffffff
    
    c ^= b
    c &= 0xffffffff
    c -= ((b << 14) + (b >> (32 - 14)))
    c &= 0xffffffff
    a ^= c
    a &= 0xffffffff
    a -= ((c << 11) + (c >> (32 - 11)))
    a &= 0xffffffff
    b ^= a
    b &= 0xffffffff
    b -= ((a << 25) + (a >> (32 - 25)))
    b &= 0xffffffff
    c ^= b
    c &= 0xffffffff
    c -= ((b << 16) + (b >> (32 - 16)))
    c &= 0xffffffff
    a ^= c
    a &= 0xffffffff
    a -= ((c << 4) + (c >> (32 - 4)))
    a &= 0xffffffff
    b ^= a
    b &= 0xffffffff
    b -= ((a << 14) + (a >> (32 - 14)))
    b &= 0xffffffff
    c ^= b
    c &= 0xffffffff
    c -= ((b << 24) + (b >> (32 - 24)))
    c &= 0xffffffff
    
    return a, b, c


def main(byte_array, index, length, seed):
    a = b = c = 0xDEADBEEF + length + seed
    i = index
    
    while i + 12 < length:
        a += byte_array[i]
        i += 1
        a += (byte_array[i] << 8)
        i += 1
        a += (byte_array[i] << 16)
        i += 1
        a += (byte_array[i] << 24)
        i += 1
        b += byte_array[i]
        i += 1
        b += (byte_array[i] << 8)
        i += 1
        b += (byte_array[i] << 16)
        i += 1
        b += (byte_array[i] << 24)
        i += 1
        c += byte_array[i]
        i += 1
        c += (byte_array[i] << 8)
        i += 1
        c += (byte_array[i] << 16)
        i += 1
        c += (byte_array[i] << 24)
        i += 1
        
        a, b, c = mix_01(a, b, c)
    
    a, b, c = mix_02(a, b, c, i, length, byte_array)
    a, b, c = mix_03(a, b, c)
    
    return c


def split_to_array(input):
    data_array = []
    
    for i in range(len(input)):
        data_array.append(input[i])
        i += 1
    
    return data_array


def ord_to_array(data_array):
    for i in range(len(data_array)):
        data_array[i] = ord(data_array[i])
        i += 1
    
    return data_array


def hash_jenkins(in_data):
    input_array = split_to_array(in_data)
    input_ready = ord_to_array(input_array)
    
    input_len = len(input_ready)
    
    output_uint = main(input_ready, 0, input_len, 0)
    output_hex = hex(output_uint)
    
    output_int = int(output_hex, 16)
    if output_int > 0x7fffffff:
        output_int -= 0x100000000
    
    return output_int, output_hex


def format_hash_jenkins(hash_int, hash_hex):
    str_hash_int = str(hash_int)
    
    str_hash_hex = str(hash_hex.upper())
    str_hash_hex = str_hash_hex[2:].zfill(8)
    
    return str_hash_int, str_hash_hex


# other functions
def endianness(hash_to_work):
    fixed_hash = str()
    for i in range(len(hash_to_work), 0, -2):
        fixed_hash = fixed_hash + hash_to_work[i:i+2]
    return fixed_hash


def int_to_hex(in_data):
    if type(in_data) != int:
        return -1
    
    hex_value = hex(int(in_data))
    clean_hex = hex_value[2:].upper().zfill(8)
    
    return clean_hex
