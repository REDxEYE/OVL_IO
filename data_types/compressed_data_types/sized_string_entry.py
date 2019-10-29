from typing import List

from byte_io import ByteIO
from data_types.ovl_base import OVLBase
from utils.hex_utils import to_hex


class SizedStringEntry(OVLBase):

    def __init__(self):
        self.file_hash = 0
        self.ext_hash = 0
        self.header_index = 0
        self.data_offset = 0
        self.index = 0
        self.name = ""
        self.extension = ""
        self.header = None
        self.address = 0
        self.children = []  # type:List[SizedStringEntry]

    def read(self, reader: ByteIO):
        self.file_hash = reader.read_uint32()
        self.ext_hash = reader.read_uint32()
        self.header_index = reader.read_int32()
        self.data_offset = reader.read_uint32()

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        print(f'{prefix}\tname: {self.name}')
        print(f'{prefix}\textension: {self.extension}')
        print(f'{prefix}\tfile_hash: {to_hex(self.file_hash,4)}')
        print(f'{prefix}\text_hash: {to_hex(self.ext_hash,4)}')
        print(f'{prefix}\theader_index:{self.header_index}')
        print(f'{prefix}\tdata_offset:{self.data_offset}')
