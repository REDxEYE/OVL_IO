from ByteIO import ByteIO


class OVLHeader:

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


class OVLType:

    def __init__(self):
        self.name = ''
        self.name_offset = 0
        self.zero04 = 0
        self.type_hash = 0
        self.loader_type = 0
        self.symbol_start = 0
        self.symbols_to_resolve = 0
        self.Unknown3 = 0
        self.Unknown4 = 0
        self.Unknown5 = 0

    def read(self, reader: ByteIO, is_x64=True):
        self.name_offset = reader.read_uint32()
        if is_x64:
            self.zero04 = reader.read_uint32()
        self.type_hash = reader.read_uint32()
        self.loader_type = reader.read_uint32()
        self.symbol_start = reader.read_uint32()
        self.symbols_to_resolve = reader.read_uint8()
        self.Unknown3 = reader.read_uint8()
        self.Unknown4 = reader.read_uint8()
        self.Unknown5 = reader.read_uint8()
        self.name = reader.read_from_offset(0x90 + self.name_offset, reader.read_ascii_string)

    def __repr__(self):
        return '<OVL type "{}" count:{} type_hash:{}>'.format(self.name, self.symbols_to_resolve,self.type_hash)


class OVLFile:

    def __init__(self):
        self.name = ''
        self.name_offset = 0
        self.hash = 0
        self.type = 0
        self.unknown1 = 0
        self.loader_index = 0
        self.unknown2 = 0
        self.loader: OVLType = None

    def read(self, reader: ByteIO):
        self.name_offset = reader.read_uint32()
        self.hash = reader.read_uint32()
        self.type = reader.read_uint8()
        self.unknown1 = reader.read_uint8()
        self.loader_index = reader.read_uint8()
        self.unknown2 = reader.read_uint8()

        self.name = reader.read_from_offset(0x90 + self.name_offset, reader.read_ascii_string)

    def __repr__(self):
        return '<OVL file "{}" type:{} loader:{} loader id:{} hash:{}>'.format(self.name, self.type, self.loader.name,self.loader_index,self.hash)


# u4 name_offset;
# u4 unknown04 <bgcolor=0xd8d8ff>;
# u4 unknown08 <bgcolor=0xd8d8ff>;
# u4 fh2_count <format=decimal>;
# u2 fh3_count <format=decimal>;
# u2 fh1_count <format=decimal>;
# u4 zero14 <bgcolor=0xd8d8ff>;
# u4 unknown18 <bgcolor=0xd8d8ff>;
# u4 fh6_count <format=decimal>;
# u4 fh5_count <format=decimal>;
# u4 zero24 <bgcolor=0xd8d8ff>;
# u4 unknown28 <bgcolor=0xd8d8ff>;
# u4 comp_size;
# u4 uncomp_size;
# u4 zero34 <bgcolor=0xd8d8ff>;
# u4 unknown38 <bgcolor=0xd8d8ff>;
# u4 header2_size;
# u4 unknown40 <bgcolor=0xd8d8ff>;

class OVLArchive:

    def __init__(self):
        self.name = ''
        self.name_offset = 0
        self.unknown04 = 0
        self.unknown08 = 0
        self.fh2_count = 0
        self.fh3_count = 0
        self.headerTypeCnt = 0
        self.zero14 = 0
        self.unknown18 = 0
        self.file_count = 0
        self.symbol_count = 0
        self.compressed_data_start = 0
        self.unknown28 = 0
        self.comp_size = 0
        self.uncomp_size = 0
        self.zero34 = 0
        self.unknown38 = 0
        self.header2_size = 0
        self.unknown40 = 0

    def read(self, reader: ByteIO, archive_name_table_offset):
        self.name_offset = reader.read_uint32()
        self.name = reader.read_from_offset(archive_name_table_offset + self.name_offset, reader.read_ascii_string)
        self.unknown04 = reader.read_uint32()
        self.unknown08 = reader.read_uint32()
        self.fh2_count = reader.read_uint32()
        self.fh3_count = reader.read_uint16()
        self.headerTypeCnt = reader.read_uint16()
        self.zero14 = reader.read_uint32()
        self.unknown18 = reader.read_uint32()
        self.file_count = reader.read_uint32()
        self.symbol_count = reader.read_uint32()
        self.compressed_data_start = reader.read_uint32()
        self.unknown28 = reader.read_uint32()
        self.comp_size = reader.read_uint32()
        self.uncomp_size = reader.read_uint32()
        self.zero34 = reader.read_uint32()
        self.unknown38 = reader.read_uint32()
        self.header2_size = reader.read_uint32()
        self.unknown40 = reader.read_uint32()

    def __repr__(self):
        return '<OVL archive "{}" compressed size:{} uncompressed size:{}>'.format(self.name, self.comp_size,
                                                                                   self.uncomp_size)


