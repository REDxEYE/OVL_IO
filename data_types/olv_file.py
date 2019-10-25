from pathlib import Path
from typing import List

from byte_io import ByteIO
from data_types.ovl_base import OVLBase
from . import OVLHeader


class OVLFile(OVLBase):

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.reader = ByteIO(path=self.filepath)
        self.header = OVLHeader()
        self.mimetypes:List[] = []

    def read(self):
        reader = self.reader
        self.header.read(reader)

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        self.header.print('\t' + prefix)
