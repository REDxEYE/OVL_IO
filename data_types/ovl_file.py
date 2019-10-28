import zlib
from pathlib import Path
from typing import List

from byte_io import ByteIO
from data_types.compressed_data_types.uncompressed_archive import UncompressedArchive
from data_types.olv_unknown import OVLUnknown
from data_types.ovl_base import OVLBase
from data_types.ovl_mimetype import OVLMimeType
from data_types.ovl_header import OVLHeader
from data_types.ovl_filedescriptor import OVLFileDescriptor
from data_types.ovl_archive import OVLArchive
from data_types.ovl_dir import OVLDir
from data_types.ovl_other import OVLOther
from data_types.ovl_texture import OVLTexture
from data_types.ovl_zlibinfo import OVLZlibInfo


class OVLFile(OVLBase):

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.reader = ByteIO(path=self.filepath)
        self.header = OVLHeader()
        self.mimetypes: List[OVLMimeType] = []
        self.file_descriptors: List[OVLFileDescriptor] = []
        self.archives: List[OVLArchive] = []
        self.dirs: List[OVLDir] = []
        self.textures: List[OVLTexture] = []
        self.other: List[OVLOther] = []
        self.unknown: List[OVLUnknown] = []
        self.zlibinfo: List[OVLZlibInfo] = []

        self.uncompressed_archives = []  # type:List[UncompressedArchive]

    def read(self):
        reader = self.reader
        self.header.read(reader)
        self.set_x64_mode(self.header.flags1 & 0x08)
        reader.skip(self.header.names_length)

        for _ in range(self.header.mimetype_count):
            mime = OVLMimeType()
            self.register(mime)
            mime.read(reader)
            self.mimetypes.append(mime)

        for _ in range(self.header.file_count):
            file = OVLFileDescriptor()
            self.register(file)
            file.read(reader)
            self.file_descriptors.append(file)

        archive_name_table_offset = self.reader.tell()
        reader.skip(self.header.archive_names_length)

        for _ in range(self.header.archive_count):
            archive = OVLArchive()
            self.register(archive)
            archive.read(reader, archive_name_table_offset)
            self.archives.append(archive)

        for _ in range(self.header.dir_count):
            o_dir = OVLDir()
            self.register(o_dir)
            o_dir.read(reader)
            self.dirs.append(o_dir)

        for _ in range(self.header.texture_count):
            texture = OVLTexture()
            self.register(texture)
            texture.read(reader)
            self.textures.append(texture)

        for _ in range(self.header.other_count):
            other = OVLOther()
            self.register(other)
            other.read(reader)
            self.other.append(other)

        for _ in range(self.header.ovs_file_count):
            unk = OVLUnknown()
            self.register(unk)
            unk.read(reader)
            self.other.append(unk)

        for _ in range(self.header.archive_count):
            zl = OVLZlibInfo()
            self.register(zl)
            zl.read(reader)
            self.zlibinfo.append(zl)

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        self.header.print('\t' + prefix)
        for mime in self.mimetypes:
            mime.print('\t' + prefix)
        for file in self.file_descriptors:
            file.print('\t' + prefix)
        for archive in self.archives:
            archive.print('\t' + prefix)
        for o_dir in self.dirs:
            o_dir.print('\t' + prefix)
        for tex in self.textures:
            tex.print('\t' + prefix)
        for other in self.other:
            other.print('\t' + prefix)
        for unk in self.unknown:
            unk.print('\t' + prefix)
        for unk in self.zlibinfo:
            unk.print('\t' + prefix)
        for unk in self.uncompressed_archives:
            unk.print('\t' + prefix)

    def read_archives(self):
        for archive in self.archives:
            archive.print()
            if archive.name == 'STATIC':
                archive.uncompressed_data = zlib.decompress(self.reader.read_bytes(archive.compressed_size))
                _path = Path(self.filepath).with_suffix('.static.decompressed')
                with _path.open('wb') as fp:
                    fp.write(archive.uncompressed_data)
                uncompressed = archive.get_uncompressed()
                uncompressed.read()
                self.uncompressed_archives.append(uncompressed)
