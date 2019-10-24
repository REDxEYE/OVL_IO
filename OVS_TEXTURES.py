from typing import Dict, Any, Tuple

from PIL import Image

from ByteIO import ByteIO


class OVSResourceHeader:
    def __init__(self) -> None:
        self.offset = 0
        self.size = 0

    def __repr__(self):
        return f'<OVSResourceHeader size:{self.size} offset:{self.offset}>'


class OVSTextureArchive:

    def __init__(self, parent):
        from OVL_COMPRESSED_DATA import OVLCompressedData
        self.parent: OVLCompressedData = parent

        self.readers = []
        self.resources = {}  # type: Dict[int,OVSResourceHeader]
        if len(self.parent.parent.archives) > 1:
            self.textures_1 = self.parent.parent.path.with_suffix('.ovs.textures_l1')
            self.reader_t1 = ByteIO(file=self.textures_1.open('rb')).unzip()
            self.readers.append(self.reader_t1)
            self.read_archive(self.reader_t1)
        if len(self.parent.parent.archives) > 2:
            self.textures_2 = self.parent.parent.path.with_suffix('.ovs.textures_l0')
            self.reader_t2 = ByteIO(file=self.textures_2.open('rb')).unzip()
            self.readers.append(self.reader_t2)
        else:
            pass
            # print('INVALID')
            # exit(0xDEAD)

    def read(self):
        for reader in self.readers:
            self.read_archive(reader)
        self.extract_textures()

    def read_archive(self, archive_reader: ByteIO):
        reader = archive_reader
        temp1 = reader.read_fmt('III')
        # reader.skip(12)
        num43 = reader.read_int32()
        temp2 = reader.read_fmt('II')
        # reader.skip(4 * 2)
        num44 = reader.read_int32()
        temp3 = reader.read_fmt('II')
        # reader.skip(4 * 2)

        images_start = reader.tell() + (56 * num44) + 16 + num43
        for i in range(num44):
            image_hash = reader.read_uint32()
            reader.skip(20)
            image_size = reader.read_int32()
            reader.skip(4)
            resource = OVSResourceHeader()
            resource.offset = images_start
            resource.size = image_size
            self.resources[image_hash] = resource
            images_start += image_size

    def extract_textures(self):
        preader = self.parent.relocated_reader
        for asset in self.parent.ovs_assets:
            if asset.type_hash == 193506774:
                preader.seek(asset.new_offset)
                preader.skip(8 * 3)
                data_offset = preader.read_int64()
                texture_format = preader.read_int16()
                storage_id = preader.read_int8()
                preader.seek(data_offset + 8)
                preader.read_int32()
                width = preader.read_int32()
                height = preader.read_int32()
                preader.skip(4)
                layers = preader.read_int32()
                if layers > 1:
                    height *= layers
                preader.skip(4)
                pixel_mode = ('raw', 'RGBA', 0, 1)  # type: Tuple[str,Any,int]
                out_mode = 'RGBA'
                if texture_format == 102:
                    pixel_mode = ('bcn', 4, 0)
                    out_mode = 'L'
                elif texture_format == 103:
                    pixel_mode = ('bcn', 5, 0)
                elif texture_format == 107:
                    pixel_mode = ('bcn', 7, 0)
                elif texture_format == 96:
                    pixel_mode = ('bcn', 1, 0)
                elif texture_format == 108:
                    pixel_mode = ('bcn', 7, 0)
                else:
                    print('UNKNOWN FORMAT', texture_format)
                if self.parent.parent.files_by_hash.get(asset.file_hash, False):
                    texture_file = self.parent.parent.files_by_hash[asset.file_hash]
                    texture_name = texture_file.name
                    texture_lod_name = texture_name + '_lod0'
                    lod_hash = self.parent.parent.hash_by_name.get(texture_lod_name, 0)
                    path = self.parent.parent.path.parent.absolute() / self.parent.parent.path.stem / texture_name
                    path = path.with_name(path.name + '.tga')
                    path = path.absolute()
                    print('TEXTURE', texture_name, width, height, texture_format)
                    if storage_id == 1:
                        file_data_header = asset.file_data_header
                        if file_data_header:
                            part_id = file_data_header.part_array_offset + 1
                            embedded_file_header = self.parent.embedded_file_headers[part_id]
                            print(embedded_file_header)
                            self.parent.reader.seek(embedded_file_header.offset)
                            image_data = self.parent.reader.read_bytes(embedded_file_header.size)
                            image = Image.frombuffer(out_mode, (width, height), image_data, *pixel_mode)
                            image.split()[-1].save(path.with_name(path.stem + '_ALPHA.tga'))
                            image = image.convert('RGB')
                            image.save(path)
                    elif storage_id > 1:
                        reader = self.readers[storage_id - 2]
                        resource = self.resources.get(lod_hash, None)
                        if resource is not None:
                            print(resource)
                            reader.seek(resource.offset)
                            image_data = reader.read_bytes(resource.size)
                            image = Image.frombuffer('RGBA', (width, height), image_data, *pixel_mode)
                            image.split()[-1].save(path.with_name(path.stem + '_ALPHA.tga'))
                            image = image.convert('RGB')
                            image.save(path)
                        else:
                            print('ERROR')

                else:
                    print('Texture not found')
            if asset.header_index != -1:
                file = self.parent.parent.files_by_hash.get(asset.file_hash)
                preader.seek(asset.new_offset)
                if asset.type_hash == 2218662654:
                    string_offsets = []
                    strings = []
                    string_count = preader.read_uint64()
                    string_table_offset = preader.read_uint64()
                    preader.seek(string_table_offset)
                    for _ in range(string_count):
                        string_offset = preader.read_uint64()
                        string_offsets.append(string_offset)
                    for string_offset in string_offsets:
                        preader.seek(string_offset)
                        strings.append(preader.read_ascii_string())
                    print('STRINGS FROM {} STRING TABLE :{}'.format(file.name, strings))
                elif asset.type_hash == 193491583:
                    unk1 = preader.read_uint64()
                    unk2 = preader.read_uint64()
                    unks3 = [preader.read_uint64() for _ in range(4)]
                    null1 = preader.read_uint64()
                    null2 = preader.read_uint64()
                    print('UNKS FROM {}:'.format(file.name + file.type.big_extension))
                    print(unk1)
                    print(unk2)
                    print(unks3)
                    print(null1)
                    print(null2)
                    for offset in unks3:
                        preader.seek(offset)
                        print('10 next ints on offset', preader.peek_fmt('i' * 10))
                        b = 0xDEAD
                    print('=' * 10)
                elif asset.type_hash == 2090500106:
                    a = 0xBEEF  # don't really know what is this
                elif asset.type_hash == 267026877:
                    unk1 = preader.read_uint64()
                    null1 = preader.read_uint64()
                    null2 = preader.read_uint64()

                    print('UNKS FROM {}:'.format(file.name))
                    print(unk1)
                    print(null1)
                    print(null2)
                    print('=' * 10)

                elif asset.type_hash == 1074387168:
                    unk_offset = preader.read_uint64()
                    unk1 = preader.read_uint64()
                    preader.seek(unk_offset)
                    print('UNKS FROM {}:'.format(file.name))
                    print('unk_offset:', unk_offset)
                    print('unk1:', unk1)
                    print('10 next ints on offset', preader.peek_fmt('I' * 10))
                elif asset.type_hash == 2356887053:  # MODEL SHIT
                    b = 0xDEAD
                else:
                    a = 0xCAFE
