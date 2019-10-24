# from CTF_ByteIO import ByteIO
from ByteIO import ByteIO
from OVL_Util import OVLBase


class OVLHeader(OVLBase):

    def __init__(self):
        self.sig = ''
        self.flags = 0
        self.version = 0
        self.need_bswap = 0
        self.unknown07 = 0
        self.flags2 = 0
        self.unknown0C = 0
        self.names_length = 0
        self.unknown2_count = 0

        self.other_count = 0
        self.dir_count = 0
        self.mimetype_count = 0
        self.file_count = 0
        self.file_count2 = 0
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
        self.flags, self.version, self.need_bswap, self.unknown07 = reader.read_fmt('4B')
        self.flags2 = reader.read_uint32()
        self.unknown0C = reader.read_uint32()
        self.names_length = reader.read_uint32()
        self.unknown2_count = reader.read_uint32()
        self.other_count = reader.read_uint32()
        self.dir_count = reader.read_uint16()
        self.mimetype_count = reader.read_uint16()
        self.file_count = reader.read_uint32()
        self.file_count2 = reader.read_uint32()
        self.texture_count = reader.read_uint32()
        self.archive_count = reader.read_uint32()
        self.header_types_count = reader.read_uint32()
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

    @property
    def hash(self):
        return self.mimehash

    @property
    def extension(self):
        return '.' + self.name.split(':')[-1]

    @property
    def big_extension(self):
        return '.' + '.'.join(self.name.split(':')[1:])

    def read(self, reader: ByteIO, is_x64=True):
        if is_x64:
            self.name_offset = reader.read_uint64()
        else:
            self.name_offset = reader.read_uint32()
        self.unk = reader.read_uint32()
        self.mimehash = reader.read_uint32()
        self.unk1 = reader.read_uint16()
        self.unk2 = reader.read_uint16()
        self.file_index_offset = reader.read_uint32()
        self.file_count = reader.read_uint32()
        self.name = reader.read_from_offset(0x90 + self.name_offset, reader.read_ascii_string)

    def __repr__(self):
        return '<OVL type "{}" count:{} type_hash:{}>'.format(self.name, self.file_count, self.unk)


class OVLFileDescriptor(OVLBase):

    def __init__(self):
        self.name = ''
        self.name_offset = 0
        self.file_hash = 0
        self.fragments_count = 0
        self.unknown1 = 0
        self.loader_index = 0

    def read(self, reader: ByteIO):
        self.name_offset = reader.read_uint32()
        self.file_hash = reader.read_uint32()
        self.fragments_count = reader.read_uint8()
        self.unknown1 = reader.read_uint8()
        self.loader_index = reader.read_uint16()

        self.name = reader.read_from_offset(0x90 + self.name_offset, reader.read_ascii_string)

    @property
    def type(self) -> OVLMimeType:
        return self.parent.types[self.loader_index]

    @property
    def type_hash(self):
        return self.type.hash

    @property
    def hash(self):
        return self.file_hash

    def __repr__(self):
        return '<OVL file "{}" type:{} loader:{} loader id:{} hash:{}>'.format(self.name, self.fragments_count, self.type,
                                                                               self.loader_index, self.file_hash)


