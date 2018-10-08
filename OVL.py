import os
import zlib
from pprint import pprint
from pathlib import Path

from OVL_COMPRESSED_DATA import *
from OVL_DATA import *


class OVL:
    is_x64 = False
    unknown_type= OVLType()
    def __init__(self, path):
        self.path = Path(path)
        self.reader = ByteIO(self.path.open('rb'))
        self.header = OVLHeader()
        self.types = []  # type:List[OVLType]
        self.files = []  # type:List[OVLFile]
        self.archive_name_table_offset = 0
        self.archives = []  # type: List[OVLArchiveV2]
        self.dirs = []  # type:List[OVLDir]
        self.parts = []  # type:List[OVLPart]
        self.others = []  # type:List[OVLOther]
        self.unknown = []  # type:List[OVLUnk]
        self.archives2 = []  # type:List[OVLArchive2]
        self.static_archive = None  # type: OVLArchiveV2

        self.ovs_headers = []  # type: List[OVSTypeHeader]
        self.ovs_file_headers = []  # type: List[OVSFileDataHeader]
        self.ovs_file3_headers = []  # type: List[OVSAsset]
        self.ovs_file4_headers = []  # type: List[OVSFileSection4]

        self.files_by_hash = {}

    def read(self):
        self.header.read(self.reader)
        self.is_x64 = True  # self.header.flags & 0x08
        self.reader.skip(self.header.names_length)
        for _ in range(self.header.type_count):
            ovl_type = OVLType()
            ovl_type.read(self.reader, is_x64=self.is_x64)
            self.types.append(ovl_type)
        for _ in range(self.header.file_count):
            ovl_file = OVLFile()
            ovl_file.read(self.reader)
            ovl_file.loader = self.types[ovl_file.loader_index]
            self.files.append(ovl_file)
        self.archive_name_table_offset = self.reader.tell()
        self.reader.skip(self.header.archive_names_length)
        for _ in range(self.header.archive_count):
            ovl_archive = OVLArchiveV2()
            ovl_archive.read(self.reader, self.archive_name_table_offset)
            self.archives.append(ovl_archive)
        for _ in range(self.header.dir_count):
            ovl_dir = OVLDir()
            ovl_dir.read(self.reader)
            self.dirs.append(ovl_dir)
        for _ in range(self.header.part_count):
            ovl_part = OVLPart()
            ovl_part.read(self.reader)
            for file in self.files:
                if ovl_part.hash == file.hash:
                    ovl_part.name = file.name
            self.parts.append(ovl_part)
        for _ in range(self.header.other_count):
            ovl_other = OVLOther()
            ovl_other.read(self.reader)
            self.others.append(ovl_other)
        for _ in range(self.header.unknown_count):
            ovl_unk = OVLUnk()
            ovl_unk.read(self.reader)
            self.unknown.append(ovl_unk)
        for _ in range(self.header.archive_count):
            ovl_archive2 = OVLArchive2()
            ovl_archive2.read(self.reader)
            self.archives2.append(ovl_archive2)

        for archive in self.archives:

            if archive.name == 'STATIC':
                archive.uncompressed_data = zlib.decompress(self.reader.read_bytes(archive.packed_size))
                self.static_archive = archive
            else:
                self.reader.seek(archive.ovs_offset)
                archive.uncompressed_data = zlib.decompress(self.reader.read_bytes(archive.packed_size))
            try:
                with open(r'test_data\{}-{}.decompressed'.format(self.path.stem,archive.name), 'wb') as fp:
                    fp.write(self.static_archive.uncompressed_data)
            except:
                pass

    def write(self, writer: ByteIO):
        self.header.write(writer)
        # not all header fields are accurate yet,
        # but we'll come back and re-write this section
        names_start = writer.tell()
        for ovl_type in sorted(self.types, key=lambda x: x.name_offset):
            ovl_type.name_offset = writer.tell() - names_start
            writer.write_ascii_string(ovl_type.name, True)
        for ovl_file in sorted(self.files, key=lambda x: x.name_offset):
            ovl_file.name_offset = writer.tell() - names_start
            writer.write_ascii_string(ovl_file.name, True)
        for ovl_dir in sorted(self.dirs, key=lambda x: x.name_offset):
            ovl_dir.name_offset = writer.tell() - names_start
            writer.write_ascii_string(ovl_dir.name, True)
        for ovl_part in sorted(self.parts, key=lambda x: x.name_offset):
            ovl_part.name_offset = writer.tell() - names_start
            writer.write_ascii_string(ovl_part.name, True)
        for ovl_other in sorted(self.others, key=lambda x: x.name_offset):
            ovl_other.name_offset = writer.tell() - names_start
            writer.write_ascii_string(ovl_other.name, True)
        writer.align(8)
        self.header.names_length = writer.tell() - names_start
        for ovl_type in self.types:
            ovl_type.write(writer, self.is_x64)
        for ovl_file in self.files:
            ovl_file.write(writer)
        archive_name_table_start = writer.tell()
        for ovl_archive in self.archives:
            ovl_archive.nameIndex = writer.tell() - archive_name_table_start
            writer.write_ascii_string(ovl_archive.name, True)
        writer.align(8, archive_name_table_start)
        self.header.archive_names_length = writer.tell() - archive_name_table_start
        for ovl_archive in self.archives:
            ovl_archive.unpacked_size = len(ovl_archive.uncompressed_data)
            ovl_archive.compressed_data = zlib.compress(ovl_archive.uncompressed_data)
            ovl_archive.packed_size = len(ovl_archive.compressed_data)
            ovl_archive.write(writer)
        for ovl_dir in self.dirs:
            ovl_dir.write(writer)
        for ovl_part in self.parts:
            ovl_part.write(writer)
        for ovl_other in self.others:
            ovl_other.write(writer)
        for ovl_unk in self.unknown:
            ovl_unk.write(writer)
        for ovl_archive2 in self.archives2:
            ovl_archive2.write(writer)
        for ovl_archive in self.archives:
            writer.write_bytes(ovl_archive.compressed_data)
        writer.seek(0)
        self.header.write(writer)

    def get_file_by_hash(self, hash_value) ->OVLFile:
        if not self.files_by_hash:
            self.files_by_hash = {f.hash: f for f in self.files}
        return self.files_by_hash.get(hash_value)

    def get_type_by_hash(self, hash_value) ->OVLType:
        for t in self.types:
            if t.type_hash == hash_value:
                return t
        return self.unknown_type

    def read_uncompressed(self):
        archive = self.static_archive
        section_offsets = []
        total_size = 0
        reader = ByteIO(byte_object=archive.uncompressed_data)
        for _ in range(archive.file_type_header_count):
            header = OVSTypeHeader()
            header.read(reader)
            self.ovs_headers.append(header)

        for header in self.ovs_headers:
            header.read_subs(reader)
            for sh in header.subs:
                pass
                total_size += sh.size
                section_offsets.append(sh.offset)
                print(sh)
        offset = 0

        for i in range(archive.file_data_header_count):
            file_header = OVSFileDataHeader()
            file_header.offset = offset
            file_header.read(reader)
            offset += file_header.size
            file_header.file_name = self.get_file_by_hash(file_header.name_hash).name
            self.ovs_file_headers.append(file_header)
            print(file_header)
        # print(reader)
        n3xtab = self.static_archive.embeddedFileCount
        array8 = []
        array9 = [None] * n3xtab
        array10 = []
        for _ in range(n3xtab):
            array8.append(reader.read_int32())
            array10.append(reader.read_int32())
        # print(reader)

        for i in range(archive.asset_count):
            file3_header = OVSAsset()
            file3_header.read(reader)
            if file3_header.chunk_id > 0:
                file3_header.offset = section_offsets[file3_header.chunk_id] + file3_header.offset
            else:
                file3_header.offset = 0
            self.ovs_file3_headers.append(file3_header)
            print(file3_header)

        for i in range(archive.relocation_num):
            file4_header = OVSFileSection4()
            file4_header.read(reader)
            file4_header.offset1 = section_offsets[file4_header.section1] + file4_header.offset1
            file4_header.offset2 = section_offsets[file4_header.section2] + file4_header.offset2
            self.ovs_file4_headers.append(file4_header)
            print(file4_header)
        reader.skip(archive.size_extra)
        section = ByteIO(byte_object=reader.read_bytes(total_size))
        for file_section in self.ovs_file4_headers:
            section.seek(file_section.offset1)
            section.write_uint64(file_section.offset2)
        pos = reader.tell()
        for i in range(len(self.ovs_file_headers)):
            if self.ovs_file_headers[i].type_hash != 193506774:
                for j in range(self.ovs_file_headers[i].size):
                    num17 = self.ovs_file_headers[i].offset + j
                    if array8[num17] == 0:
                        array9[num17] = pos
                        pos += array10[num17]
        for i in range(len(self.ovs_file_headers)):
            if self.ovs_file_headers[i].type_hash != 193506774:
                for j in range(self.ovs_file_headers[i].size):
                    num18 = self.ovs_file_headers[i].offset + j
                    if array8[num18] == 1:
                        array9[num18] = pos
                        pos += array10[num18]
        for i in range(len(self.ovs_file_headers)):
            if self.ovs_file_headers[i].type_hash != 193506774:
                for j in range(self.ovs_file_headers[i].size):
                    num19 = self.ovs_file_headers[i].offset + j
                    array9[num19] = pos
                    pos += array10[num19]
        for i in range(len(self.ovs_file_headers)):
            if self.ovs_file_headers[i].type_hash != 193506774:
                for j in range(self.ovs_file_headers[i].size):
                    num20 = self.ovs_file_headers[i].offset + j
                    if array8[num20] == 2:
                        array9[num20] = pos
                        pos += array10[num20]

        for k in range(len(self.ovs_file_headers)):
            file_header = self.ovs_file_headers[k]
            if file_header.type_hash == 193499543 and file_header.size == 3:
                section_pos = array9[file_header.offset + 1]
                reader.seek(section_pos)
                reader.skip(16)
                num21 = reader.read_int32()
                if num21 != 0:
                    reader.skip(94)
                    num22 = reader.read_int16()
                    reader.skip(256 + 4 + 4 + 4)
                    num23 = reader.read_int32()
                    num24 = reader.read_int32()
                    reader.skip(20 * (num22 - 1))
                    reader.skip(4 * (num22))
                    reader.skip(104 * (num22))
                    num25 = array9[file_header.offset + 1]
                    # fffffff0
                    reader.seek((reader.tell() - num25) + 15 & 0xfffffff0) + num25
                    num26 = reader.read_int32()
                    reader.skip(140)
                    num27 = num26 + 7 & 2147483640
                    reader.skip(num27 * 2)
                    reader.skip(num26 * 64)
                    str = self.path.stem + "_" + hex(file_header.name_hash)
                    print(str)
                    input()

        print(reader)


if __name__ == '__main__':
    model = r'test_data\loc.ovl'
    a = OVL(model)
    a.read()
    # a.read_uncompressed()
    compressed = OVLCompressedData(a, a.static_archive)
    compressed.read(ByteIO(byte_object=a.static_archive.uncompressed_data))
    out = ByteIO(path='test_data/compressed_repacked', mode='w')
    compressed.write(out)
    out.close()