class OVLArchiveV2:

    def __init__(self):
        self.name = ''
        self.nameIndex = 0

        self.Block1a = 0
        self.Block1b = 0
        self.Block2a = 0
        self.Block2b = 0

        self.headerSubTypeCnt = 0

        self.Block3b = 0

        self.fsUnk1Count = 0
        self.headerTypeCnt = 0

        self.Block5a = 0
        self.Block5b = 0

        self.fsUnk2Count = 0

        self.Block6b = 0

        self.fsUnk4Count = 0
        self.fsUnk3Count = 0

        self.compressedDataStart = 0

        self.Unknown1 = 0

        self.CompressedDataSize = 0
        self.DecompressedDataSize = 0

        self.Unknown2 = 0
        self.Unknown3 = 0

        self.Header2Size = 0

        self.Unknown5 = 0

    def read(self, reader: ByteIO, archive_name_table_offset):
        self.nameIndex = reader.read_uint32()
        self.Block1a = reader.read_uint16()
        self.Block1b = reader.read_uint16()
        self.Block2a = reader.read_uint16()
        self.Block2b = reader.read_uint16()
        self.headerSubTypeCnt = reader.read_uint16()
        self.Block3b = reader.read_uint16()
        self.fsUnk1Count = reader.read_uint16()
        self.headerTypeCnt = reader.read_uint16()
        self.Block5a = reader.read_uint16()
        self.Block5b = reader.read_uint16()
        self.fsUnk2Count = reader.read_uint16()
        self.Block6b = reader.read_uint16()
        self.fsUnk4Count = reader.read_uint32()
        self.fsUnk3Count = reader.read_uint32()
        self.compressedDataStart = reader.read_uint32()
        self.Unknown1 = reader.read_uint32()
        self.CompressedDataSize = reader.read_uint32()
        self.DecompressedDataSize = reader.read_uint32()
        self.Unknown2 = reader.read_uint32()
        self.Unknown3 = reader.read_uint32()
        self.Header2Size = reader.read_uint32()
        self.Unknown5 = reader.read_uint32()
        self.name = reader.read_from_offset(archive_name_table_offset + self.nameIndex, reader.read_ascii_string)

    def __repr__(self):
        return '<OVL archive "{}" compressed size:{} uncompressed size:{}>'.format(self.name, self.CompressedDataSize,
                                                                                   self.DecompressedDataSize)


class OVLDir:

    def __init__(self):
        self.name = ''
        self.name_offset = 0

    def read(self, reader: ByteIO):
        self.name_offset = reader.read_uint32()
        self.name = reader.read_from_offset(0x90 + self.name_offset, reader.read_ascii_string)

    def __repr__(self):
        return '<OVL dir "{}">'.format(self.name)


class OVLPart:

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


class OVLOther:

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

    def __repr__(self):
        return '<OVL other "{}">'.format(self.name)


class OVLUnk:

    def __init__(self):
        self.unknown00 = 0
        self.unknown04 = 0
        self.unknown08 = 0

    def read(self, reader: ByteIO):
        self.unknown00 = reader.read_uint32()
        self.unknown04 = reader.read_uint32()
        self.unknown08 = reader.read_uint32()

    def __repr__(self):
        return '<OVL unk {} {} {}>'.format(self.unknown00, self.unknown04, self.unknown08)


class OVLArchive2:

    def __init__(self):
        self.unknown00 = 0
        self.data_size = 0

    def read(self, reader: ByteIO):
        self.unknown00 = reader.read_uint32()
        self.data_size = reader.read_uint32()

    def __repr__(self):
        return '<OVL archive2 {} data size:{}>'.format(self.unknown00, self.data_size)


if __name__ == '__main__':
    a = OVLHeader()
    b = ByteIO(path=r'test_data\Velociraptor.ovl')
    a.read(b)
    print(a.__dict__)
