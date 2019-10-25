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

    def read(self):
