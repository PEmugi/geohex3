from geohex3 import deg2hex

def test_deg2hex():
    hex_x, hex_y = deg2hex(139.766084, 35.681382, 4)
    assert hex_x == 417 and hex_y == -149
    
