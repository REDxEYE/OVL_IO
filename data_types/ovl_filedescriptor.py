from byte_io import ByteIO

from data_types.ovl_base import OVLBase
from utils.hex_utils import to_hex


class OVLFileDescriptor(OVLBase):

    def __init__(self):
        from data_types import OVLMimeType
        self.name = ''
        self.name_offset = 0
        self.file_hash = 0
        self.fragments_count = 0
        self.unknown1 = 0
        self.extension_id = 0
        self.mimetype = OVLMimeType()

    def read(self, reader: ByteIO):
        self.name_offset = reader.read_uint32()
        self.file_hash = reader.read_uint32()
        self.fragments_count = reader.read_uint8()
        self.unknown1 = reader.read_uint8()
        self.extension_id = reader.read_uint16()
        self.mimetype = self.parent.mimetypes[self.extension_id]

        self.name = reader.read_from_offset(0x90 + self.name_offset, reader.read_ascii_string)

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        print(f'{prefix}\tname: {self.name}')
        print(f'{prefix}\tfile_hash: {to_hex(self.file_hash,4)}')
        print(f'{prefix}\tfragments_count: {self.fragments_count}')
        print(f'{prefix}\textension_id: {self.extension_id} ({self.parent.mimetypes[self.extension_id].name})')
