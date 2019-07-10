import struct

import bitstring

from interpreter import Lexer, Parser


class CasioProgram(object):
    def __init__(self, name, text):
        self.name = name.rstrip(b'\x00')
        self.size = len(text)
        # first 10 bytes are reserved
        lexer = Lexer(text[10:])
        parser = Parser(lexer)
        self._parse(parser)

    def _parse(self, parser):
        try:
            self.tree = parser.parse()
        except:
            self.tree = None

    def __str__(self):
        isParsed = hasattr(self, 'tree') and self.tree
        status = '(valid)' if isParsed else '(invalid)'
        stringname = self.name.decode('ascii')
        return f'{stringname:8s}  : {self.size:5d} {status}'

    def __repr__(self):
        return self.__str__()


class G1mFile(object):
    def __init__(self, filepath, debug=False):
        self.filepath = filepath
        self.debug = debug
        # table for G1M character set
        self.char_encoding_table = bytes.maketrans(
            b'\x89\x99',
            b'\x2b\x7e'
        )

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

        # translate the title
        itemTitle = itemTitle.translate(self.char_encoding_table)

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

        program = CasioProgram(itemTitle, itemData)
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
