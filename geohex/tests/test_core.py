from geohex import deg2hex, encode, decode

def test_deg2hex():
    hex_x, hex_y = deg2hex(4, 139.766084, 35.681382)
    assert hex_x == 417 and hex_y == -149
    

#def test_hex2deg():
#    deg_x, deg_y = hex2deg(4, 417, -149)
#    assert abs(139.766084 - deg_x) <= 0.00001 and \
#            abs(35.681382 - deg_y) <= 0.00001

def test_encode():
    assert encode(7, -1632, 9851) == "RU6063103"


def test_decode():
    assert decode("RU6063103") == (7, -1632, 9851)


def test_total():
    testcasefile = open("./geohex/tests/testcase.list", "r")
    for line in testcasefile:
        lat, lon, level, hexcode = line.rstrip("\n\r").split(",")
        hex_x, hex_y = deg2hex(int(level), float(lon), float(lat))
        resultcode = encode(int(level), hex_x, hex_y)
        print(resultcode + ":" + hexcode)
        print(hexcode)
        assert resultcode == hexcode
        
