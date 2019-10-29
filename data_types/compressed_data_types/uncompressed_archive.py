from typing import List

from byte_io import ByteIO
from data_types.compressed_data_types.asset_entry import AssetEntry
from data_types.compressed_data_types.buffer_entry import BufferEntry
from data_types.compressed_data_types.data_entry import DataEntry
from data_types.compressed_data_types.fragment import Fragment
from data_types.compressed_data_types.header_type import HeaderType
from data_types.compressed_data_types.header_entry import HeaderEntry
from data_types.compressed_data_types.set_entry import SetEntry
from data_types.compressed_data_types.set_header import SetHeader
from data_types.compressed_data_types.sized_string_entry import SizedStringEntry
from data_types.ovl_base import OVLBase


class UncompressedArchive(OVLBase):

    def __init__(self, archive):
        from data_types.ovl_archive import OVLArchive
        from data_types.ovl_file import OVLFile
        self.archive: OVLArchive = archive
        self.ovs_file: OVLFile = archive.parent
        self.reader = ByteIO(byte_object=self.archive.uncompressed_data)
        self.header_types = []  # type:List[HeaderType]
        self.header_entries = []  # type:List[HeaderEntry]
        self.data_entries = []  # type:List[DataEntry]
        self.buffer_entries = []  # type:List[BufferEntry]
        self.sized_string_entries = []  # type:List[SizedStringEntry]
        self.fragments = []  # type:List[Fragment]
        self.set_header = SetHeader()
        self.set_entries = []  # type:List[SetEntry]
        self.asset_entries = []  # type:List[AssetEntry]
        self.has_ms2 = False

    def read_sized_str(self,pos, size):
        """Returns content of stream from pos until pos+size"""
        self.reader.seek(pos)
        return self.reader.read(size)

    def get_name(self, file_hash):
        for file_entry in self.ovs_file.file_descriptors:
            if file_entry.file_hash == file_hash:
                return file_entry.name
        return "ERROR"

    def get_ext(self, ext_hash):
        for mimetype in self.ovs_file.mimetypes:
            if mimetype.ext_hash == ext_hash:
                return mimetype.ext
        return "ERROR"

    def get_file_desc(self, file_hash, ext_hash):
        for file in self.ovs_file.file_descriptors:
            if file.file_hash == file_hash and file.mimetype.ext_hash == ext_hash:
                return file
        return None

    def find_data_entry(self, file_hash, ext_hash):
        for data in self.data_entries:
            if data.file_hash == file_hash and data.ext_hash == ext_hash:
                return data
        return None

    def find_str_entry(self, file_hash, ext_hash):
        for data in self.sized_string_entries:
            if data.file_hash == file_hash and data.ext_hash == ext_hash:
                return data
        return None

    def get_frag(self, t):
        """Returns entries of l matching each type tuple in t that have not been processed.
        t: tuple of (x,y) tuples for each fragments header types"""
        out = []
        for h_types in t:
            # print("looking for",h_types)
            for f in self.fragments:
                # can't add fragments that have already been added elsewhere
                if f.done:
                    continue
                # print((f.type_0, f.type_1))
                if h_types == (f.header_0.type, f.header_1.type):
                    f.done = True
                    out.append(f)
                    break
            else:
                raise AttributeError("Could not find a fragment matching header types " + str(h_types))
        return out

    def read(self):
        reader = self.reader
        check_header_data_size = 0
        for _ in range(self.archive.header_type_count):
            header = HeaderType()
            self.register(header)
            header.read(reader)

            self.header_types.append(header)
        for header in self.header_types:
            for _ in range(header.sub_header_count):
                sub_header = HeaderEntry()
                self.register(sub_header)
                sub_header.read(reader)
                sub_header.name = self.get_name(sub_header.file_hash)
                sub_header.extension = self.get_ext(sub_header.ext_hash)
                sub_header.type = header.type
                sub_header.file_desc = self.get_file_desc(sub_header.file_hash, sub_header.ext_hash)
                check_header_data_size += sub_header.size
                header.sub_header_types.append(sub_header)
                self.header_entries.append(sub_header)
        for _ in range(self.archive.data_count):
            entry = DataEntry()
            self.register(entry)
            entry.read(reader)
            self.data_entries.append(entry)
        for _ in range(self.archive.buffer_count):
            entry = BufferEntry()
            self.register(entry)
            entry.read(reader)
            self.buffer_entries.append(entry)
        for i in range(self.archive.file_count):
            entry = SizedStringEntry()
            self.register(entry)
            entry.read(reader)
            entry.name = self.get_name(entry.file_hash)
            entry.extension = self.get_ext(entry.ext_hash)
            entry.data_entry = self.find_data_entry(entry.file_hash, entry.ext_hash)
            entry.header = self.header_entries[entry.header_index] if entry.header_index != -1 else None
            entry.index = i
            self.sized_string_entries.append(entry)
        for _ in range(self.archive.fragment_count):
            entry = Fragment()
            self.register(entry)
            entry.read(reader)

            entry.header_0 = self.header_entries[entry.header_index_0]
            entry.header_1 = self.header_entries[entry.header_index_1]

            self.fragments.append(entry)

        set_data_offset = reader.tell()
        self.set_header.read(reader)

        for _ in range(self.set_header.set_count):
            entry = SetEntry()
            self.register(entry)
            entry.read(reader)
            entry.name = self.get_name(entry.file_hash)
            entry.ext = self.get_ext(entry.ext_hash)
            self.set_entries.append(entry)
        for _ in range(self.set_header.asset_count):
            entry = AssetEntry()
            self.register(entry)
            entry.read(reader)
            entry.name = self.get_name(entry.file_hash)
            entry.ext = self.get_ext(entry.ext_hash)
            self.asset_entries.append(entry)

        for i, set_entry in enumerate(self.set_entries):
            if i == self.set_header.set_count - 1:
                set_entry.end = self.set_header.asset_count
            else:
                set_entry.asset = self.asset_entries[set_entry.start:set_entry.end]
            sized_str_entry = self.find_str_entry(set_entry.file_hash, set_entry.ext_hash)
            sized_str_entry.children = [self.sized_string_entries[a.file_index] for a in set_entry.assets]

        header_size = reader.tell()

        header_data = reader.read_bytes(-1)
        data = header_data[check_header_data_size:]

        for fragment in self.fragments:
            fragment.address_0 = header_size + fragment.header_0.offset + fragment.data_offset_0
            fragment.address_1 = header_size + fragment.header_1.offset + fragment.data_offset_1

        for sized_str_entry in self.sized_string_entries:
            # usual, valid files
            if sized_str_entry.header is not None:
                sized_str_entry.address = header_size + sized_str_entry.header.offset + sized_str_entry.data_offset
            # ????? - those with -1 as the header index, possibly only for set entries (virtual files)
            else:
                sized_str_entry.address = header_size  # + sized_str_entry.data_offset
        sorted_sized_str_entries = []
        reversed_sized_str_entries = list(reversed(self.sized_string_entries))
        frag_order = ("mdl2", "fgm", "ms2", "banis", "bani", "tex", "txt", "enumnamer", "motiongraphvars", "hier",)

        for ext in frag_order:
            for sized_str_entry in reversed_sized_str_entries:
                if sized_str_entry.extension == ext:
                    if ext == "ms2":
                        self.has_ms2 = False
                    sorted_sized_str_entries.append(sized_str_entry)
        fgm_frag_count = 5 if self.has_ms2 > 1 else 4
        dic = {
            "fgm": ((2, 2) for x in range(fgm_frag_count)),
            "ms2": ((2, 2), (2, 2), (2, 2),),
            "bani": ((2, 2),),
            "tex": ((3, 3), (3, 7),),
        }
        all_addresses = [f.address_0 for f in self.fragments] + \
                        [f.address_1 for f in self.fragments] + \
                        [f.address for f in self.sized_string_entries]

        sorted_addresses = sorted(set(all_addresses))
        sorted_addresses.append(header_size + check_header_data_size)

        for f in self.fragments:
            # get the offset of the next entry that points into this buffer
            ind = sorted_addresses.index(f.address_1) + 1
            # set data size for this entry
            f.data_size_1 = sorted_addresses[ind] - f.address_1

            # get the offset of the next entry that points into this buffer
            ind = sorted_addresses.index(f.address_0) + 1
            # set data size for this entry
            f.data_size_0 = sorted_addresses[ind] - f.address_0

        reversed_fragments = list(reversed(self.fragments))
        for sized_str_entry in reversed(sorted_sized_str_entries):
            print("Collecting fragments for", sized_str_entry.name)
            # fixed fragments
            if sized_str_entry.extension in dic:
                t = dic[sized_str_entry.extension]
            # variable fragments
            elif sized_str_entry.extension == "mdl2":
                # 5 fixed ones
                t = ((2, 2) for x in range(5))
            # empty tuple, no fragments
            else:
                t = ()
            # print(t)
            # get and set fragments
            sized_str_entry.fragments = self.get_frag(t)
            # for debugging only:
            for frag in sized_str_entry.fragments:
                frag.sized_str_entry_index = sized_str_entry.index
                frag.name = sized_str_entry.name

            # second pass: collect model fragments
        for sized_str_entry in reversed(sorted_sized_str_entries):
            # variable fragments
            pass
            # if sized_str_entry.extension == "mdl2":
            #     print("Collecting model fragments for", sized_str_entry.name)
            #
            #     # infer the model count from the fragment with material1 data
            #     orange_frag = sized_str_entry.fragments[2]
            #     orange_frag_count = orange_frag.data_size_1 // 4
            #     mats = []
            #     reader.seek(orange_frag.address_1)
            #     for i in range(orange_frag_count):
            #         mats.append(self.get_from(Ms2Format.Material1, stream))
            #     model_indices = [m.model_index for m in mats]
            #     sized_str_entry.model_count = max(model_indices) + 1
            #
            #     # check for empty mdl2s by ensuring that one of the fragments with constant size has the correct size
            #     yellow_frag = sized_str_entry.fragments[1]
            #     if yellow_frag.data_size_1 != 64:
            #         sized_str_entry.model_count = 0
            #         sized_str_entry.model_frags = []
            #         print("No model frags for", sized_str_entry.name)
            #         continue
            #     # if we have just 1 fragment it has been added in the fixed fragment section and we can not get another one
            #     if sized_str_entry.model_count < 2:
            #         sized_str_entry.model_frags = []
            #         print("No extra model frags for", sized_str_entry.name)
            #         continue
            #
            #     # create type template from count
            #     t = ((2, 2) for x in range(sized_str_entry.model_count))
            #     # get and set fragments
            #     sized_str_entry.model_frags = self.get_frag(reversed_fragments, t)
            #     # for debugging only:
            #     for frag in sized_str_entry.model_frags:
            #         frag.sized_str_entry_index = sized_str_entry.index
            #         frag.name = sized_str_entry.name
        buff_ind = 0
        for i, data_entry in enumerate(self.data_entries):
            data_entry.buffers = []
            data_entry.buffer_datas = []
            for j in range(data_entry.buffer_count):
                # print("data",i,"buffer",j, "buff_ind",buff_ind)
                buffer = self.buffer_entries[buff_ind]
                # also give each buffer a reference to data so we can access it later
                buffer.data_entry = data_entry
                data_entry.buffers.append(buffer)
                data_entry.buffer_datas.append(None)
                buff_ind += 1

        out_buffers = []
        # only do this if there are any data entries so that max() doesn't choke
        if self.data_entries:
            # check how many buffers occur at max in one data block
            max_buffers_per_data = max([data.buffer_count for data in self.data_entries])
            # first read the first buffer for every file
            # then the second if it has any
            # and so on, until there is no data entry left with unprocessed buffers
            for i in range(max_buffers_per_data):
                for data_entry in self.data_entries:
                    if i < data_entry.buffer_count:
                        out_buffers.append(data_entry.buffers[i])
        cursor = 0
        for b in out_buffers:
            # get the data file that referenced this buffer and store data there
            # print(b.data_entry.name)
            address = header_size + check_header_data_size + cursor
            # print("b.index", b.index, "address", address, "b.size", b.size, "cursor", cursor)
            b.start = address
            try:
                b.data_entry.buffer_datas[b.index] = data[cursor:cursor + b.size]
            except:
                print("Buffer index ouf of buffer count", b.index, "size", b.size,'cursor',cursor)
            cursor += b.size
        a = 0

    def dump(self):
        for entry in self.sized_string_entries:
            entry.print()

    def print(self, prefix=''):
        print(f'{prefix}{self.__class__.__name__}')
        for header in self.header_types:
            header.print('\t' + prefix)
        for header in self.header_entries:
            header.print('\t' + prefix)
        for header in self.data_entries:
            header.print('\t' + prefix)
        for header in self.buffer_entries:
            header.print('\t' + prefix)
        for header in self.sized_string_entries:
            header.print('\t' + prefix)
        self.set_header.print("\t" + prefix)
        for header in self.set_entries:
            header.print('\t' + prefix)
        for header in self.asset_entries:
            header.print('\t' + prefix)
