from .wallet import *

def encode_base10(value):
    sign = ""
    if value < 0:
        sign = "-"
    return sign + encode_base10__internal(abs(value))

