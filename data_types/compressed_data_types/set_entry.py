from typing import List

from byte_io import ByteIO

from data_types.ovl_base import OVLBase
from utils.hex_utils import to_hex


class SetEntry(OVLBase):

    def __init__(self):
        self.file_hash = 0
        self.ext_hash = 0
        self.start = 0
        self.name = ""
        self.ext = ""
        self.end = 0
        from data_types.compressed_data_types.asset_entry import AssetEntry
        self.assets = []  # type:List[AssetEntry]

    def read(self, reader: ByteIO):
        self.file_hash = reader.read_uint32()
        self.ext_hash = reader.read_uint32()
        self.start = reader.read_uint32()

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        print(f'{prefix}\tname: {self.name}')
        print(f'{prefix}\text: {self.ext}')
        print(f'{prefix}\tfile_hash: {to_hex(self.file_hash,4)}')
        print(f'{prefix}\text_hash: {to_hex(self.ext_hash)}')
        print(f'{prefix}\tstart: {self.start}')
