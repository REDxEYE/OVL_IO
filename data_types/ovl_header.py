from byte_io import ByteIO
from data_types.ovl_base import OVLBase


class OVLHeader(OVLBase):

    def __init__(self):
        self.sig = ''  # FRES
        self.flags1 = 0
        self.version = 0
        self.need_bswap = 0
        self.unk07 = 0
        self.flags2 = 0

        self.names_length = 0
        self.unknown2_count = 0
        self.other_count = 0
        self.dir_count = 0
        self.mimetype_count = 0
        self.file_count = 0
        self.file2_count = 0
        self.texture_count = 0
        self.archive_count = 0
        self.header_type_count = 0
        self.header_count = 0
        self.data_count = 0
        self.buffer_count = 0
        self.ovs_file_count = 0
        self.unknown44 = 0
        self.unknown48 = 0
        self.unknown4C = 0
        self.archive_names_length = 0
        self.file_count3 = 0
        self.type_names_length = 0
        self.zero0C = 0
        self.zero10 = 0
        self.zero14 = 0
        self.zero18 = 0
        self.zero1C = 0
        self.zero20 = 0
        self.zero24 = 0
        self.zero28 = 0
        self.zero2C = 0
        self.zero30 = 0
        self.zero34 = 0
        self.zero38 = 0
        self.zero3C = 0

    def read(self, reader: ByteIO):
        self.sig = reader.read_fourcc()
        assert self.sig == 'FRES'
        self.flags1, self.version, self.need_bswap, self.unk07 = reader.read_fmt('4B')
        self.flags2 = reader.read_uint32()
        self.unk07 = reader.read_uint32()
        self.names_length = reader.read_uint32()
        self.unknown2_count = reader.read_uint32()
        self.other_count = reader.read_uint32()
        self.dir_count = reader.read_uint16()
        self.mimetype_count = reader.read_uint16()
        self.file_count = reader.read_uint32()
        self.file2_count = reader.read_uint32()
        self.texture_count = reader.read_uint32()
        self.archive_count = reader.read_uint32()
        self.header_type_count = reader.read_uint32()
        self.header_count = reader.read_uint32()
        self.data_count = reader.read_uint32()
        self.buffer_count = reader.read_uint32()
        self.ovs_file_count = reader.read_uint32()
        self.unknown44 = reader.read_uint32()
        self.unknown48 = reader.read_uint32()
        self.unknown4C = reader.read_uint32()
        self.archive_names_length = reader.read_uint32()
        self.file_count3 = reader.read_uint32()
        self.type_names_length = reader.read_uint32()
        self.zero0C = reader.read_uint32()
        self.zero10 = reader.read_uint32()
        self.zero14 = reader.read_uint32()
        self.zero18 = reader.read_uint32()
        self.zero1C = reader.read_uint32()
        self.zero20 = reader.read_uint32()
        self.zero24 = reader.read_uint32()
        self.zero28 = reader.read_uint32()
        self.zero2C = reader.read_uint32()
        self.zero30 = reader.read_uint32()
        self.zero34 = reader.read_uint32()
        self.zero38 = reader.read_uint32()
        self.zero3C = reader.read_uint32()

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        print(f'{prefix}\tflag1:{self.flags1}')
        print(f'{prefix}\tflags2:{self.flags2}')
        print(f'{prefix}\tversion:{self.version}')
        print(f'{prefix}\tneed_bswap:{self.need_bswap}')
        print(f'{prefix}\tunknown2_count:{self.unknown2_count}')
        print(f'{prefix}\tother_count:{self.other_count}')
        print(f'{prefix}\tdir_count:{self.dir_count}')
        print(f'{prefix}\tmimetype_count:{self.mimetype_count}')
        print(f'{prefix}\tfile_count:{self.file_count}')
        print(f'{prefix}\tfile2_count:{self.file2_count}')
        print(f'{prefix}\tfile_count3:{self.file_count3}')
        print(f'{prefix}\ttexture_count:{self.texture_count}')
        print(f'{prefix}\tarchive_count:{self.archive_count}')
        print(f'{prefix}\theader_type_count:{self.header_type_count}')
        print(f'{prefix}\theader_count:{self.header_count}')
        print(f'{prefix}\tdata_count:{self.data_count}')
        print(f'{prefix}\tbuffer_count:{self.buffer_count}')
        print(f'{prefix}\tovs_file_count:{self.ovs_file_count}')
