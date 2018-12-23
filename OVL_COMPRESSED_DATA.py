import os
from copy import copy
from pathlib import Path
from typing import List, Dict

from ByteIO import ByteIO
from OVL_DATA import OVLArchiveV2, OVLFileDescriptor
from OVL_Util import OVLBase


class OVLCompressedData(OVLBase):
    def __init__(self, parent, archive: OVLArchiveV2) -> None:
        from OVLFile import OVL
        self.parent: OVL = parent
        self.archive = archive
        self.ovs_headers = []  # type: List[OVSTypeHeader]
        self.ovs_sub_headers = []  # type: List[OVLTypeSubHeader]
        self.ovs_file_headers = []  # type: List[OVLDataHeader]
        self.embedded_file_headers = []  # type: List[OVLEmbeddedFileDescriptor]
        self.ovs_assets = []  # type: List[OVLAsset]
        self.relocations = []  # type: List[OVLRelocation]
        self.extra_data = b''  # type: bytes
        self.buffer = b''  # type: bytes
        self.ovs_cur_pos = 0
        self.reader: ByteIO = None
        self.relocated_reader: ByteIO = None
        self.hash2file_data_header = {}  # type: Dict[int,OVLDataHeader]

    def write_data(self, name, data, ext):
        path = Path('./') / 'extracted' / name
        if not path.parent.exists():
            path.parent.mkdir(exist_ok=True)
        path = path.with_suffix(ext).absolute()
        print('Writting {} bytes to {}'.format(len(data), name))
        with path.open('wb') as fp:
            fp.write(data)

    def read(self, reader: ByteIO):
        self.reader = reader
        section_offsets = []
        total_size = 0
        for _ in range(self.archive.file_type_header_count):
            header = OVSTypeHeader()
            self.register(header)
            header.read(reader)
            self.ovs_headers.append(header)
        for _ in range(self.archive.sub_header_count):
            sub_header = OVLTypeSubHeader()
            self.register(sub_header)
            sub_header.read(reader)
            total_size += sub_header.size
            section_offsets.append(sub_header.offset)
            self.ovs_sub_headers.append(sub_header)

        for i in range(1, len(section_offsets)):
            section_offsets[i] -= section_offsets[0]
        section_offsets[0] = 0

        offset = 0

        for _ in range(self.archive.file_data_header_count):
            file_header = OVLDataHeader()
            self.register(file_header)
            file_header.part_array_offset = offset
            file_header.read(reader)
            offset += file_header.part_count
            file_header.file_name = self.parent.get_file_by_hash(file_header.file_hash).name
            self.hash2file_data_header[file_header.file_hash] = file_header
            self.ovs_file_headers.append(file_header)

        for _ in range(self.archive.embedded_file_count):
            embedded_header = OVLEmbeddedFileDescriptor()
            self.register(embedded_header)
            embedded_header.read(reader)
            self.embedded_file_headers.append(embedded_header)

        for _ in range(self.archive.asset_count):
            asset = OVLAsset()
            self.register(asset)
            asset.read(reader)
            if asset.chunk_id > 0:
                asset.new_offset = section_offsets[asset.chunk_id] + asset.offset
            else:
                asset.new_offset = 0
            self.ovs_assets.append(asset)

        for _ in range(self.archive.relocation_num):
            relocation = OVLRelocation()
            self.register(relocation)
            relocation.read(reader)
            relocation.offset1 = section_offsets[relocation.section1] + relocation.offset1
            relocation.offset2 = section_offsets[relocation.section2] + relocation.offset2
            self.relocations.append(relocation)

        self.extra_data = reader.read_bytes(self.archive.size_extra)

        self.buffer = reader.read_bytes(total_size)
        relocation_buffer = ByteIO(byte_object=copy(self.buffer))

        for relocation in self.relocations:
            relocation_buffer.seek(relocation.offset1)
            relocation_buffer.write_uint32(relocation.offset2)
        self.relocated_reader = relocation_buffer
        self.ovs_cur_pos = reader.tell()


        for file_header in self.ovs_file_headers:
            if file_header.type_hash != 193506774:
                for j in range(file_header.part_count):
                    embedded_header_id = file_header.part_array_offset + j
                    embedded_header = self.embedded_file_headers[embedded_header_id]
                    if embedded_header.archive_id == 0:
                        embedded_header.offset = self.ovs_cur_pos
                        self.ovs_cur_pos += embedded_header.size
        for file_header in self.ovs_file_headers:
            if file_header.type_hash != 193506774:
                for j in range(file_header.part_count):
                    embedded_header_id = file_header.part_array_offset + j
                    embedded_header = self.embedded_file_headers[embedded_header_id]
                    if embedded_header.archive_id == 1:
                        embedded_header.offset = self.ovs_cur_pos
                        self.ovs_cur_pos += embedded_header.size
        for file_header in self.ovs_file_headers:
            if file_header.type_hash == 193506774:
                for j in range(file_header.part_count):
                    embedded_header_id = file_header.part_array_offset + j
                    embedded_header = self.embedded_file_headers[embedded_header_id]
                    embedded_header.offset = self.ovs_cur_pos
                    self.ovs_cur_pos += embedded_header.size
        for file_header in self.ovs_file_headers:
            if file_header.type_hash != 193506774:
                for j in range(file_header.part_count):
                    embedded_header_id = file_header.part_array_offset + j
                    embedded_header = self.embedded_file_headers[embedded_header_id]
                    if embedded_header.archive_id == 2:
                        embedded_header.offset = self.ovs_cur_pos
                        self.ovs_cur_pos += embedded_header.size

        pass

    def get_asset_by_hash(self, file_hash):
        for asset in self.ovs_assets:
            if asset.file_hash == file_hash:
                return asset
        return None

    def read_files(self):
        reader = self.reader
        preader = self.relocated_reader
        for file_header in self.ovs_file_headers:
            print('File "{}" {}'.format(file_header.file.name, file_header.file.type.name))
            print('\t', file_header)
            total = 0
            for i in range(file_header.part_count):
                embedded_file = self.embedded_file_headers[file_header.part_array_offset + i]
                print('\t', embedded_file)
                total += embedded_file.size
            print('Total size:', total)

            if file_header.type_hash == 193499543 and file_header.part_count == 3:
                asset = self.get_asset_by_hash(file_header.file_hash)

                embedded_file = self.embedded_file_headers[file_header.part_array_offset + 1]
                reader.seek(embedded_file.offset)
                reader.skip(16)
                num21 = reader.read_int32()
                bone_pos = []
                bone_rot = []
                bone_parents = {}
                vertexes = []
                normals = []
                weights_bone_ids = []
                weights_weights = []
                uv = []
                faces = []
                if num21:
                    reader.skip(94)
                    num22 = reader.read_int16()
                    reader.skip(256)
                    reader.skip(4)
                    reader.skip(4)
                    reader.skip(4)
                    vertex_count = reader.read_int32()
                    face_count_time3 = reader.read_int32()
                    reader.skip(20 * (num22 - 1))
                    reader.skip(4 * num22)
                    reader.skip(104 * num22)
                    embedded_file = self.embedded_file_headers[file_header.part_array_offset + 1]
                    new_offset = (reader.tell() - embedded_file.offset + 15 & 0xFFFFFFF0) + embedded_file.offset
                    reader.seek(new_offset)

                    bone_count = reader.read_int32()
                    num27 = bone_count + 1
                    reader.skip(140)
                    some_sort_of_ids = reader.read_fmt('H' * num27)
                    reader.skip(bone_count * 64)
                    for bone_id in range(bone_count):
                        pos = reader.read_fmt('fff')
                        reader.read_float()
                        bone_pos.append(pos)
                        pos = reader.read_fmt('fff')
                        reader.read_float()
                        bone_rot.append(pos)
                    for bone_id in range(bone_count):
                        parent_id = reader.read_uint8()
                        bone_parents[bone_id] = parent_id

                    embedded_file = self.embedded_file_headers[file_header.part_array_offset]
                    hash2bone_name = {}
                    reader.seek(embedded_file.offset)
                    names = []
                    name_count = num27 + 1
                    reader.skip(4 * name_count)
                    # reader.seek(embedded_file.offset + 4 * name_count)
                    for _ in range(name_count):
                        names.append(reader.read_ascii_string())
                    reader.seek(embedded_file.offset)
                    for i in range(name_count):
                        name_hash = reader.read_uint32()
                        hash2bone_name[name_hash] = names[i]

                    embedded_file = self.embedded_file_headers[file_header.part_array_offset + 2]
                    reader.seek(embedded_file.offset)
                    # print(embedded_file.size)
                    for i in range(vertex_count):
                        vertex = reader.read_packed_vector()
                        vertexes.append(vertex)
                        x = (reader.read_uint8() - 128) / 128
                        y = (reader.read_uint8() - 128) / 128
                        z = (reader.read_uint8() - 128) / 128
                        normals.append((x, y, z))
                        reader.skip(5)
                        uv.append((reader.read_packed_float16(), reader.read_packed_float16()))
                        reader.skip(4 * 3)
                        reader.skip(3)  # skip tangents
                        weights_bone_ids.extend(reader.read_fmt('bbbb'))
                        weights_weights.extend(map(lambda a: a / 255, reader.read_fmt('bbbb')))
                        reader.skip(4 * 2)
                        pass
                    for i in range(face_count_time3 // 3):
                        faces.append(reader.read_fmt('HHH'))

            path = self.parent.path.parent.absolute() / self.parent.path.stem / 'dump'
            os.makedirs(path, exist_ok=True)
            path /= file_header.file.name
            path = path.with_name(file_header.file.name + file_header.file.type.big_extension)
            print('Saving file to', path)
            with path.open('wb') as buff:
                for i in range(file_header.part_count):
                    embedded_file = self.embedded_file_headers[file_header.part_array_offset + i]
                    reader.seek(embedded_file.offset)
                    buff.write(reader.read_bytes(embedded_file.size))
            print('=' * 20)


    def write(self, writer: ByteIO):  # TODO: FIX IT
        self.archive.file_type_header_count = len(self.ovs_headers)
        for header in self.ovs_headers:
            header.sub_type_count = len(header.subs)
            header.write(writer)
        for chunk_id, sub_header in enumerate(self.ovs_sub_headers):
            sub_header.size = len(self.chunks[chunk_id].data)
            sub_header.write(writer)
        self.archive.file_data_header_count = len(self.ovs_file_headers)
        for file_header in self.ovs_file_headers:
            file_header.write(writer)
        self.archive.embedded_file_count = len(self.embedded_file_headers)
        for embedded_file_id, embedded_file_header in enumerate(self.embedded_file_headers):
            embedded_file_header.size = len(self.embedded_files[embedded_file_id])
            embedded_file_header.write(writer)
        self.archive.asset_count = len(self.ovs_assets)
        for file3_header in self.ovs_assets:
            file3_header.write(writer)
        self.archive.relocation_num = len(self.relocations)
        for file4_header in self.relocations:
            file4_header.write(writer)
        writer.write_bytes(self.extra_data)
        for chunk in self.chunks:
            writer.write_bytes(chunk.data)
        for embedded_file in self.embedded_files:
            writer.write_bytes(embedded_file)


class OVSTypeHeader(OVLBase):

    def __init__(self):
        self.header_type = 0
        self.sub_type_count = 0

    def read(self, reader: ByteIO):
        self.header_type, self.sub_type_count = reader.read_fmt('HH')

    def write(self, writer: ByteIO):
        writer.write_fmt('HH', self.header_type, self.sub_type_count)

    def __repr__(self):
        return '<OVS Type header type:{} sub type count:{}>'.format(self.header_type, self.sub_type_count)


class OVLTypeSubHeader(OVLBase):

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

    @property
    def file(self) -> OVLFileDescriptor:
        return self.parent.parent.get_file_by_hash(self.file_hash)

    @property
    def file_type(self):
        return self.file.type

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


class OVLDataHeader(OVLBase):

    def __init__(self):
        self.file_hash = 0
        self.type_hash = 0
        self.fileNo = 0
        self.part_count = 0
        self.part_array_offset = 0
        self.unk4 = 0
        self.size1 = 0
        self.total_size = 0
        self.file_name = ''

    @property
    def file(self) -> OVLFileDescriptor:
        return self.parent.parent.get_file_by_hash(self.file_hash)

    def read(self, reader: ByteIO):
        self.file_hash = reader.read_uint32()
        self.type_hash = reader.read_uint32()
        self.fileNo = reader.read_uint16()
        self.part_count = reader.read_uint16()
        self.unk4 = reader.read_uint32()
        self.size1 = reader.read_uint64()
        self.total_size = reader.read_uint64()

    def write(self, writer: ByteIO):
        writer.write_uint32(self.file_hash)
        writer.write_uint32(self.type_hash)
        writer.write_uint16(self.fileNo)
        writer.write_uint16(self.part_count)
        writer.write_uint32(self.unk4)
        writer.write_uint64(self.size1)
        writer.write_uint64(self.total_size)

    def __repr__(self):
        return f'<OVSFileDataHeader "{self.file_name}" type hash:{self.type_hash} size:{self.total_size} {self.size1} file_count:{self.part_count} file_array_offset:{self.part_array_offset}>'


class OVLEmbeddedFileDescriptor(OVLBase):
    def __init__(self):
        self.archive_id = 0  # 1 - inside STATIC archive, >1 - external archive, 0 -> inside main file?
        self.size = 0
        self.offset = 0

    def read(self, reader: ByteIO):
        self.archive_id = reader.read_int32()
        self.size = reader.read_int32()

    def write(self, writer: ByteIO):
        writer.write_uint32(self.archive_id)
        writer.write_uint32(self.size)

    def __repr__(self):
        return f'<EmbeddedFileDescriptor archive_id:{self.archive_id} size:{self.size} offset:{self.offset}>'


class OVLAsset(OVLBase):

    def __init__(self):
        self.file_hash = 0
        self.local_type_hash = 0
        self.chunk_id = 0
        self.offset = 0
        self.size = 0
        self.new_offset = 0

    @property
    def file(self) -> OVLFileDescriptor:
        return self.parent.parent.get_file_by_hash(self.file_hash)

    @property
    def file_data_header(self) -> OVLDataHeader:
        return self.parent.hash2file_data_header.get(self.file_hash, None)

    @property
    def name(self) -> str:
        return self.file.name

    @property
    def type(self):
        return self.file.type

    @property
    def type_hash(self) -> int:
        return self.file.type_hash

    def read(self, reader: ByteIO):
        self.file_hash = reader.read_uint32()
        self.local_type_hash = reader.read_uint32()
        self.chunk_id = reader.read_int32()
        self.offset = reader.read_int32()

    def write(self, writer: ByteIO):
        writer.write_uint32(self.file_hash)
        writer.write_uint32(self.local_type_hash)
        writer.write_int32(self.chunk_id)
        writer.write_uint32(self.offset)

    def __repr__(self):
        return f'<OVSAsset "{self.name}" type:{self.type.name} global offset:{self.new_offset} local offset:{self.offset} chunk_id:{self.chunk_id}>'


class OVLRelocation(OVLBase):

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
