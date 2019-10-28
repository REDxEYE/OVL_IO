from typing import List

from byte_io import ByteIO
from data_types.compressed_data_types.header_types import HeaderType
from data_types.compressed_data_types.sub_headers import SubHeader
from data_types.ovl_base import OVLBase


class UncompressedArchive(OVLBase):

    def __init__(self, archive):
        from data_types.ovl_archive import OVLArchive
        self.archive: OVLArchive = archive
        self.reader = ByteIO(byte_object=self.archive.uncompressed_data)
        self.header_types = []  # type:List[HeaderType]
        self.sub_header_types = []  # type:List[SubHeader]

    def read(self):
        reader = self.reader
        for _ in range(self.archive.type_count):
            header = HeaderType()
            self.register(header)
            header.read(reader)
            self.header_types.append(header)
        for _ in range(self.archive.header_count):
                sub_header = SubHeader()
                self.register(sub_header)
                sub_header.read(reader)
                self.sub_header_types.append(sub_header)

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        for header in self.header_types:
            header.print('\t' + prefix)
        for header in self.sub_header_types:
            header.print('\t' + prefix)

