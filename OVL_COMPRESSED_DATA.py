from pathlib import Path
from typing import List

from ByteIO import ByteIO
# from CTF_ByteIO import ByteIO
from OVL_DATA import OVLArchiveV2


class OVLCompressedData:
    def __init__(self, parent, archive: OVLArchiveV2):
        from OVL import OVL
        self.parent: OVL = parent
        self.archive = archive
        self.ovs_headers = []  # type: List[OVSTypeHeader]
        self.ovs_file_headers = []  # type: List[OVSFileDataHeader]
        self.embedded_file_headers = []  # type: List[EmbeddedFileDescriptor]
        self.ovs_file3_headers = []  # type: List[OVSFileSection3]
        self.ovs_file4_headers = []  # type: List[OVSFileSection4]
        self.chunks = []  # type: List[OVSChunk]
        self.embedded_files = []  # type: List[bytes]
        self.extra_data = []  # type: bytes

    def read(self, reader: ByteIO):
        section_offsets = []
        total_size = 0
        for _ in range(self.archive.file_type_header_count):
            header = OVSTypeHeader()
            header.read(reader)
            self.ovs_headers.append(header)
        for header in self.ovs_headers:
            header.read_subs(reader)
            for sub_header in header.subs:
                total_size += sub_header.size
                section_offsets.append(sub_header.offset)

        offset = 0
        for _ in range(self.archive.file_data_header_count):
            file_header = OVSFileDataHeader()
            file_header.offset = offset
            file_header.read(reader)
            offset += file_header.size
            file_header.file_name = self.parent.get_file_by_hash(file_header.name_hash).name
            self.ovs_file_headers.append(file_header)

        for _ in range(self.archive.embeddedFileCount):
            embedded_file = EmbeddedFileDescriptor()
            embedded_file.read(reader)
            self.embedded_file_headers.append(embedded_file)

        for _ in range(self.archive.asset_count):
            file3_header = OVSFileSection3()
            file3_header.read(reader)
            file3_header.name = self.parent.get_file_by_hash(file3_header.name_hash).name
            if file3_header.chunk_id > 0:
                file3_header.offset = section_offsets[file3_header.chunk_id] + file3_header.offset
            else:
                file3_header.offset = 0
            self.ovs_file3_headers.append(file3_header)

        for _ in range(self.archive.fsUnk4Count):
            file4_header = OVSFileSection4()
            file4_header.read(reader)
            file4_header.offset1 = section_offsets[file4_header.section1] + file4_header.offset1
            file4_header.offset2 = section_offsets[file4_header.section2] + file4_header.offset2
            self.ovs_file4_headers.append(file4_header)
        self.extra_data = reader.read_bytes(self.archive.size_extra)
        all_sub_headers = [sub for header in self.ovs_headers for sub in header.subs]
        for sub_header in all_sub_headers:
            reader.seek(sub_header.offset)
            chunk = OVSChunk(self, sub_header)
            chunk.read(reader)
            chunk.save('./')
            self.chunks.append(chunk)
        for embedded_file_header in self.embedded_file_headers:
            self.embedded_files.append(reader.read_bytes(embedded_file_header.size))

        # assert reader.tell() == reader.size()

    def write(self, writer: ByteIO):
        self.archive.file_type_header_count = len(self.ovs_headers)
        for header in self.ovs_headers:
            header.sub_type_count = len(header.subs)
            header.write(writer)
        for chunk_id, sub_header in enumerate(sub_header for header in self.ovs_headers for sub_header in header.subs):
            sub_header.size = len(self.chunks[chunk_id].data)
            sub_header.write(writer)
        self.archive.file_data_header_count = len(self.ovs_file_headers)
        for file_header in self.ovs_file_headers:
            file_header.write(writer)
        self.archive.embeddedFileCount = len(self.embedded_file_headers)
        for embedded_file_id, embedded_file_header in enumerate(self.embedded_file_headers):
            embedded_file_header.size = len(self.embedded_files[embedded_file_id])
            embedded_file_header.write(writer)
        self.archive.asset_count = len(self.ovs_file3_headers)
        for file3_header in self.ovs_file3_headers:
            file3_header.write(writer)
        self.archive.fsUnk4Count = len(self.ovs_file4_headers)
        for file4_header in self.ovs_file4_headers:
            file4_header.write(writer)
        writer.write_bytes(self.extra_data)
        for chunk in self.chunks:
            writer.write_bytes(chunk.data)
        for embedded_file in self.embedded_files:
            writer.write_bytes(embedded_file)


