import data_types
from byte_io import ByteIO

if __name__ == '__main__':
    from contextlib import redirect_stdout

    with open('data.txt', 'w') as f:
        with redirect_stdout(f):
            # model = r'test_data/Dracorex.ovl'
            # model = r'test_data/Driver.ovl'
            model = r'test_data/Parrot.ovl'
            file = data_types.OVLFile(model)
            file.read()
            file.read_archives()
            for archive in file.archives:
                archive.uncompressed_archive.dump()
            # file.print()
