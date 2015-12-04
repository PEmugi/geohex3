import math
##
# HALF_EL = equator / 2
# HEX_LEN = length of one side of Hex.
#               ( HALF_EL / 27) * 2
##
HALF_EL = 20037508.34
HEX_LEN = 1484259.877037037

def deg2meter(lon, lat):
    x = lon * HALF_EL / 180.0
    y = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) / (math.pi / 180.0) 
    y *= HALF_EL / 180.0;

    return x, y
    

def meter2deg(x, y):
    lon = (x / HALF_EL) * 180.0
    lat = math.degrees(2 * math.atan(math.exp(math.radians(y / (HALF_EL) * 180))) - math.pi / 2)  

    return lon, lat
