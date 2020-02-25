import os
import struct

import bitstring

from common import translate_string_literal
from g1m import G1mLexer, G1mParser
from ucb import UcbLexer, UcbParser


class CasioProgram(object):
    def __init__(self, name, size, tree):
        self.name = name
        self.stringname = str(translate_string_literal(name), 'ascii')
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
        assert itemTypeIdentifier == 0x01

        # first 10 bytes are reserved
        lexer = G1mLexer(itemData[10:])
        parser = G1mParser(lexer)
        tree = parser.parse()

        program = CasioProgram(
            itemTitle.partition(b'\x00')[0],
            len(itemData),
            tree
        )
        return program


    def load(self):
        with open(self.filepath, 'rb') as fp:
            numItems = self._read_header(fp)
            programs = [None] * numItems
            i = 0
            while i < numItems:
                if self.debug:
                    print(f'---------- reading item {i}')
                programs[i] = self._read_item(fp)
                i += 1
            return programs


def load_program_from_ucb_file(filepath):
    with open(filepath, 'rb') as fp:
        ucb_data = fp.read()
    lexer = UcbLexer(ucb_data)
    parser = UcbParser(lexer)
    tree = parser.parse()

    program = CasioProgram(
        os.path.basename(filepath).rpartition('.')[0].encode('ascii'),
        len(ucb_data),
        tree
    )


def load_programs_from_ucb_dir(dirpath):
    programs = []
    for filename in os.listdir(dirpath):
        if not filename.lower().endswith('.ucb'):
            continue
        filepath = os.path.join(dirpath, filename)
        program = load_program_from_ucb_file(filepath)
        programs.append(program)
    return programs


def load_programs_from_g1m_file(filepath):
    g1mfile = G1mFile(filepath, debug=False)
    return g1mfile.load()
