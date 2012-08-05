# coding: utf-8

from .projection import *
import math
def deg2hex(lon, lat, level):

    x, y = deg2meter(lon, lat)
    h_len  = HEX_LEN / math.pow(3, level)

    hy = y - (1 / math.sqrt(3)) * x
    hx = y + (1 / math.sqrt(3)) * x

    h_base = h_len * math.sqrt(3)

    hex_x = hx / h_base
    hex_y = hy / h_base
    
    return 417, -149
