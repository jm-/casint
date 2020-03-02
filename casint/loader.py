import os
import struct

import bitstring

from .common import translate_casio_bytes_to_ascii, translate_ascii_bytes_to_casio
from .g1m import G1mLexer, G1mParser
from .ucb import UcbLexer, UcbParser


class InvalidCasioItemTypeException(Exception):
    pass


class InvalidCasioProgramNameException(Exception):
    pass


class CasioProgram(object):
    def __init__(self, name, size, tree):
        self.name = name
        self.stringname = str(translate_casio_bytes_to_ascii(name), 'ascii')
        self.size = size
        self.tree = tree


    def __str__(self):
        status = '(valid)' if self.tree else '(invalid)'
        # translate the title
        return f'{self.stringname:8s}  : {self.size:5d} {status}'


    def __repr__(self):
        return self.__str__()


class G1mFile(object):
    def __init__(self, filepath, debug=False):
        self.filepath = filepath
        self.debug = debug


    def _read_header(self, fp):
        headerBytes = fp.read(32)
        headerBits = bitstring.Bits(bytes=headerBytes)

        headerIbits = ~headerBits
        headerIbytes = headerIbits.tobytes()

        (   fileIdentifier,
            fileTypeIdentifier,
            magicSequence1,
            controlByte1,
            magicSequence2,
            totalFileSize,
            controlByte2,
            reservedSequence1,
            numItems
        ) = struct.unpack('>8sB5sB1sIB9sH', headerIbytes)

        if self.debug:
            print(f'fileIdentifier={fileIdentifier}')
            print(f'fileTypeIdentifier={fileTypeIdentifier}')
            print(f'totalFileSize={totalFileSize}')
            print(f'numItems={numItems}')

        # validate the control bytes
        lsb = totalFileSize % 256
        assert (lsb + 0x41) % 256 == controlByte1
        assert (lsb + 0xb8) % 256 == controlByte2

        # validate magic sequences
        assert magicSequence1 == b'\x00\x10\x00\x10\x00'
        assert magicSequence2 == b'\x01'

        return numItems


    def _read_program(self, itemTitle, itemData):
        # first 10 bytes are reserved
        lexer = G1mLexer(itemData[10:], self.filepath)
        parser = G1mParser(lexer)
        tree = parser.parse()

        program = CasioProgram(
            itemTitle.partition(b'\x00')[0],
            len(itemData),
            tree
        )
        return program


    def _read_pict(self, item_title, item_data):
        return None


    def _read_item(self, fp):
        itemHeader1 = fp.read(20)

        (   itemIdentifier,
            reservedSequence1,
            itemHeaderTypeIdentifier
        ) = struct.unpack('>16s3sB', itemHeader1)

        if self.debug:
            print(f'itemIdentifier={itemIdentifier}')
            print(f'reservedSequence1={reservedSequence1}')
            print(f'itemHeaderTypeIdentifier={itemHeaderTypeIdentifier}')

        # make sure we're dealing with a known item type,
        # so that itemHeader2 can be safely decoded
        assert itemHeaderTypeIdentifier == 0x01

        itemHeader2 = fp.read(24)

        (   memLocationName,
            itemTitle,
            itemTypeIdentifier,
            itemLength,
            reservedSequence2
        ) = struct.unpack('>8s8sBI3s', itemHeader2)

        if self.debug:
            print(f'memLocationName={memLocationName}')
            print(f'itemTitle={itemTitle}')
            print(f'itemTypeIdentifier={itemTypeIdentifier}')
            print(f'itemLength={itemLength}')
            print(f'reservedSequence2={reservedSequence2}')

        # read the rest of the item
        itemData = fp.read(itemLength)

        # make sure the item is a program
        if itemTypeIdentifier == 0x01:
            return self._read_program(itemTitle, itemData)

        elif itemTypeIdentifier == 0x07:
            return self._read_pict(itemTitle, itemData)

        else:
            raise InvalidCasioItemTypeException(
                f"Unknown item type: {itemTypeIdentifier}"
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


def get_program_name_from_filename(filename):
    program_name = filename.rpartition('.')[0].encode('ascii')
    if len(program_name) < 1 or len(program_name) > 8:
        raise InvalidCasioProgramNameException(
            f'"{program_name}" must be between 1 and 8 characters long'
        )
    return translate_ascii_bytes_to_casio(program_name)


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


def load_programs_from_ucb_dir(dirpath):
    programs = []
    for filename in os.listdir(dirpath):
        if not filename.lower().endswith('.ucb'):
            continue
        filepath = os.path.join(dirpath, filename)
        progam_name = get_program_name_from_filename(filename)
        program = load_program_from_ucb_file(filepath, progam_name)
        programs.append(program)
    return programs


def load_programs_from_g1m_file(filepath):
    g1mfile = G1mFile(filepath, debug=False)
    return g1mfile.load()
