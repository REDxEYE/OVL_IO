from pathlib import Path
from typing import Dict

from ByteIO import ByteIO
from PIL import Image


class OVSTextureArchive:

    def __init__(self, parent):
        from OVL_COMPRESSED_DATA import OVLCompressedData
        self.parent: OVLCompressedData = parent
        if len(self.parent.parent.archives) > 1:
            self.filepath = self.parent.parent.path.with_suffix('.ovs.textures_l1')
        elif len(self.parent.parent.archives) > 2:
            self.filepath = self.parent.parent.path.with_suffix('.ovs.textures_l0')
        else:
            print('INVALID')
            exit(0xDEAD)
        self.reader = ByteIO(file=self.filepath.open('rb')).unzip()

    def read(self):
        reader = self.reader
        preader = self.parent.buffer_reader
        reader.skip(12)
        num43 = reader.read_int32()
        reader.skip(4 * 2)
        num44 = reader.read_int32()
        reader.skip(4 * 2)
        dictionary4 = {}  # type: Dict[int,int]
        hash2offset = {}  # type: Dict[int,int]
        dictionary6 = {}  # type: Dict[int,int]
        hash2size = {}  # type: Dict[int,int]

        num45 = reader.tell() + (56 * num44) + 16 + num43
        for i in range(num44):
            num46 = reader.read_uint32()
            reader.skip(20)
            num47 = reader.read_int32()
            reader.skip(4)
            hash2offset[num46] = num45
            hash2size[num46] = num47
            num45 += num47

        for asset in self.parent.ovs_assets:
            if asset.type_hash == 193506774:
                preader.seek(asset.new_offset)
                preader.skip(8 * 3)
                num53 = preader.read_int64()
                texture_format = preader.read_int16()
                num55 = preader.read_int8()
                preader.seek(num53 + 8)
                preader.read_int32()
                width = preader.read_int32()
                height = preader.read_int32()
                reader.skip(4)
                num59 = preader.read_int32()
                if num59 > 1:
                    height *= num59
                preader.skip(4)
                pixel_mode = ('raw', 'RGBA')
                if texture_format == 103:
                    pixel_mode = ('bcn', 5, 0)
                if texture_format == 107:
                    pixel_mode = ('bcn', 7, 0)
                if texture_format == 96:
                    pixel_mode = ('bcn', 1, 0)
                if texture_format == 108:
                    pixel_mode = ('bcn', 7, 0)
                if self.parent.parent.files_by_hash.get(asset.name_hash, False):
                    texture_file = self.parent.parent.files_by_hash[asset.name_hash]
                    texture_name = texture_file.name
                    texture_lod_name = texture_name + '_lod0'
                    lod_hash = self.parent.parent.hash_by_name.get(texture_lod_name, 0)
                    if lod_hash:
                        lod_file = self.parent.parent.files_by_hash[lod_hash]
                    else:
                        lod_file = None
                    path = self.filepath.parent / texture_name
                    path = path.with_name(path.name + '.tga')
                    path = path.absolute()
                    if num55 == 1:
                        file_data_header = self.parent.hash2file_data_header.get(asset.name_hash, False)
                        if file_data_header:
                            num65 = file_data_header.offset + 1
                            self.parent.reader.seek(self.parent.array10[num65])
                            embedded_file_header = self.parent.embedded_file_headers[num65]

                            image_data = self.parent.reader.read_bytes(embedded_file_header.size)
                            print(embedded_file_header.size)
                            image = Image.frombuffer('RGBA', (width, height), image_data, *pixel_mode)
                            image.split()[-1].save(path.with_name(path.stem + '_ALPHA.tga'))
                            image = image.convert('RGB')
                            image.save(path)
                    elif num55 == 2:
                        if hash2offset.get(lod_hash, False):
                            reader.seek(hash2offset[lod_hash])
                            image_data = reader.read_bytes(hash2size[lod_hash])
                            print(hash2size[lod_hash])
                            image = Image.frombuffer('RGBA', (width, height), image_data, *pixel_mode)
                            image.split()[-1].save(path.with_name(path.stem + '_ALPHA.tga'))
                            image = image.convert('RGB')
                            image.save(path)
                        else:
                            print('ERROR')

                else:
                    print('Texture not found')
