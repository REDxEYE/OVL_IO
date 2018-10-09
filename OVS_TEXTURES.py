from pathlib import Path

from ByteIO import ByteIO


class OVSTextureArchive:

    def __init__(self, parent):
        from OVLFile import OVL
        self.parent: OVL = parent
        self.filepath = parent.path.with_suffix('.ovs.textures_l1')
        self.reader = ByteIO(file=self.filepath.open('rb')).unzip()

    def read(self):
        reader = self.reader
        reader.skip(12)
        num43 = reader.read_int32()
        reader.skip(4*2)
        num44 = reader.read_int32()
        reader.skip(4*2)
        num45 = reader.tell() +(56 * num44) + 16 + num43
        for i in range(num44):
            num46 = reader.read_uint32()
            reader.skip(20)
            num47 = reader.read_int32()
            reader.skip()

