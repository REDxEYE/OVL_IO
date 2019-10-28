from byte_io import ByteIO
from data_types.ovl_base import OVLBase
from utils.hex_utils import to_hex


class OVLTexture(OVLBase):

    def __init__(self):
        self.hash = 0
        self.name = ''
        self.name_offset = 0
        self.unknown08 = 0
        self.unknown09 = 0
        self.unknown0A = 0
        self.unknown0C = 0
        self.unknown10 = 0

    def read(self, reader: ByteIO):
        self.hash = reader.read_uint32()
        self.name_offset = reader.read_uint32()
        self.name = reader.read_from_offset(0x90 + self.name_offset, reader.read_ascii_string)
        self.unknown08 = reader.read_uint8()
        self.unknown09 = reader.read_uint8()
        self.unknown0A = reader.read_uint16()
        self.unknown0C = reader.read_uint32()
        self.unknown10 = reader.read_uint32()

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        print(f'{prefix}\tname: {self.name}')
        print(f'{prefix}\thash: {to_hex(self.hash,4)}')
        print(f'{prefix}\tunknown08: {self.unknown08}')
        print(f'{prefix}\tunknown09: {self.unknown09}')
        print(f'{prefix}\tunknown0A: {self.unknown0A}')
        print(f'{prefix}\tunknown0C: {self.unknown0C}')
        print(f'{prefix}\tunknown10: {self.unknown10}')
