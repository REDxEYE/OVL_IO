from binascii import hexlify
from math import ceil


def to_hex(value: int, bit_len: int = 0):
    bit_len = bit_len if bit_len > 0 else ceil(value.bit_length()/8)
    return hexlify(value.to_bytes(bit_len, 'little')).upper().decode('ascii')


__all__ = [to_hex]
