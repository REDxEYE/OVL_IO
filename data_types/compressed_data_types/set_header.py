from byte_io import ByteIO
from data_types.ovl_base import OVLBase


class SetHeader(OVLBase):

    def __init__(self):
        self.set_count = 0
        self.asset_count = 0
        self.sig_a = 0
        self.sig_b = 0

    def read(self, reader: ByteIO):
        self.set_count = reader.read_uint32()
        self.asset_count = reader.read_uint32()
        self.sig_a = reader.read_uint32()
        self.sig_b = reader.read_uint32()
        assert self.sig_a == 1065336831
        assert self.sig_b == 16909320

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        print(f'{prefix}\tset_count: {self.set_count}')
        print(f'{prefix}\tasset_count: {self.asset_count}')
        print(f'{prefix}\tsig_a: {self.sig_a}')
        print(f'{prefix}\tsig_b: {self.sig_b}')
