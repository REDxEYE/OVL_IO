from byte_io import ByteIO
from data_types.ovl_base import OVLBase
from utils.hex_utils import to_hex


class SubHeader(OVLBase):
    def __init__(self):
        self.zero1 = 0
        self.zero2 = 0
        self.size = 0
        self.offset = 0
        self.file_hash = 0
        self.file_count = 0
        self.type_hash = 0
        self.zero3 = 0

    def read(self, reader: ByteIO):
        self.zero1 = reader.read_uint32()
        self.zero2 = reader.read_uint32()
        self.size = reader.read_uint32()
        self.offset = reader.read_uint32()
        self.file_hash = reader.read_uint32()
        self.file_count = reader.read_uint32()
        self.type_hash = reader.read_uint32()
        self.zero3 = reader.read_uint32()

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        print(f'{prefix}\tfile_hash: {to_hex(self.file_hash,4)}')
        print(f'{prefix}\ttype_hash: {to_hex(self.type_hash,4)}')
        print(f'{prefix}\tsize: {self.size}')
        print(f'{prefix}\tfile_count: {self.file_count}')
