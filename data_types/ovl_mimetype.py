from byte_io import ByteIO
from data_types.ovl_base import OVLBase
from utils.djb import djb
from utils.hex_utils import to_hex


class OVLMimeType(OVLBase):

    def __init__(self):
        self.name = 'UNKNOWN'
        self.name_offset = 0
        self.unk = 0
        self.mimehash = 0
        self.unk1 = 0
        self.unk2 = 0
        self.file_index_offset = 0
        self.file_count = 0

    def read(self, reader: ByteIO):
        self.name_offset = reader.read_uint32()
        self.unk = reader.read_uint32()
        self.mimehash = reader.read_uint32()
        self.unk1 = reader.read_uint16()
        self.unk2 = reader.read_uint16()
        self.file_index_offset = reader.read_uint32()
        self.file_count = reader.read_uint32()
        self.name = reader.read_from_offset(0x90 + self.name_offset, reader.read_ascii_string)

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        print(f'{prefix}\tname: {self.name}')
        print(f'{prefix}\tmimehash: {to_hex(self.mimehash,4)}')
        print(f'{prefix}\tdjb hash: {to_hex(djb(self.name.split(":")[-1]),4)}')
        print(f'{prefix}\tfile_index_offset: {self.file_index_offset}')
        print(f'{prefix}\tfile_count: {self.file_count}')
