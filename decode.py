import struct

import bitstring

from interpreter import *

class CasioProgram(object):
    def __init__(self, text):
        # first 10 bytes are reserved
        self.lexer = Lexer(text[10:])
        self.parser = Parser(self.lexer)

    def parse(self):
        tree = self.parser.parse()


class G1mFile(object):
    def __init__(self, filepath):
        self.filepath = filepath

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

        print 'fileIdentifier', fileIdentifier
        print 'fileTypeIdentifier', fileTypeIdentifier
        print 'totalFileSize', totalFileSize
        print 'numItems', numItems

        # validate the control bytes
        lsb = totalFileSize % 256
        assert (lsb + 0x41) % 256 == controlByte1
        assert (lsb + 0xb8) % 256 == controlByte2

        # validate magic sequences
        assert magicSequence1 == '\x00\x10\x00\x10\x00'
        assert magicSequence2 == '\x01'

        return numItems

    def _read_item(self, fp):
        itemHeader1 = fp.read(20)

        (   itemIdentifier,
            reservedSequence1,
            itemHeaderTypeIdentifier
        ) = struct.unpack('>16s3sB', itemHeader1)

        print 'itemIdentifier', itemIdentifier
        print 'reservedSequence1', reservedSequence1
        print 'itemHeaderTypeIdentifier', itemHeaderTypeIdentifier

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

        print 'memLocationName', memLocationName
        print 'itemTitle', itemTitle
        print 'itemTypeIdentifier', itemTypeIdentifier
        print 'itemLength', itemLength
        print 'reservedSequence2', reservedSequence2

        # read the rest of the item
        itemData = fp.read(itemLength)

        # make sure the item is a program
        assert itemTypeIdentifier == 0x01

        program = CasioProgram(itemData)
        program.parse()

    def load(self):
        with open(self.filepath, 'rb') as fp:
            numItems = self._read_header(fp)
            i = 0
            while i < numItems:
                print '---------- reading item %d' % (i,)
                self._read_item(fp)
                i += 1

def main(filepath):
    g1mfile = G1mFile(filepath)
    g1mfile.load()

    # debugging
    return g1mfile

if __name__ == '__main__':
    from sys import argv as args

    if len(args) == 2:
        # debugging: remove assignment
        g = main(args[1])
    else:
        print 'Usage: %s <file.g1m>' % (args[0],)