class OVSChunk:

    def __init__(self, parent: OVLCompressedData, header: 'OVSTypeSubHeader'):
        self.parent = parent
        self.header: OVSTypeSubHeader = header
        self.data: bytes = None

    @property
    def chunk_name(self):
        return self.file.name

    @property
    def file(self):
        return self.parent.parent.get_file_by_hash(self.header.file_hash)

    @property
    def chunk_type(self):
        return self.file.loader.name

    def read(self, reader: ByteIO):
        self.data = reader.read_bytes(self.header.size)

    def __repr__(self):
        return '<OVSChunk "{}" name:"{}">'.format(self.chunk_type, self.chunk_name)

    @property
    def file_ext(self):
        return self.chunk_type.split(':')[1]

    def save(self,path):
        if type(path) is not Path:
            path = Path(path)
        path = path/'extracted'/self.file.name
        if not path.parent.exists():
            path.parent.mkdir(exist_ok=True)
        path = path.with_suffix('.'+self.file_ext)
        with path.open('wb') as fp:
            fp.write(self.data)



class OVSTypeHeader:

    def __init__(self):
        self.header_type = 0
        self.sub_type_count = 0
        self.subs = []  # type: List[OVSTypeSubHeader]

    def read(self, reader: ByteIO):
        self.header_type, self.sub_type_count = reader.read_fmt('HH')

    def write(self, writer: ByteIO):
        writer.write_fmt('HH', self.header_type, self.sub_type_count)

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

    def write(self, writer: ByteIO):
        writer.write_uint32(self.unk1)
        writer.write_uint32(self.unk2)
        writer.write_uint32(self.size)
        writer.write_uint32(self.offset)
        writer.write_uint32(self.file_hash)
        writer.write_uint32(self.unk6)
        writer.write_uint32(self.type_hash)
        writer.write_uint32(self.unk8)

    def __repr__(self):
        mems = []
        for m, v in vars(self).items():
            mems.append('{}:{}'.format(m, v))
        return '<OVS sub header {}>'.format(','.join(mems))


class OVSFileDataHeader:

    def __init__(self):
        self.name_hash = 0
        self.type_hash = 0
        self.fileNo = 0
        self.size = 0
        self.offset = 0
        self.unk4 = 0
        self.size1 = 0
        self.size2 = 0
        # self.size3_texture = 0
        # self.unk9 = 0
        self.file_name = ''

    def read(self, reader: ByteIO):
        self.name_hash = reader.read_uint32()
        self.type_hash = reader.read_uint32()
        self.fileNo = reader.read_uint16()
        self.size = reader.read_uint16()
        self.unk4 = reader.read_uint32()
        self.size1 = reader.read_uint64()
        self.size2 = reader.read_uint64()
        # self.size3_texture = reader.read_uint32()
        # self.unk9 = reader.read_uint32()

    def write(self, writer: ByteIO):
        writer.write_uint32(self.name_hash)
        writer.write_uint32(self.type_hash)
        writer.write_uint16(self.fileNo)
        writer.write_uint16(self.size)
        writer.write_uint32(self.unk4)
        writer.write_uint64(self.size1)
        writer.write_uint64(self.size2)

    def __repr__(self):
        return f'<OVSFileDataHeader "{self.name_hash}" type hash:{self.type_hash} size:{self.size} offset:{self.offset}>'


class EmbeddedFileDescriptor:
    def __init__(self):
        self.unk1 = 0
        self.size = 0

    def read(self, reader: ByteIO):
        self.unk1 = reader.read_int32()
        self.size = reader.read_int32()

    def write(self, writer: ByteIO):
        writer.write_uint32(self.unk1)
        writer.write_uint32(self.size)

    def __repr__(self):
        return f'<EmbeddedFileDescriptor unk1={self.unk1} size={self.size}>'


class OVSFileSection3:

    def __init__(self):
        self.name_hash = 0
        self.type_hash = 0
        self.chunk_id = 0
        self.offset = 0

    def read(self, reader: ByteIO):
        self.name_hash = reader.read_uint32()
        self.type_hash = reader.read_uint32()
        self.chunk_id = reader.read_int32()
        self.offset = reader.read_int32()

    def write(self, writer: ByteIO):
        writer.write_uint32(self.name_hash)
        writer.write_uint32(self.type_hash)
        writer.write_uint32(self.chunk_id)
        writer.write_uint32(self.offset)

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

    def write(self, writer: ByteIO):
        writer.write_uint32(self.section1)
        writer.write_uint32(self.offset1)
        writer.write_int32(self.section2)
        writer.write_int32(self.offset2)

    def __repr__(self):
        mems = []
        for m, v in vars(self).items():
            mems.append('{}:{}'.format(m, v))
        return '<OVSFileSection4 {}>'.format(','.join(mems))
