from pathlib import Path
from typing import Dict

from ByteIO import ByteIO


class OVSTextureArchive:

    def __init__(self, parent):
        from OVL_COMPRESSED_DATA import OVLCompressedData
        self.parent: OVLCompressedData = parent
        self.filepath = parent.path.with_suffix('.ovs.textures_l1')
        self.reader = ByteIO(file=self.filepath.open('rb')).unzip()

    def read(self):
        reader = self.reader
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

        # for asset in self.
