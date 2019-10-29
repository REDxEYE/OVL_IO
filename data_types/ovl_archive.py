from byte_io import ByteIO
from data_types.compressed_data_types.uncompressed_archive import UncompressedArchive
from data_types.ovl_base import OVLBase


class OVLArchive(OVLBase):

    def __init__(self):
        self.name = ''
        self.name_offset = 0

        self.ovs_head_offset = 0
        self.ovs_file_offset = 0
        self.header_count = 0
        self.data_count = 0
        self.header_type_count = 0

        self.zero = 0

        self.buffer_count = 0

        self.fragment_count = 0
        self.file_count = 0

        self.archive_data_offset = 0

        self.extra_data_size = 0

        self.compressed_size = 0
        self.uncompressed_size = 0

        self.zero3 = 0
        self.ovs_header_offset = 0

        self.header_size = 0

        self.ovs_offset = 0

        self.uncompressed_data = b''  # type: bytes
        self.uncompressed_archive = None

    def read(self, reader: ByteIO, archive_name_table_offset):
        self.name_offset = reader.read_uint32()
        self.ovs_head_offset = reader.read_uint32()
        self.ovs_file_offset = reader.read_uint32()
        self.header_count = reader.read_uint32()
        self.data_count = reader.read_uint16()
        self.header_type_count = reader.read_uint16()
        self.zero = reader.read_uint32()
        self.buffer_count = reader.read_uint32()
        self.fragment_count = reader.read_uint32()
        self.file_count = reader.read_uint32()
        self.archive_data_offset = reader.read_uint32()
        self.extra_data_size = reader.read_uint32()
        self.compressed_size = reader.read_uint32()
        self.uncompressed_size = reader.read_uint32()
        self.zero3 = reader.read_uint32()
        self.ovs_header_offset = reader.read_uint32()
        self.header_size = reader.read_uint32()
        self.ovs_offset = reader.read_uint32()
        self.name = reader.read_from_offset(archive_name_table_offset + self.name_offset, reader.read_ascii_string)

    def get_uncompressed(self):
        self.uncompressed_archive = UncompressedArchive(self)
        return self.uncompressed_archive

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        print(f'{prefix}\tname: {self.name}')
        print(f'{prefix}\tarchive_data_offset: {self.archive_data_offset}')
        print(f'{prefix}\tcompressed_size: {self.compressed_size}')
        print(f'{prefix}\tuncompressed_size: {self.uncompressed_size}')
        print(f'{prefix}\tovs_head_offset: {self.ovs_head_offset}')
        print(f'{prefix}\tovs_file_offset: {self.ovs_file_offset}')
        print(f'{prefix}\tovs_header_offset: {self.ovs_header_offset}')
        print(f'{prefix}\theader_count: {self.header_count}')
        print(f'{prefix}\tdata_count: {self.data_count}')
        print(f'{prefix}\ttype_count: {self.header_type_count}')
        print(f'{prefix}\tbuffer_count: {self.buffer_count}')
        print(f'{prefix}\tfragment_count: {self.fragment_count}')
        print(f'{prefix}\tfile_count: {self.file_count}')
        print(f'{prefix}\textra_data_size: {self.extra_data_size}')
