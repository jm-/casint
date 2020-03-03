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
        return f"{self.stringname}.ucp"


    def write_ucb(self, fp):
        # write out characters for each pixel
        x = 0
        for pixel in self.image_bits:
            if pixel:
                fp.write(b'#')
            else:
                fp.write(b' ')
            x += 1
            if x == 128:
                fp.write(b'\n')
                x = 0


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


    def get_program_by_name(self, name):
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


    def _read_program(self, item_title, item_data):
        # first 10 bytes are reserved
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
            bitstring.Bits(bytes=item_data[:1024])
        )
        return pict


    def _read_item(self, fp):
        item_header_1 = fp.read(20)

        (   item_identifier,
            reserved_sequence_1,
            item_header_type_identifier
        ) = struct.unpack('>16s3sB', item_header_1)

        if self.debug:
            print(f'item_identifier={item_identifier}')
            print(f'reserved_sequence_1={reserved_sequence_1}')
            print(f'item_header_type_identifier={item_header_type_identifier}')

        # make sure we're dealing with a known item type,
        # so that item_header_2 can be safely decoded
        assert item_header_type_identifier == 0x01

        item_header_2 = fp.read(24)

        (   mem_location_name,
            item_title,
            item_type_identifier,
            item_length,
            reserved_sequence_2
        ) = struct.unpack('>8s8sBI3s', item_header_2)

        if self.debug:
            print(f'mem_location_name={mem_location_name}')
            print(f'item_title={item_title}')
            print(f'item_type_identifier={item_type_identifier}')
            print(f'item_length={item_length}')
            print(f'reserved_sequence_2={reserved_sequence_2}')

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
    image_bits = bitstring.BitArray(length=128 * 64)
    with open(filepath, 'rb') as fp:
        lines = fp.readlines()

    for y, line in enumerate(lines):
        for x, c in enumerate(line.rstrip(b'\r\n')):
            image_bits[y * 128 + x] = (c != 0x20)

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
        elif filename.lower().endswith('.ucp'):
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
