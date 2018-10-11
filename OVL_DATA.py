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
        self.type_count = 0
        self.file_count = 0
        self.file_count2 = 0
        self.part_count = 0
        self.archive_count = 0
        self.unknown30 = 0
        self.unknown34 = 0
        self.unknown38 = 0
        self.unknown3C = 0
        self.unknown_count = 0
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
        self.type_count = reader.read_uint16()
        self.file_count = reader.read_uint32()
        self.file_count2 = reader.read_uint32()
        self.part_count = reader.read_uint32()
        self.archive_count = reader.read_uint32()
        self.unknown30 = reader.read_uint32()
        self.unknown34 = reader.read_uint32()
        self.unknown38 = reader.read_uint32()
        self.unknown3C = reader.read_uint32()
        self.unknown_count = reader.read_uint32()
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

    def write(self, writer: ByteIO):
        writer.write_fourcc(self.sig)
        writer.write_fmt('4B', self.flags, self.version, self.need_bswap, self.unknown07)
        writer.write_uint32(self.flags2)
        writer.write_uint32(self.unknown0C)
        writer.write_uint32(self.names_length)
        writer.write_uint32(self.unknown2_count)
        writer.write_uint32(self.other_count)
        writer.write_uint16(self.dir_count)
        writer.write_uint16(self.type_count)
        writer.write_uint32(self.file_count)
        writer.write_uint32(self.file_count2)
        writer.write_uint32(self.part_count)
        writer.write_uint32(self.archive_count)
        writer.write_uint32(self.unknown30)
        writer.write_uint32(self.unknown34)
        writer.write_uint32(self.unknown38)
        writer.write_uint32(self.unknown3C)
        writer.write_uint32(self.unknown_count)
        writer.write_uint32(self.unknown44)
        writer.write_uint32(self.unknown48)
        writer.write_uint32(self.unknown4C)
        writer.write_uint32(self.archive_names_length)
        writer.write_uint32(self.file_count3)
        writer.write_uint32(self.type_names_length)
        writer.write_uint32(self.zero0C)
        writer.write_uint32(self.zero10)
        writer.write_uint32(self.zero14)
        writer.write_uint32(self.zero18)
        writer.write_uint32(self.zero1C)
        writer.write_uint32(self.zero20)
        writer.write_uint32(self.zero24)
        writer.write_uint32(self.zero28)
        writer.write_uint32(self.zero2C)
        writer.write_uint32(self.zero30)
        writer.write_uint32(self.zero34)
        writer.write_uint32(self.zero38)
        writer.write_uint32(self.zero3C)


class OVLTypeHeader(OVLBase):

    def __init__(self):
        self.name = 'UNKNOWN'
        self.name_offset = 0
        self.type_hash = 0
        self.loader_type = 0
        self.symbol_start = 0
        self.symbols_to_resolve = 0

    @property
    def hash(self):
        return self.type_hash

    def read(self, reader: ByteIO, is_x64=True):
        if is_x64:
            self.name_offset = reader.read_uint64()
        else:
            self.name_offset = reader.read_uint32()
        self.type_hash = reader.read_uint32()
        self.loader_type = reader.read_uint32()
        self.symbol_start = reader.read_uint32()
        self.symbols_to_resolve = reader.read_uint32()
        self.name = reader.read_from_offset(0x90 + self.name_offset, reader.read_ascii_string)

    def write(self, writer: ByteIO, is_x64=True):
        if is_x64:
            writer.write_uint64(self.name_offset)
        else:
            writer.write_uint32(self.name_offset)
        writer.write_uint32(self.type_hash)
        writer.write_uint32(self.loader_type)
        writer.write_uint32(self.symbol_start)
        writer.write_uint32(self.symbols_to_resolve)

    def __repr__(self):
        return '<OVL type "{}" count:{} type_hash:{}>'.format(self.name, self.symbols_to_resolve, self.type_hash)


