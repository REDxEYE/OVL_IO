from byte_io import ByteIO
from data_types.ovl_base import OVLBase
from utils.hex_utils import to_hex


class DataEntry(OVLBase):

    def __init__(self):
        self.file_hash = 0
        self.ext_hash = 0
        self.file_index = 0
        self.buffer_count = 0
        self.part_array_offset = 0
        self.zero1 = 0
        self.size1 = 0
        self.total_size = 0
        self.file_name = ''
        self.buffers = []
        self.buffer_datas = []

    def read(self, reader: ByteIO):
        self.file_hash = reader.read_uint32()
        self.ext_hash = reader.read_uint32()
        self.file_index = reader.read_uint16()
        self.buffer_count = reader.read_uint16()
        self.zero1 = reader.read_uint32()
        self.size1 = reader.read_uint64()
        self.total_size = reader.read_uint64()

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        print(f'{prefix}\tfile_hash: {to_hex(self.file_hash,4)}')
        print(f'{prefix}\ttype_hash: {to_hex(self.ext_hash,4)}')
        print(f'{prefix}\tfile_index: {self.file_index}')
        print(f'{prefix}\tbuffer_count: {self.buffer_count}')
        print(f'{prefix}\tsize1: {self.size1}')
        print(f'{prefix}\ttotal_size: {self.total_size}')
