import math
##
# HALF_EL = equator / 2
# HEX_LEN = length of one side of Hex.
#               ( HALF_EL / 27) * 2
##
HALF_EL = 20037408.34
HEX_LEN = 1484252.4696296295 

def deg2meter(lon, lat):
    x = lon * HALF_EL / 180.0
    y = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) / (math.pi / 180.0) 
    y *= HALF_EL / 180.0;

    return x, y
    