class OVLFileDescriptor(OVLBase):

    def __init__(self):
        self.name = ''
        self.name_offset = 0
        self.file_hash = 0
        self._type = 0
        self.unknown1 = 0
        self.loader_index = 0
        self.unknown2 = 0

    def read(self, reader: ByteIO):
        self.name_offset = reader.read_uint32()
        self.file_hash = reader.read_uint32()
        self._type = reader.read_uint16()
        self.loader_index = reader.read_uint16()

        self.name = reader.read_from_offset(0x90 + self.name_offset, reader.read_ascii_string)

    @property
    def type(self) -> OVLTypeHeader:
        return self.parent.types[self.loader_index]

    @property
    def type_hash(self):
        return self.type.hash

    @property
    def hash(self):
        return self.file_hash

    def write(self, writer: ByteIO):
        writer.write_uint32(self.name_offset)
        writer.write_uint32(self.file_hash)
        writer.write_uint16(self.type)
        writer.write_uint16(self.loader_index)

    def __repr__(self):
        return '<OVL file "{}" type:{} loader:{} loader id:{} hash:{}>'.format(self.name, self._type, self.type,
                                                                               self.loader_index, self.file_hash)


class OVLArchiveV2(OVLBase):

    def __init__(self):
        self.name = ''
        self.nameIndex = 0

        self.Block1 = 0
        self.Block2 = 0
        self.sub_header_count = 0
        self.file_data_header_count = 0
        self.file_type_header_count = 0

        self.Block5 = 0

        self.embedded_file_count = 0

        self.relocation_num = 0
        self.asset_count = 0

        self.ovs_offset = 0

        self.size_extra = 0

        self.packed_size = 0
        self.unpacked_size = 0

        self.Unknown2 = 0
        self.Unknown3 = 0

        self.Header2Size = 0

        self.Unknown5 = 0

        self.uncompressed_data = None  # type: bytes

    def read(self, reader: ByteIO, archive_name_table_offset):
        self.nameIndex = reader.read_uint32()
        self.Block1 = reader.read_uint32()
        self.Block2 = reader.read_uint32()
        self.sub_header_count = reader.read_uint32()
        self.file_data_header_count = reader.read_uint16()
        self.file_type_header_count = reader.read_uint16()
        self.Block5 = reader.read_uint32()
        self.embedded_file_count = reader.read_uint32()
        self.relocation_num = reader.read_uint32()
        self.asset_count = reader.read_uint32()
        self.ovs_offset = reader.read_uint32()
        self.size_extra = reader.read_uint32()
        self.packed_size = reader.read_uint32()
        self.unpacked_size = reader.read_uint32()
        self.Unknown2 = reader.read_uint32()
        self.Unknown3 = reader.read_uint32()
        self.Header2Size = reader.read_uint32()
        self.Unknown5 = reader.read_uint32()
        self.name = reader.read_from_offset(archive_name_table_offset + self.nameIndex, reader.read_ascii_string)

    def write(self, writer: ByteIO):
        writer.write_uint32(self.nameIndex)
        writer.write_uint32(self.Block1)

        writer.write_uint32(self.Block2)

        writer.write_uint32(self.sub_header_count)
        writer.write_uint16(self.file_data_header_count)
        writer.write_uint16(self.file_type_header_count)
        writer.write_uint32(self.Block5)
        writer.write_uint32(self.embedded_file_count)
        writer.write_uint32(self.relocation_num)
        writer.write_uint32(self.asset_count)
        writer.write_uint32(self.ovs_offset)
        writer.write_uint32(self.size_extra)
        writer.write_uint32(self.packed_size)
        writer.write_uint32(self.unpacked_size)
        writer.write_uint32(self.Unknown2)
        writer.write_uint32(self.Unknown3)
        writer.write_uint32(self.Header2Size)
        writer.write_uint32(self.Unknown5)

    def __repr__(self):
        return '<OVL archive "{}" compressed size:{} uncompressed size:{}>'.format(self.name, self.packed_size,
                                                                                   self.unpacked_size)


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


class OVLPart(OVLBase):

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

    def write(self, writer: ByteIO):
        writer.write_uint32(self.hash)
        writer.write_uint32(self.name_offset)
        writer.write_uint32(self.unknown08)
        writer.write_uint32(self.unknown0C)
        writer.write_uint32(self.unknown10)

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
