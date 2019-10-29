from typing import List

from byte_io import ByteIO
from data_types.compressed_data_types.header_entry import HeaderEntry
from data_types.ovl_base import OVLBase


class HeaderType(OVLBase):

    def __init__(self):
        self.type = 0
        self.sub_header_count = 0
        self.sub_header_types = []  # type:List[HeaderEntry]

    def read(self, reader: ByteIO):
        self.type = reader.read_uint16()
        self.sub_header_count = reader.read_uint16()

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        print(f'{prefix}\ttype: {self.type}')
        print(f'{prefix}\tsub_header_count: {self.sub_header_count}')

