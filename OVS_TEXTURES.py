from pathlib import Path
from typing import Dict

from ByteIO import ByteIO


class OVSTextureArchive:

    def __init__(self, parent):
        from OVL_COMPRESSED_DATA import OVLCompressedData
        self.parent: OVLCompressedData = parent
        self.filepath = self.parent.parent.path.with_suffix('.ovs.textures_l1')
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
                num57 = preader.read_int32()
                num58 = preader.read_int32()
                reader.skip(4)
                num59 = preader.read_int32()
                if num59 > 1:
                    num58 *= num59
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
                else:
                    print('Texture not found')
