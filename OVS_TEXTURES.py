from pathlib import Path
from typing import Dict

from ByteIO import ByteIO
from PIL import Image

class OVSTextureArchive:

    def __init__(self, parent):
        from OVL_COMPRESSED_DATA import OVLCompressedData
        self.parent: OVLCompressedData = parent
        if len(self.parent.parent.archives)>1:
            self.filepath = self.parent.parent.path.with_suffix('.ovs.textures_l1')
        elif len(self.parent.parent.archives)>2:
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
        dictionary5 = {}  # type: Dict[int,int]
        dictionary6 = {}  # type: Dict[int,int]
        dictionary7 = {}  # type: Dict[int,int]

        num45 = reader.tell() + (56 * num44) + 16 + num43
        for i in range(num44):
            num46 = reader.read_uint32()
            reader.skip(20)
            num47 = reader.read_int32()
            reader.skip(4)
            dictionary5[num46] = num45
            dictionary7[num46] = num47
            num45 += num47

        for asset in self.parent.ovs_assets:
            if asset.type_hash == 193506774:
                preader.seek(asset.new_offset)
                preader.skip(8 * 3)
                num53 = preader.read_int64()
                num54 = preader.read_int16()
                num55 = preader.read_int8()
                preader.seek(num53 + 8)
                num56 = preader.read_int32()
                width = preader.read_int32()
                height = preader.read_int32()
                reader.skip(4)
                num59 = preader.read_int32()
                if num59 > 1:
                    height *= num59
                preader.skip(4)
                if self.parent.parent.files_by_hash.get(asset.name_hash, False):
                    texture_file = self.parent.parent.files_by_hash[asset.name_hash]
                    texture_name = texture_file.name
                    texture_lod_name = texture_name+'_lod0'
                    lod_hash = self.parent.parent.hash_by_name.get(texture_lod_name,0)
                    if lod_hash:
                        lod_file = self.parent.parent.files_by_hash[lod_hash]
                    else:
                        lod_file = None
                    print(texture_file)
                    print(lod_file)
                    print(width,height)
                    if num55 == 1:
                        file_data_header = self.parent.hash2file_data_header.get(asset.name_hash, False)
                        if file_data_header:
                            num65 = file_data_header.offset + 1
                            self.parent.reader.seek(self.parent.array10[num65])
                            embedded_file_header = self.parent.embedded_file_headers[num65]

                            image_data = self.parent.reader.read_bytes(embedded_file_header.size)
                            print(embedded_file_header.size)
                            a = Image.frombuffer('RGB', (width, height), image_data, 'raw', 'RGBA', 0, 1)
                            a.save(texture_name + '.tga')
                    elif num55 == 2:
                        if dictionary5.get(lod_hash, False):
                            reader.seek(dictionary5[lod_hash])
                            image_data = reader.read_bytes(dictionary7[lod_hash])
                            print(dictionary7[lod_hash])
                            # a = Image.frombuffer('RGB', (width, height), image_data, 'raw', 'L', 0, 1)
                            # a.save(texture_name + '.tga')

                else:
                    print('Texture not found')


