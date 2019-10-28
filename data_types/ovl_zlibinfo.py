from byte_io import ByteIO
from data_types.ovl_base import OVLBase


class OVLZlibInfo(OVLBase):

    def __init__(self):
        self.unknown00 = 0
        self.data_size = 0

    def read(self, reader: ByteIO):
        self.unknown00 = reader.read_uint32()
        self.data_size = reader.read_uint32()

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        print(f'{prefix}\tunknown00: {self.unknown00}')
        print(f'{prefix}\tdata_size: {self.data_size}')