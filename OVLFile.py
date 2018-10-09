import zlib
from pathlib import Path
from typing import List

from ByteIO import ByteIO
from OVL_COMPRESSED_DATA import OVLCompressedData
from OVL_DATA import OVLType, OVLArchiveV2, OVLFileDescriptor, OVLDir, OVLArchive2, OVLOther, OVLPart, OVLUnk, OVLHeader
from OVS_TEXTURES import OVSTextureArchive


class OVL:
    is_x64 = False
    unknown_type = OVLType()

    def __init__(self, path):
        self.path = Path(path)
        self.reader = ByteIO(self.path.open('rb'))
        self.header = OVLHeader()
        self.types = []  # type:List[OVLType]
        self.files = []  # type:List[OVLFileDescriptor]
        self.archive_name_table_offset = 0
        self.archives = []  # type: List[OVLArchiveV2]
        self.dirs = []  # type:List[OVLDir]
        self.parts = []  # type:List[OVLPart]
        self.others = []  # type:List[OVLOther]
        self.unknown = []  # type:List[OVLUnk]
        self.archives2 = []  # type:List[OVLArchive2]
        self.static_archive = None  # type: OVLArchiveV2

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
            ovl_file = OVLFileDescriptor()
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
            try:
                if archive.name == 'STATIC':
                    archive.uncompressed_data = zlib.decompress(self.reader.read_bytes(archive.packed_size))
                    self.static_archive = archive
                else:
                    self.reader.seek(archive.ovs_offset)
                    archive.uncompressed_data = zlib.decompress(self.reader.read_bytes(archive.packed_size))

                with open(r'test_data\{}-{}.decompressed'.format(self.path.stem, archive.name), 'wb') as fp:
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

    def get_file_by_hash(self, hash_value) -> OVLFileDescriptor:
        if not self.files_by_hash:
            self.files_by_hash = {f.hash: f for f in self.files}
        return self.files_by_hash.get(hash_value)

    def get_type_by_hash(self, hash_value) -> OVLType:
        for t in self.types:
            if t.type_hash == hash_value:
                return t
        return self.unknown_type


if __name__ == '__main__':
    model = r'test_data\Tyrannosaurus.ovl'
    a = OVL(model)
    a.read()
    # a.read_uncompressed()
    compressed = OVLCompressedData(a, a.static_archive)
    compressed.read(ByteIO(byte_object=a.static_archive.uncompressed_data))
    compressed.read_mesh()
    b = OVSTextureArchive(a)
    b.read()
    # out = ByteIO(path='test_data/compressed_repacked', mode='w')
    # compressed.write(out)
    # out.close()
