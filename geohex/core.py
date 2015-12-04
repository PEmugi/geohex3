# coding: utf-8

from .projection import *
import math

__all__ = ["create_zone", "create_zone_by_code", "meter2hex", "hex2deg", "hex2meter", "deg2hex", "encode", "decode", "create_zones_by_extent"]

HEX_KEY = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

WKB_TMPL = "POLYGON(({0} {1}, {2} {3}, {4} {5}, {6} {7}, {8} {9}, {10} {11}, {0} {1}))"


class Zone(object):
    """Hex Zone"""

    def __init__(self, level, hex_x_no, hex_y_no):
        self._code = encode(level, hex_x_no, hex_y_no)
        self._hex_x_no = hex_x_no
        self._hex_y_no = hex_y_no
        self._level = level
        self._x, self._y = hex2meter(self._level, self._hex_x_no, self._hex_y_no)
        self._lon, self._lat = meter2deg(self._x, self._y)
    
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

    def get_movable_zones(self, distance):

        result = []
        for delta_y in range(-distance, distance + 1):
            minx = -distance + delta_y if delta_y > 0 else -distance
            maxx = distance + delta_y if delta_y < 0 else distance
            for delta_x in range(minx, maxx + 1):
                if delta_x == delta_y == 0: continue
                result.append(Zone(self._level, self._hex_x_no + delta_x, self._hex_y_no + delta_y))

        return result

    def __eq__(self, other):
        return other.code == self._code

    def __hash__(self):
        return hash(self._code)
        

    def get_distance(self, other):
        if self._level != other.level:
            raise Exception("Level must be same")

        delta_x = self._hex_x_no - other.hex_x_no
        delta_y = self._hex_y_no - other.hex_y_no
        abs_delta_x = abs(delta_x)
        abs_delta_y = abs(delta_y)

        if delta_x * delta_y > 0:
            return  abs_delta_x if abs_delta_x > abs_delta_y else abs_delta_y

        return abs_delta_x + abs_delta_y


    def get_vertices(self):
        h_len = HEX_LEN / math.pow(3, self._level)
        half_h_len = h_len / 2
        h_height = half_h_len * math.sqrt(3)
        self._x, self._y = hex2meter(self._level, self._hex_x_no, self._hex_y_no)
        h_top = self._y + h_height
        h_btm = self._y - h_height
        h_l = self._x - h_len
        h_r = self._x + h_len
        h_cl = self._x - half_h_len
        h_cr = self._x + half_h_len

        return ((h_l, self._y),
                (h_cl, h_top),
                (h_cr, h_top),
                (h_r, self._y),
                (h_cr, h_btm),
                (h_cl, h_btm))

    def get_vertices_deg(self):
        return tuple(meter2deg(m[0], m[1]) for m in self.get_vertices())

    def get_wkt(self):
        return WKB_TMPL.format(*reduce(lambda a, b: a+b, self.get_vertices()))
    
    def get_wkt_deg(self):
        return WKB_TMPL.format(*reduce(lambda a, b: a+b, self.get_vertices_deg()))
        


def create_zone(level, lon, lat):
    return Zone(level, *deg2hex(level, lon, lat))


def create_zone_by_code(hexcode):
    return Zone(*decode(hexcode))


def deg2hex(level, lon, lat):
    """degree to hex xy"""
    
    x, y = deg2meter(lon, lat)
    return meter2hex(level, x, y)

def meter2hex(level, x, y):
    """meter to hex xy"""

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

    return int(hex_x_no), int(hex_y_no)


def hex2deg(level, hex_x, hex_y):
    """hex xy to degree"""

    return meter2deg(*hex2meter(level, hex_x, hex_y))

def hex2meter(level, hex_x, hex_y):
    """hex xy to meter"""

    h_len  = HEX_LEN / math.pow(3, level)
    y = (hex_x + hex_y) * h_len * math.sqrt(3) / 2.0
    x = (hex_x - hex_y) * h_len * 3.0 / 2.0

    return x, y
    

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


def create_zones_by_extent(level, minx, miny, maxx, maxy):
    """ """
    
    ll_zone = create_zone(level, minx, miny)
    lr_zone = create_zone(level, maxx, miny)
    ul_zone = create_zone(level, minx, maxy)
    ur_zone = create_zone(level, maxx, maxy)

    #if ll_zone.hex_x_no + ll_zone.hex_y_no > lr_zone.hex_x_no + lr_zone.hex_y_no:
    #    lr_zone = Zone(level, lr_zone.hex_x_no + 1, lr_zone.hex_y_no)
    #elif ll_zone.hex_x_no + ll_zone.hex_y_no < lr_zone.hex_x_no + lr_zone.hex_y_no:
    #    lr_zone = Zone(level, lr_zone.hex_x_no , lr_zone.hex_y_no -1)
    #if ul_zone.hex_x_no + ul_zone.hex_y_no < ur_zone.hex_x_no + ur_zone.hex_y_no:
    #    ur_zone = Zone(level, ur_zone.hex_x_no + 1, ur_zone.hex_y_no)
    #elif ul_zone.hex_x_no + ul_zone.hex_y_no < ur_zone.hex_x_no + ur_zone.hex_y_no:
    #    ur_zone = Zone(level, ur_zone.hex_x_no , ur_zone.hex_y_no -1)
    to_remove = set()
    to_remove.add(Zone(level, ll_zone.hex_x_no - 1, ll_zone.hex_y_no))
    to_remove.add(Zone(level, lr_zone.hex_x_no, lr_zone.hex_y_no - 1))
    to_remove.add(Zone(level, ul_zone.hex_x_no, ul_zone.hex_y_no + 1))
    to_remove.add(Zone(level, ur_zone.hex_x_no + 1, ur_zone.hex_y_no))

    result = set()
    width = lr_zone.get_distance(ll_zone)
    height = ul_zone.get_distance(ll_zone)

    for i in range(0, width // 2 + 1):
        base1 = Zone(level, ll_zone.hex_x_no + i, ll_zone.hex_y_no - i)
        #result.append(base1)
        for j in range(0, height + 1):
            result.add(Zone(level, base1.hex_x_no + j, base1.hex_y_no + j))
        if base1.code != lr_zone.code:
            ##base2 = Zone(level, base1.hex_x_no, base1.hex_y_no -1)
            base2 = Zone(level, base1.hex_x_no + 1, base1.hex_y_no)
            #result.append(base2)
            ##for k in range(0, height + 2):
            ##    result.append(Zone(level, base2.hex_x_no + k, base2.hex_y_no + k))
            for k in range(0, height ):
                result.add(Zone(level, base2.hex_x_no + k, base2.hex_y_no + k))
            
    if ll_zone.get_vertices_deg()[0][1] > miny:
        for i in range(0, width // 2 + 1):
            result.add(Zone(level, ll_zone.hex_x_no + i, ll_zone.hex_y_no - 1 -i))
    if ul_zone.get_vertices_deg()[0][1] < maxy:
        for i in range(0, width // 2 + 1):
            result.add(Zone(level, ul_zone.hex_x_no + 1 + i, ul_zone.hex_y_no - i))
    if ll_zone.get_vertices_deg()[1][0] > minx:
        for i in range(0, height):
            result.add(Zone(level, ll_zone.hex_x_no + i, ll_zone.hex_y_no + 1 + i))
    if lr_zone.get_vertices_deg()[2][0] < maxx:
        for i in range(0, height):
            result.add(Zone(level, lr_zone.hex_x_no + 1 + i, lr_zone.hex_y_no + i))
    return result - to_remove
            

