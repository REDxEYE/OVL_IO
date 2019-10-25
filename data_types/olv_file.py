from pathlib import Path
from typing import List

from byte_io import ByteIO
from data_types.ovl_base import OVLBase
from data_types.ovl_mimetype import OVLMimeType
from data_types.ovl_header import OVLHeader


class OVLFile(OVLBase):

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.reader = ByteIO(path=self.filepath)
        self.header = OVLHeader()
        self.mimetypes: List[OVLMimeType] = []

    def read(self):
        reader = self.reader
        self.header.read(reader)
        self.set_x64_mode(self.header.flags1 & 0x08)
        for _ in range(self.header.mimetype_count):
            mime = OVLMimeType()
            mime.register(self)
            mime.read(reader)
            self.mimetypes.append(mime)

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        self.header.print('\t' + prefix)
