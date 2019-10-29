from byte_io import ByteIO

from data_types.ovl_base import OVLBase


class Fragment(OVLBase):

    def __init__(self):
        self.header_index_0 = 0
        self.data_offset_0 = 0
        self.header_index_1 = 0
        self.data_offset_1 = 0
        self.address_0 = 0
        self.address_1 = 0
        self.data_size_0 = 0
        self.data_size_1 = 0

        from data_types.compressed_data_types.header_entry import HeaderEntry
        self.header_0 = HeaderEntry()
        self.header_1 = HeaderEntry()
        self.name = ''
        self.done = False
        self.sized_str_entry_index = -1

    def read(self, reader: ByteIO):
        self.header_index_0 = reader.read_uint32()
        self.data_offset_0 = reader.read_uint32()
        self.header_index_1 = reader.read_uint32()
        self.data_offset_1 = reader.read_uint32()

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        print(f'{prefix}\theader_index_0: {self.header_index_0}')
        print(f'{prefix}\tdata_offset_0: {self.data_offset_0}')
        print(f'{prefix}\theader_index_1: {self.header_index_1}')
        print(f'{prefix}\tdata_offset_1: {self.data_offset_1}')
