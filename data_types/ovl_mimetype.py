from byte_io import ByteIO
from data_types.ovl_base import OVLBase


class OVLMimeType(OVLBase):

    def __init__(self):
        self.name = 'UNKNOWN'
        self.name_offset = 0
        self.unk = 0
        self.mimehash = 0
        self.unk1 = 0
        self.unk2 = 0
        self.file_index_offset = 0
        self.file_count = 0

    def read(self,reader:ByteIO):
        if self.is_x64:
            self.name_offset = reader.read_uint64()
        else:
            self.name_offset = reader.read_uint32()
        self.unk = reader.read_uint32()
        self.mimehash = reader.read_uint32()
        self.unk1 = reader.read_uint16()
        self.unk2 = reader.read_uint16()
        self.file_index_offset = reader.read_uint32()
        self.file_count = reader.read_uint32()
        self.name = reader.read_from_offset(0x90 + self.name_offset, reader.read_ascii_string)
