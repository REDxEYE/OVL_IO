import data_types
from byte_io import ByteIO

if __name__ == '__main__':
    model = r'test_data/Driver.ovl'
    file = data_types.OVLFile(model)
    file.print()