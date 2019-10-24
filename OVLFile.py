import sys
import zlib
from pathlib import Path
from typing import List, Dict

from ByteIO import ByteIO
from OVL_COMPRESSED_DATA import OVLCompressedData
from OVL_DATA import OVLMimeType, OVLArchive, OVLFileDescriptor, OVLDir, OVLArchive2, OVLOther, OVLTexture, OVLUnk, OVLHeader
from OVL_Util import OVLBase
from OVS_TEXTURES import OVSTextureArchive


class OVL(OVLBase):
    is_x64 = False
    unknown_type = OVLMimeType()

    def __init__(self, path):
        self.path = Path(path)
        self.reader = ByteIO(self.path.open('rb'))
        self.header = OVLHeader()
        self.types = []  # type:List[OVLMimeType]
        self.files = []  # type:List[OVLFileDescriptor]
        self.archive_name_table_offset = 0
        self.archives = []  # type: List[OVLArchive]
        self.dirs = []  # type:List[OVLDir]
        self.parts = []  # type:List[OVLTexture]
        self.others = []  # type:List[OVLOther]
        self.unknown = []  # type:List[OVLUnk]
        self.archives2 = []  # type:List[OVLArchive2]
        self.static_archive = None  # type: OVLArchive

        self.files_by_hash = {} #type: Dict[int,OVLFileDescriptor]
        self.hash_by_name = {} #type: Dict[str,int]

    def read(self):
        self.header.read(self.reader)
        self.is_x64 = self.header.flags & 0x08
        self.reader.skip(self.header.names_length)

        for _ in range(self.header.mimetype_count):
            ovl_type = OVLMimeType()
            self.register(ovl_type)
            ovl_type.read(self.reader, is_x64=self.is_x64)
            self.types.append(ovl_type)

        for _ in range(self.header.file_count):
            ovl_file = OVLFileDescriptor()
            self.register(ovl_file)
            ovl_file.read(self.reader)
            self.files.append(ovl_file)

        self.files_by_hash = {f.file_hash: f for f in self.files}
        self.hash_by_name = {f.name: f.file_hash for f in self.files}

        self.archive_name_table_offset = self.reader.tell()
        self.reader.skip(self.header.archive_names_length)

        for _ in range(self.header.archive_count):
            ovl_archive = OVLArchive()
            self.register(ovl_archive)
            ovl_archive.read(self.reader, self.archive_name_table_offset)
            self.archives.append(ovl_archive)

        for _ in range(self.header.dir_count):
            ovl_dir = OVLDir()
            self.register(ovl_dir)
            ovl_dir.read(self.reader)
            self.dirs.append(ovl_dir)

        for _ in range(self.header.texture_count):
            ovl_part = OVLTexture()
            self.register(ovl_part)
            ovl_part.read(self.reader)
            for file in self.files:
                if ovl_part.hash == file.file_hash:
                    ovl_part.name = file.name
            self.parts.append(ovl_part)

        for _ in range(self.header.other_count):
            ovl_other = OVLOther()
            self.register(ovl_other)
            ovl_other.read(self.reader)
            self.others.append(ovl_other)

        for _ in range(self.header.ovs_file_count):
            ovl_unk = OVLUnk()
            self.register(ovl_unk)
            ovl_unk.read(self.reader)
            self.unknown.append(ovl_unk)

        for _ in range(self.header.archive_count):
            ovl_archive2 = OVLArchive2()
            self.register(ovl_archive2)
            ovl_archive2.read(self.reader)
            self.archives2.append(ovl_archive2)

        for archive in self.archives:
            print(archive)
            try:
                if archive.name == 'STATIC':
                    archive.uncompressed_data = zlib.decompress(self.reader.read_bytes(archive.compressed_size))
                    self.static_archive = archive
                else:
                    self.reader.seek(archive.zero2)
                    archive.uncompressed_data = zlib.decompress(self.reader.read_bytes(archive.compressed_size))

                with open(r'test_data\{}-{}.decompressed'.format(self.path.stem, archive.name), 'wb') as fp:
                    fp.write(self.static_archive.uncompressed_data)
            except:
                pass

    def get_file_by_hash(self, hash_value) -> OVLFileDescriptor:
        if not self.files_by_hash:
            self.files_by_hash = {f.file_hash: f for f in self.files}
        return self.files_by_hash.get(hash_value)

    def get_type_by_hash(self, hash_value) -> OVLMimeType:
        for t in self.types:
            if t.unk == hash_value:
                return t
        return self.unknown_type


if __name__ == '__main__':
    model = r'test_data\Tyrannosaurus.ovl'
    # model = sys.argv[1]
    # model = r'JWEDinos\Tyrannosaurus\Tyrannosaurus.ovl'
    a = OVL(model)
    a.read()
    # a.read_uncompressed()
    compressed = OVLCompressedData(a, a.static_archive)
    compressed.read(ByteIO(byte_object=a.static_archive.uncompressed_data))
    compressed.read_files()
    b = OVSTextureArchive(compressed)
    b.read()
    # out = ByteIO(path='test_data/compressed_repacked', mode='w')
    # compressed.write(out)
    # out.close()
