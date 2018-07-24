from typing import List

from ByteIO import ByteIO


class OVSTypeHeader:

    def __init__(self):
        self.header_type = 0
        self.sub_type_count = 0
        self.subs = []  # type: List[OVSTypeSubHeader]

    def read(self, reader: ByteIO):
        self.header_type, self.sub_type_count = reader.read_fmt('HH')

    def __repr__(self):
        return '<OVS Type header type:{} sub type count:{}>'.format(self.header_type, self.sub_type_count)

    def read_subs(self, reader):
        for _ in range(self.sub_type_count):
            sub = OVSTypeSubHeader()
            sub.read(reader)
            self.subs.append(sub)


class OVSTypeSubHeader:

    def __init__(self):
        self.unk1 = 0
        self.unk2 = 0
        self.size = 0
        self.offset = 0
        self.file_hash = 0
        self.unk6 = 0
        self.type_hash = 0
        self.unk8 = 0

    def read(self, reader: ByteIO):
        self.unk1 = reader.read_uint32()
        self.unk2 = reader.read_uint32()
        self.size = reader.read_uint32()
        self.offset = reader.read_uint32()
        self.file_hash = reader.read_uint32()
        self.unk6 = reader.read_uint32()
        self.type_hash = reader.read_uint32()
        self.unk8 = reader.read_uint32()

    def __repr__(self):
        mems = []
        for m, v in vars(self).items():
            mems.append('{}:{}'.format(m, v))
        return '<OVS sub header {}>'.format(','.join(mems))


class OVSFileDataHeader:

    def __init__(self):
        self.file_hash = 0
        self.type_hash = 0
        self.fileNo = 0
        self.type = 0
        self.unk4 = 0
        self.size1 = 0
        self.size2 = 0
        self.size3_texture = 0
        self.unk9 = 0

    def read(self, reader: ByteIO):
        self.file_hash = reader.read_uint32()
        self.type_hash = reader.read_uint32()
        self.fileNo = reader.read_uint16()
        self.type = reader.read_uint16()
        self.unk4 = reader.read_uint32()
        self.size1 = reader.read_uint32()
        self.size2 = reader.read_uint32()
        self.size3_texture = reader.read_uint32()
        self.unk9 = reader.read_uint32()

    def __repr__(self):
        mems = []
        for m, v in vars(self).items():
            mems.append('{}:{}'.format(m, v))
        return '<OVSFileDataHeader {}>'.format(','.join(mems))


class OVSFileSection3:

    def __init__(self):
        self.file_hash = 0
        self.type_hash = 0
        self.u = 0
        self.offset = 0

    def read(self, reader: ByteIO):
        self.file_hash = reader.read_uint32()
        self.type_hash = reader.read_uint32()
        self.u = reader.read_int32()
        self.offset = reader.read_int32()

    def __repr__(self):
        mems = []
        for m, v in vars(self).items():
            mems.append('{}:{}'.format(m, v))
        return '<OVSFileSection3 {}>'.format(','.join(mems))


class OVSFileSection4:

    def __init__(self):
        self.section1 = 0
        self.offset1 = 0
        self.section2 = 0
        self.offset2 = 0

    def read(self, reader: ByteIO):
        self.section1 = reader.read_uint32()
        self.offset1 = reader.read_uint32()
        self.section2 = reader.read_int32()
        self.offset2 = reader.read_int32()

    def __repr__(self):
        mems = []
        for m, v in vars(self).items():
            mems.append('{}:{}'.format(m, v))
        return '<OVSFileSection4 {}>'.format(','.join(mems))
