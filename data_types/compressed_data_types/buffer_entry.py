from byte_io import ByteIO
from data_types.ovl_base import OVLBase


class BufferEntry(OVLBase):

    def __init__(self):
        self.index = 0
        self.size = 0

    def read(self, reader: ByteIO):
        self.index = reader.read_uint32()
        self.size = reader.read_uint32()

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        print(f'{prefix}\tindex: {self.index}')
        print(f'{prefix}\tsize: {self.size}')
