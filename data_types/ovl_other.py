from byte_io import ByteIO
from data_types.ovl_base import OVLBase


class OVLOther(OVLBase):

    def __init__(self):
        self.unknown00 = 0
        self.name = ''
        self.name_offset = 0
        self.unknown08 = 0

    def read(self, reader: ByteIO):
        self.unknown00 = reader.read_uint32()
        self.name_offset = reader.read_uint32()
        self.name = reader.read_from_offset(0x90 + self.name_offset, reader.read_ascii_string)
        self.unknown08 = reader.read_uint32()

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        print(f'{prefix}\tunknown00: {self.unknown00}')
        print(f'{prefix}\tname: {self.name}')
        print(f'{prefix}\tunknown08: {self.unknown08}')
