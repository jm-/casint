import os
import struct

import bitstring

from .common import translate_casio_bytes_to_ascii, translate_ascii_bytes_to_casio
from .g1m import G1mLexer, G1mParser
from .ucb import UcbLexer, UcbParser


class InvalidCasioItemTypeException(Exception):
    pass


class InvalidCasioItemNameException(Exception):
    pass


class CasioItem():
    def __init__(self, name):
        self.name = name
        self.stringname = str(translate_casio_bytes_to_ascii(name), 'ascii')


    def get_ucb_filename(self):
        raise NotImplementedError()


    def write_ucb(self, fp):
        raise NotImplementedError()


class CasioProgram(CasioItem):
    def __init__(self, name, size, tree):
        super().__init__(name)
        self.size = size
        self.tree = tree


    def get_ucb_filename(self):
        return f"{self.stringname}.ucb"


    def write_ucb(self, fp):
        self.tree.write_ucb(fp, 0)


    def write_g1m(self, fp):
        self.tree.write_g1m(fp)


    def __str__(self):
        status = '(valid)' if self.tree else '(invalid)'
        # translate the title
        return f'{self.stringname:8s}  : {self.size:5d} {status}'


    def __repr__(self):
        return self.__str__()


class CasioPict(CasioItem):
    def __init__(self, name, image_bits):
        super().__init__(name)
        assert self.stringname.startswith('PICT')
        num = int(self.stringname[4:])
        assert num >= 1 and num <= 20
        self.num = num
        self.image_bits = image_bits


    def get_ucb_filename(self):
        return f"{self.stringname}.bmp"


    def write_ucb(self, fp):
        # write image as bmp
        width = 128
        height = 128
        bytes_per_pixel = 3

        # check that the image is 128x128
        assert len(self.image_bits) == (128 * 128)

        # BMP header
        # filetype
        fp.write(b'BM')
        # entire file size (header + header + pixel data)
        fp.write(struct.pack('<I', 14 + 40 + width * height * bytes_per_pixel))
        # reserved (x2)
        fp.write(b'\x00\x00')
        fp.write(b'\x00\x00')
        # pixel data offset (14 + 40 = 54)
        fp.write(struct.pack('<I', 14 + 40))

        # DIB header
        # header size
        fp.write(struct.pack('<I', 40))
        # width x height
        fp.write(struct.pack('<ii', width, height))
        # planes
        fp.write(struct.pack('<H', 1))
        # bits per pixel
        fp.write(struct.pack('<H', bytes_per_pixel * 8))
        # compression
        fp.write(struct.pack('<I', 0))
        # image size
        fp.write(struct.pack('<I', width * height * bytes_per_pixel))
        # pixels per meter (unused)
        fp.write(struct.pack('<ii', 0, 0))
        # total colours, important colours
        fp.write(struct.pack('<II', 0, 0))

        # pixel data
        # scan lines are written from the bottom left of the image
        for y in range(127, -1, -1):
            row = self.image_bits[y*128:y*128+128]
            for pixel in row:
                if pixel:
                    fp.write(b'\x10\x10\x10')
                else:
                    fp.write(b'\xee\xe8\xe8')


    def __str__(self):
        return f'{self.stringname:8s}'


    def __repr__(self):
        return self.__str__()


class CasioItemCollection():
    '''
    Collection of items for a casio machine
    '''
    def __init__(self, items):
        self.items = items
        self.program_count = len(self.get_programs())


    def __iter__(self):
        return iter(self.items)


    def __len__(self):
        return len(self.items)


    def get_program_by_name(self, name):
        '''
        Gets a program by its casio name.
        '''
        for item in self.items:
            if type(item) is CasioProgram and item.name == name:
                return item


    def get_program_by_index(self, index):
        return self.get_programs()[index]


    def get_programs(self):
        return list(filter(
            lambda i: type(i) is CasioProgram,
            self.items
        ))


    def get_picts(self):
        return list(filter(
            lambda i: type(i) is CasioPict,
            self.items
        ))


    def get_program_names(self):
        return list(map(
            lambda p: p.stringname,
            self.get_programs()
        ))


