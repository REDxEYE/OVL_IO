from byte_io import ByteIO
from data_types.ovl_base import OVLBase


class OVLDir(OVLBase):

    def __init__(self):
        self.name = ''
        self.name_offset = 0

    def read(self, reader: ByteIO):
        self.name_offset = reader.read_uint32()
        self.name = reader.read_from_offset(0x90 + self.name_offset, reader.read_ascii_string)

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        print(f'{prefix}\tname: {self.name}')