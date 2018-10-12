from pathlib import Path
from typing import Dict, Any, Tuple

from ByteIO import ByteIO
from PIL import Image


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
        self.resources = {}# type: Dict[int,OVSResourceHeader]
        if len(self.parent.parent.archives) > 1:
            self.textures_1 = self.parent.parent.path.with_suffix('.ovs.textures_l1')
            self.reader_t1 = ByteIO(file=self.textures_1.open('rb')).unzip()
            self.readers.append(self.reader_t1)
            self.read_archive(self.reader_t1)
        elif len(self.parent.parent.archives) > 2:
            self.textures_2 = self.parent.parent.path.with_suffix('.ovs.textures_l0')
            self.reader_t2 = ByteIO(file=self.textures_2.open('rb')).unzip()
            self.readers.append(self.reader_t2)
        else:
            print('INVALID')
            exit(0xDEAD)

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
            # print(asset.type_hash,asset.local_type_hash)
            if asset.local_type_hash == 193506774:
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
                pixel_mode = ('raw', 'RGBA', 0)  # type: Tuple[str,Any,int]
                if texture_format == 103:
                    pixel_mode = ('bcn', 5, 0)
                if texture_format == 107:
                    pixel_mode = ('bcn', 7, 0)
                if texture_format == 96:
                    pixel_mode = ('bcn', 1, 0)
                if texture_format == 108:
                    pixel_mode = ('bcn', 7, 0)
                if self.parent.parent.files_by_hash.get(asset.file_hash, False):
                    texture_file = self.parent.parent.files_by_hash[asset.file_hash]
                    texture_name = texture_file.name
                    texture_lod_name = texture_name + '_lod0'
                    lod_hash = self.parent.parent.hash_by_name.get(texture_lod_name, 0)
                    path = self.textures_1.parent / texture_name
                    path = path.with_name(path.name + '.tga')
                    path = path.absolute()
                    if storage_id == 1:

                        file_data_header = asset.file_data_header
                        if file_data_header:
                            part_id = file_data_header.part_array_offset + 1
                            embedded_file_header = self.parent.embedded_file_headers[part_id]
                            print(embedded_file_header)
                            self.parent.reader.seek(embedded_file_header.offset)
                            image_data = self.parent.reader.read_bytes(embedded_file_header.size)
                            image = Image.frombuffer('RGBA', (width, height), image_data, *pixel_mode)
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