class G1mFile():
    def __init__(self, filepath, debug=False):
        self.filepath = filepath
        self.debug = debug


    def _read_header(self, fp):
        header_bytes = fp.read(32)
        header_bits = bitstring.Bits(bytes=header_bytes)

        header_i_bits = ~header_bits
        header_i_bytes = header_i_bits.tobytes()

        (   file_identifier,
            file_type_identifier,
            magic_sequence_1,
            control_byte_1,
            magic_sequence_2,
            total_file_size,
            control_byte_2,
            reserved_sequence_1,
            num_items
        ) = struct.unpack('>8sB5sB1sIB9sH', header_i_bytes)

        if self.debug:
            print(f'file_identifier={file_identifier}')
            print(f'file_type_identifier={file_type_identifier}')
            print(f'total_file_size={total_file_size}')
            print(f'num_items={num_items}')

        # validate the control bytes
        lsb = total_file_size % 256
        assert (lsb + 0x41) % 256 == control_byte_1
        assert (lsb + 0xb8) % 256 == control_byte_2

        # validate magic sequences
        assert magic_sequence_1 == b'\x00\x10\x00\x10\x00'
        assert magic_sequence_2 == b'\x01'

        return num_items


    def _write_header(self, fp, num_items):
        # writes the g1m header to the first 32 bytes.
        # assumes the current stream position is at the end of the file
        total_file_size = fp.tell()
        # rewind
        fp.seek(0, 0)

        # calculate the control bytes
        lsb = total_file_size % 256
        control_byte_1 = (lsb + 0x41) % 256
        control_byte_2 = (lsb + 0xb8) % 256

        # pack header
        header_i_bytes = struct.pack(
            '>8sB5sB1sIB9sH',
            b'USBPower',
            0x31,
            b'\x00\x10\x00\x10\x00',
            control_byte_1,
            b'\x01',
            total_file_size,
            control_byte_2,
            b'\xff\xff\xff\xff\xff\xff\xff\xff\xff',
            num_items
        )
        # invert the header bits
        header_i_bits = bitstring.Bits(bytes=header_i_bytes)
        header_bits = ~header_i_bits
        header_bytes = header_bits.tobytes()

        fp.write(header_bytes)


    def _read_program(self, item_title, item_data):
        password = item_data[:8]
        lexer = G1mLexer(item_data[10:], self.filepath)
        parser = G1mParser(lexer)
        tree = parser.parse()

        program = CasioProgram(
            item_title.partition(b'\x00')[0],
            len(item_data),
            tree
        )
        return program


    def _read_pict(self, item_title, item_data):
        pict = CasioPict(
            item_title.partition(b'\x00')[0],
            bitstring.Bits(bytes=item_data)
        )
        return pict


    def _read_item(self, fp):
        item_header_1 = fp.read(20)

        (   item_identifier,
            sub_item_count
        ) = struct.unpack('>16sI', item_header_1)

        if self.debug:
            print(f'item_identifier={item_identifier}')
            print(f'sub_item_count={sub_item_count}')

        # make sure the subitem count is 1,
        # so that item_header_2 can be safely decoded
        assert sub_item_count == 0x01

        item_header_2 = fp.read(24)

        (   mem_location_name,
            item_title,
            item_type_identifier,
            item_length,
            reserved_sequence
        ) = struct.unpack('>8s8sBI3s', item_header_2)

        if self.debug:
            print(f'mem_location_name={mem_location_name}')
            print(f'item_title={item_title}')
            print(f'item_type_identifier={item_type_identifier}')
            print(f'item_length={item_length}')
            print(f'reserved_sequence={reserved_sequence}')

        # read the rest of the item
        item_data = fp.read(item_length)

        # make sure the item is a program
        if item_type_identifier == 0x01:
            return self._read_program(item_title, item_data)

        elif item_type_identifier == 0x07:
            return self._read_pict(item_title, item_data)

        else:
            raise InvalidCasioItemTypeException(
                f"Unknown item type: {item_type_identifier}"
            )


    def _write_program(self, item, fp):
        # write header 1
        # item_identifier
        fp.write(b'PROGRAM\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        # sub_item_count
        fp.write(b'\x00\x00\x00\x01')

        # write header 2
        # mem_location_name
        fp.write(b'system\x00\x00')
        # item_title
        fp.write(item.name.ljust(8, b'\x00'))
        # item_type_identifier
        fp.write(b'\x01')
        # item_length
        # this needs to be written at the end
        # store the stream position now and write an empty placeholder
        item_length_stream_position = fp.tell()
        fp.write(b'\x00\x00\x00\x00')
        # reserved_sequence
        fp.write(b'\x00\x00\x00')

        # store the stream position now so we can calculate the item_length
        pre_program_stream_position = fp.tell()
        # password
        fp.write(b'\x00\x00\x00\x00\x00\x00\x00\x00')
        # alignment
        fp.write(b'\x00\x00')
        # write program data
        item.write_g1m(fp)

        # calculate item_length
        post_program_stream_position = fp.tell()
        item_length = post_program_stream_position - pre_program_stream_position
        # pad to nearest 4 bytes
        pad_length = 4 - (item_length % 4)
        if pad_length > 0:
            fp.write(b'\x00' * pad_length)
            item_length += pad_length
            post_program_stream_position += pad_length

        # rewind to write item_length
        fp.seek(item_length_stream_position, 0)
        fp.write(struct.pack('>I', item_length))

        # seek back
        fp.seek(post_program_stream_position, 0)


    def _write_pict(self, item, fp):
        # write header 1
        # item_identifier
        fp.write(b'PROGRAM\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        # sub_item_count
        fp.write(b'\x00\x00\x00\x01')

        # write header 2
        # mem_location_name
        fp.write(b'system\x00\x00')
        # item_title
        fp.write(item.name.ljust(8, b'\x00'))
        # item_type_identifier
        fp.write(b'\x07')
        # item_length
        fp.write(struct.pack('>I', 2048))
        # reserved_sequence
        fp.write(b'\x00\x00\x00')

        # write pixel data
        fp.write(item.image_bits.tobytes())


    def load(self):
        with open(self.filepath, 'rb') as fp:
            numItems = self._read_header(fp)
            items = [None] * numItems
            i = 0
            while i < numItems:
                if self.debug:
                    print(f'---------- reading item {i}')
                items[i] = self._read_item(fp)
                i += 1
            return items


    def write_items(self, items):
        item_count = len(items)
        with open(self.filepath, 'wb') as fp:
            # skip the header til last; we need to write the filesize
            fp.write(b'\x00' * 32)
            # write items
            items_written = 0
            for item in items:
                if type(item) is CasioProgram:
                    self._write_program(item, fp)
                    items_written += 1
                elif type(item) is CasioPict:
                    self._write_pict(item, fp)
                    items_written += 1
                else:
                    # undefined, skip
                    pass
            # g1m header can be written
            self._write_header(fp, items_written)


def get_item_name_from_filename(filename):
    item_name = filename.rpartition('.')[0].encode('ascii')
    if len(item_name) < 1 or len(item_name) > 8:
        raise InvalidCasioItemNameException(
            f'"{item_name}" must be between 1 and 8 characters long'
        )
    return translate_ascii_bytes_to_casio(item_name)


def load_program_from_ucb_file(filepath, progam_name):
    with open(filepath, 'rb') as fp:
        ucb_data = fp.read()

    lexer = UcbLexer(ucb_data, filepath)
    parser = UcbParser(lexer)
    tree = parser.parse()

    return CasioProgram(
        progam_name,
        len(ucb_data),
        tree
    )


def load_pict_from_ucb_file(filepath, pict_name):
    image_bits = bitstring.BitArray(length=128 * 128)
    with open(filepath, 'rb') as fp:
        # skip past the headers
        fp.seek(14 + 40, 0)
        # read scan lines
        for y in range(127, -1, -1):
            line = fp.read(128 * 3)
            i = 0
            j = 3
            k = 0
            while j <= len(line):
                pixel = line[i:j]
                image_bits[y * 128 + k] = (pixel == b'\x10\x10\x10')
                i += 3
                j += 3
                k += 1

    return CasioPict(pict_name, image_bits)


def load_items_from_ucb_dir(dirpath):
    items = []
    for filename in os.listdir(dirpath):
        filepath = os.path.join(dirpath, filename)
        if filename.lower().endswith('.ucb'):
            item = load_program_from_ucb_file(
                filepath,
                get_item_name_from_filename(filename)
            )
        elif filename.lower().endswith('.bmp'):
            item = load_pict_from_ucb_file(
                filepath,
                get_item_name_from_filename(filename)
            )
        else:
            continue
        items.append(item)
    return CasioItemCollection(items)


def load_items_from_g1m_file(filepath):
    g1mfile = G1mFile(filepath, debug=False)
    items = g1mfile.load()
    return CasioItemCollection(items)
