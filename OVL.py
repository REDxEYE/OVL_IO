import os
import zlib
from pprint import pprint
from pathlib import Path

from OVL_COMPRESSED_DATA import *
from OVL_DATA import *


class OVL:
    is_x64 = False

    def __init__(self, path):
        self.path = Path(path)
        self.reader = ByteIO(self.path.open('rb'))
        self.header = OVLHeader()
        self.types = []  # type:List[OVLType]
        self.files = []  # type:List[OVLFile]
        self.archive_name_table_offset = 0
        self.archives = []  # type: List[OVLArchiveV2]
        # self.archives = []  # type: List[OVLArchiveV2]
        self.dirs = []  # type:List[OVLDir]
        self.parts = []  # type:List[OVLPart]
        self.others = []  # type:List[OVLOther]
        self.unknown = []  # type:List[OVLUnk]
        self.archives2 = []  # type:List[OVLArchive2]
        self.zlib_data = bytes()
        self.archive: OVLArchiveV2 = None

        self.ovs_headers = []  # type: List[OVSTypeHeader]
        self.ovs_file_headers = []  # type: List[OVSFileDataHeader]
        self.ovs_file3_headers = []  # type: List[OVSFileSection3]
        self.ovs_file4_headers = []  # type: List[OVSFileSection4]

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
            # ovl_archive = OVLArchive()
            ovl_archive = OVLArchiveV2()
            ovl_archive.read(self.reader, self.archive_name_table_offset)
            self.archives.append(ovl_archive)
        # return
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
                self.archive = archive
                compressed_data = self.reader.read_bytes(archive.packed_size)
                uncompressed_data = zlib.decompress(compressed_data)
                self.zlib_data = uncompressed_data
        try:
            with open(r'test_data\{}.decompressed'.format(os.path.basename(self.path)[:-4]), 'wb') as fp:
                fp.write(a.zlib_data)
        except:
            pass

    def get_file_by_hash(self, hash):
        for f in self.files:
            if f.hash == hash and f:
                return f
        return None

    def get_type_by_hash(self, hash):
        for t in self.types:
            if t.type_hash == hash:
                return t
        return None

    def read_uncompressed(self):
        archive = self.archive
        section_offsets = []
        total_size = 0
        reader = ByteIO(byte_object=self.zlib_data)
        for _ in range(archive.headerTypeCnt):
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
        # print(reader)
        offset = 0

        for i in range(archive.fsUnk1Count):
            file_header = OVSFileDataHeader()
            file_header.offset = offset
            file_header.read(reader)
            offset += file_header.size
            file_header.file_name = self.get_file_by_hash(file_header.name_hash).name
            # file_header.type_name = self.get_type_by_hash(file_header.type_hash).name
            self.ovs_file_headers.append(file_header)
            print(file_header)
        # print(reader)
        n3xtab = self.archive.fsUnk2Count
        array8 = []
        array9 = [None] * n3xtab
        array10 = []
        for _ in range(n3xtab):
            array8.append(reader.read_int32())
            array10.append(reader.read_int32())
        # print(reader)

        for i in range(archive.asset_count):
            file3_header = OVSFileSection3()
            file3_header.read(reader)
            if file3_header.u > 0:
                file3_header.offset = section_offsets[file3_header.u] + file3_header.offset
            else:
                file3_header.offset = 0
            self.ovs_file3_headers.append(file3_header)
            print(file3_header)
        # print(reader)

        for i in range(archive.fsUnk4Count):
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
            # print(section.tell())
            section.write_uint64(file_section.offset2)
            print(f'Replacing 00000 on {section.tell()} to {file_section.offset2}')
            # with section.save_current_pos():
            #     section.rewind(8)
            #     print('test',section.peek_int64())
            # print(section.tell())
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
            if file_header.type_hash == 193499543 and file_header.size==3:
                section_pos = array9[file_header.offset+1]
                reader.seek(section_pos)
                reader.skip(16)
                num21 = reader.read_int32()
                if num21!=0:
                    reader.skip(94)
                    num22 = reader.read_int16()
                    reader.skip(256+4+4+4)
                    num23 = reader.read_int32()
                    num24 = reader.read_int32()
                    reader.skip(20*(num22-1))
                    reader.skip(4*(num22))
                    reader.skip(104*(num22))
                    num25 = array9[file_header.offset+1]
#fffffff0
                    reader.seek((reader.tell()-num25)+15 & 0xfffffff0)+num25
                    num26 = reader.read_int32()
                    reader.skip(140)
                    num27 = num26+7 & 2147483640
                    reader.skip(num27*2)
                    reader.skip(num26*64)
                    str = self.path.stem+"_"+hex(file_header.name_hash)
                    print(str)
                    input()

        print(reader)


if __name__ == '__main__':
    # model = r'./test_data/Tyrannosaurus.ovl'
    # sys.argv.append(model)
    # if len(sys.argv) > 1:
    #     model = sys.argv[-1]
    #     a = OVL(model)
    #     a.read()
    #     a.read_uncompressed()
    #     print('##########FILE TYPES##########')
    #     for type_ in a.types:
    #         print(type_)
    #
    #     print('##########FILES##########')
    #     for file in a.files:
    #         print(file)
    #
    # else:
    #     print('You forgot to pass path to file')
    # for file in os.listdir(r'test_data'):
    #     if file.endswith('.ovl'):
    #         model = r'test_data\{}'.format(file)
    #         print(file)
    #         # model = r'test_data\Parasaurolophus.ovl'
    #         a = OVL(model)
    #         a.read()
    #         a.read_uncompressed()
    #         # print(a.header.__dict__)
    #         print(a.archives[0].__dict__)
    #         pprint(a.ovs_headers)
    #         # pprint(a.types)
    #         # pprint(a.files)
    #         # pprint(a.archives)
    #         # pprint(a.dirs)
    #         # pprint(a.parts)
    #         # pprint(a.others)
    #         # pprint(a.unknown)
    #         # pprint(a.archives2)
    # model = r'test_data\velociraptor.ovl'
    model = r'test_data\Parasaurolophus.ovl'
    a = OVL(model)
    a.read()
    print(a.header.__dict__)
    pprint(a.types)
    pprint(a.files)
    print(a.archive.__dict__)
    a.read_uncompressed()
    # for file in a.files:
    #     if file.hash == 2056281489:
    #         print(file)
