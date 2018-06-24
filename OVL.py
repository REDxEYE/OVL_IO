import os
import sys
import zlib

from OVL_COMPRESSED_DATA import *
from OVL_DATA import *


class OVL:
    is_x64 = False

    def __init__(self, path):
        self.path = path
        self.reader = ByteIO(path=path)
        self.header = OVLHeader()
        self.types = []  # type:List[OVLType]
        self.files = []  # type:List[OVLFile]
        self.archive_name_table_offset = 0
        self.archives = []  # type: List[OVLArchiveV2]
        self.archives = []  # type:# List[OVLArchive]
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
                # with self.reader.save_current_pos():
                #     a = self.reader.read_uint16()
                #     assert a == 0x9c78
                compressed_data = self.reader.read_bytes(archive.CompressedDataSize)
                uncompressed_data = zlib.decompress(compressed_data)
                self.zlib_data = uncompressed_data
        try:
            with open(r'test_data\{}.decompressed'.format(os.path.basename(self.path)[:-4]), 'wb') as fp:
                fp.write(a.zlib_data)
        except:
            pass

    def read_uncompressed(self):
        archive = self.archive
        reader = ByteIO(byte_object=self.zlib_data)
        for _ in range(archive.headerTypeCnt):
            header = OVSTypeHeader()
            header.read(reader)
            self.ovs_headers.append(header)

        for header in self.ovs_headers:
            header.read_subs(reader)
            for sh in header.subs:
                pass
                # print(sh)
        # print(reader)
        for i in range(archive.fsUnk1Count):
            file_header = OVSFileDataHeader()
            file_header.read(reader)
            self.ovs_file_headers.append(file_header)
            # print(file_header)
        # print(reader)
        reader.skip(archive.fsUnk2Count * 8)
        # print(reader)

        for i in range(archive.fsUnk3Count):
            file3_header = OVSFileSection3()
            file3_header.read(reader)
            self.ovs_file3_headers.append(file3_header)
            # print(file3_header)
        # print(reader)

        for i in range(archive.fsUnk4Count):
            file4_header = OVSFileSection4()
            file4_header.read(reader)
            self.ovs_file4_headers.append(file4_header)
            # print(file4_header)
        # print(reader)


if __name__ == '__main__':
    model = r'test_data\velociraptor.ovl'
    sys.argv.append(model)
    if len(sys.argv) > 1:
        model = sys.argv[-1]
        a = OVL(model)
        a.read()
        a.read_uncompressed()
        print('##########FILE TYPES##########')
        for type_ in a.types:
            print(type_)

        print('##########FILES##########')
        for file in a.files:
            print(file)

    else:
        print('You forgot to pass path to file')
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
    # # model = r'test_data\Parasaurolophus.ovl'
    # a = OVL(model)
    # a.read()
    # print(a.header.__dict__)
    # # pprint(a.files)
    # print(a.archive.__dict__)
    # a.read_uncompressed()
    # for file in a.files:
    #     if file.hash == 2056281489:
    #         print(file)