class OVLArchive(OVLBase):

    def __init__(self):
        self.name = ''
        self.name_offset = 0

        self.ovs_header_offset = 0
        self.ovs_file_offset = 0
        self.header_count = 0
        self.data_count = 0
        self.type_count = 0

        self.zero = 0

        self.buffer_count = 0

        self.fragment_count = 0
        self.file_count = 0

        self.zero2 = 0

        self.extra_data_size = 0

        self.compressed_size = 0
        self.uncompressed_size = 0

        self.zero3 = 0
        self.ovs_header_offset = 0

        self.header_size = 0

        self.ovs_offset = 0

        self.uncompressed_data = None  # type: bytes

    def read(self, reader: ByteIO, archive_name_table_offset):
        self.name_offset = reader.read_uint32()
        self.ovs_header_offset = reader.read_uint32()
        self.ovs_file_offset = reader.read_uint32()
        self.header_count = reader.read_uint32()
        self.data_count = reader.read_uint16()
        self.type_count = reader.read_uint16()
        self.zero = reader.read_uint32()
        self.buffer_count = reader.read_uint32()
        self.fragment_count = reader.read_uint32()
        self.file_count = reader.read_uint32()
        self.zero2 = reader.read_uint32()
        self.extra_data_size = reader.read_uint32()
        self.compressed_size = reader.read_uint32()
        self.uncompressed_size = reader.read_uint32()
        self.zero3 = reader.read_uint32()
        self.ovs_header_offset = reader.read_uint32()
        self.header_size = reader.read_uint32()
        self.ovs_offset = reader.read_uint32()
        self.name = reader.read_from_offset(archive_name_table_offset + self.name_offset, reader.read_ascii_string)


    def __repr__(self):
        return '<OVL archive "{}" compressed size:{} uncompressed size:{}>'.format(self.name, self.compressed_size,
                                                                                   self.uncompressed_size)


class OVLDir(OVLBase):

    def __init__(self):
        self.name = ''
        self.name_offset = 0

    def read(self, reader: ByteIO):
        self.name_offset = reader.read_uint32()
        self.name = reader.read_from_offset(0x90 + self.name_offset, reader.read_ascii_string)

    def write(self, writer: ByteIO):
        writer.write_uint32(self.name_offset)

    def __repr__(self):
        return '<OVL dir "{}">'.format(self.name)


class OVLTexture(OVLBase):

    def __init__(self):
        self.hash = 0
        self.name = ''
        self.name_offset = 0
        self.unknown08 = 0
        self.unknown0C = 0
        self.unknown10 = 0

    def read(self, reader: ByteIO):
        self.hash = reader.read_uint32()
        self.name_offset = reader.read_uint32()
        self.name = reader.read_from_offset(0x90 + self.name_offset, reader.read_ascii_string)
        self.unknown08 = reader.read_uint32()
        self.unknown0C = reader.read_uint32()
        self.unknown10 = reader.read_uint32()

    def __repr__(self):
        return '<OVL part "{}">'.format(self.name)


class OVLOther(OVLBase):

    def __init__(self):
        self.unknown00 = 0
        self.name = ''
        self.name_offset = 0
        self.unknown08 = 0

    def read(self, reader: ByteIO):
        self.unknown00 = reader.read_uint32()
        self.name_offset = reader.read_uint32()
        self.name = reader.read_from_offset(0x90 + self.name_offset, reader.read_ascii_string)
        self.unknown08 = reader.read_uint32()

    def write(self, writer: ByteIO):
        writer.write_uint32(self.unknown00)
        writer.write_uint32(self.name_offset)
        writer.write_uint32(self.unknown08)

    def __repr__(self):
        return '<OVL other "{}">'.format(self.name)


class OVLUnk(OVLBase):

    def __init__(self):
        self.unknown00 = 0
        self.unknown08 = 0

    def read(self, reader: ByteIO):
        self.unknown00 = reader.read_uint32()
        self.unknown08 = reader.read_uint64()

    def write(self, writer: ByteIO):
        writer.write_uint32(self.unknown00)
        writer.write_uint64(self.unknown08)

    def __repr__(self):
        return '<OVL unk {} {}>'.format(self.unknown00, self.unknown08)


class OVLArchive2(OVLBase):

    def __init__(self):
        self.unknown00 = 0
        self.data_size = 0

    def read(self, reader: ByteIO):
        self.unknown00 = reader.read_uint32()
        self.data_size = reader.read_uint32()

    def write(self, writer: ByteIO):
        writer.write_uint32(self.unknown00)
        writer.write_uint32(self.data_size)

    def __repr__(self):
        return '<OVL archive2 {} data size:{}>'.format(self.unknown00, self.data_size)


if __name__ == '__main__':
    a = OVLHeader()
    b = ByteIO(path=r'/test_data\Velociraptor.ovl')
    a.read(b)
    print(a.__dict__)
