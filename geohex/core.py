# coding: utf-8

from .projection import *
import math

__all__ = ["deg2hex", "encode", "decode"]

HEX_KEY = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


class Zone(object):
    """Hex Zone"""

    def __init__(self, level, hex_x_no, hex_y_no):
        self._code = encode(level, hex_x_no, hex_y_no)
        self._hex_x_no = hex_x_no
        self._hex_y_no = hex_y_no
        self._level = level

    
    @property
    def code(self):
        return self._code
    
    @property
    def hex_x_no(self):
        return self._hex_x_no

    @property
    def hex_y_no(self):
        return self._hex_y_no

    @property
    def level(self):
        return self._level

    def get_parent(self):
        return create_zone_by_code(self._code[:-1])

    def get_children(self):
        return [create_zone_by_code(self._code + c) for c in "012345678"]

    def get_neibhor(self):
        result = []
        for x in (-1, 0, 1):
            for y in (-1, 0, 1):
                z = Zone(self._level, self._hex_x_no + x, self._hex_y_no + y)
                result.append(z)
        return result



    def get_distance(self, another):
        pass

    def get_movable_zone(self, distance):
        pass


def create_zone(level, lon, lat):
    return Zone(level, *deg2hex(level, lon, lat))


def create_zone_by_code(hexcode):
    return Zone(*decode(hexcode))


def deg2hex(level, lon, lat):
    """degree to hex xy"""

    x, y = deg2meter(lon, lat)
    h_len  = HEX_LEN / math.pow(3, level)

    hy = y - (1 / math.sqrt(3)) * x
    hx = y + (1 / math.sqrt(3)) * x

    # h_base = 3 * h_len / sqrt(3)
    h_base = h_len * math.sqrt(3)

    hex_x_coord = hx / h_base
    hex_y_coord = hy / h_base

    hex_x_coord_org = math.floor(hex_x_coord)
    hex_y_coord_org = math.floor(hex_y_coord)

    hex_x_no = round(hex_x_coord)
    hex_y_no = round(hex_y_coord)
    #Y > -X + hex_x_coord_org + hex_y_coord_org + 1
    if hex_y_coord >= -hex_x_coord + hex_x_coord_org + hex_y_coord_org + 1:
        #Y > 0.5X + hex_y_coord_org - 0.5hex_x_coord_org
        #Y < 2X - 2hex_x_coord_org + hex_y_coord_org
        if 0.5 * hex_x_coord - 0.5 * hex_x_coord_org + hex_y_coord_org < hex_y_coord \
            < 2.0 * hex_x_coord - 2.0 * hex_x_coord_org + hex_y_coord_org:
            hex_x_no = hex_x_coord_org + 1
            hex_y_no = hex_y_coord_org + 1

    #Y < -X + hex_x_coord_org + hex_y_coord_org + 1
    elif hex_y_coord < -hex_x_coord + hex_x_coord_org + hex_y_coord_org + 1:
        #Y > 2X - 2hex_x_coord_org + hex_y_coord_org - 1
        #Y < 0.5X - 0.5hex_x_coord_org + hex_y_coord_org + 0.5
        if 2.0 * hex_x_coord - 2.0 * hex_x_coord_org + hex_y_coord_org - 1 < hex_y_coord \
                < 0.5 * hex_x_coord - 0.5 * hex_x_coord_org + hex_y_coord_org + 0.5:
            hex_x_no = hex_x_coord_org
            hex_y_no = hex_y_coord_org
        
    x = (hex_x_no * h_base - hex_y_no * h_base) * (math.sqrt(3) / 2)
    if HALF_EL - x < h_len / 2:
        tmp_x_no = hex_x_no
        hex_x_no = hex_y_no
        hex_y_no = tmp_x_no

    return hex_x_no, hex_y_no 


def hex2deg(level, hex_x, hex_y):
    """hex xy to degree"""

    h_len  = HEX_LEN / math.pow(3, level)

    # h_base = 3 * h_len / sqrt(3)
    h_base = h_len * math.sqrt(3)

    hx = hex_x * h_base
    hy = hex_y * h_base
    
    y = (hx + hy) / 2
    x = (hx - hy) * (math.sqrt(3) / 2)

    return meter2deg(x, y)
    

def encode(level, hex_x_no, hex_y_no):
    """encode hex xy to hexcode"""
    
    codes = []
    for i in range(-2, level + 1, 1):
        base = math.pow(3, level - i)
        boundary = math.ceil(base / 2)
        code = 0

        if hex_x_no <= -boundary:
            hex_x_no += base
        elif hex_x_no >= boundary:
            code += 6
            hex_x_no -= base
        else:
            code += 3

        if hex_y_no <= -boundary:
            hex_y_no += base
        elif hex_y_no >= boundary:
            code += 2
            hex_y_no -= base
        else:
            code += 1
            
        codes.append(str(code))

    head_code = int("".join(codes[:3]))
    quotient = head_code // 30
    remainder = head_code % 30

    head_code_hex = HEX_KEY[quotient] + HEX_KEY[remainder]

    return head_code_hex + "".join(codes[3:])


def decode(code):
    """hexcode to hex xy"""

    level = len(code) - 2

    quotient = HEX_KEY.index(code[0])
    remainder = HEX_KEY.index(code[1])
    head_code = "{0:03}".format(quotient * 30 + remainder)
    
    base_code = head_code + code[2:]

    hex_x_no = 0
    hex_y_no = 0

    for i, c in enumerate(base_code):
        x = int(c) // 3
        y = int(c) % 3

        base = math.pow(3, level + 2 - i)

        if x == 0:
            hex_x_no -= base
        elif x == 2:
            hex_x_no += base

        if y == 0:
            hex_y_no -= base
        elif y == 2:
            hex_y_no += base

    return level, int(hex_x_no), int(hex_y_no)

            



        
