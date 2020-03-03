import os
import sys

from casint.loader import G1mFile, CasioProgram


def prepare_output_folder(output_folder):
    try:
        os.makedirs(output_folder)
    except OSError:
        pass


def unpack(filepath, output_folder):
    # load the input
    g1mfile = G1mFile(filepath, debug=False)
    items = g1mfile.load()
    # get output ready
    prepare_output_folder(output_folder)
    # write items
    for item in items:
        item_filename = item.get_ucb_filename()
        item_filepath = os.path.join(output_folder, item_filename)
        with open(item_filepath, 'wb') as fp:
            item.write_ucb(fp)


def print_usage():
    print(f'Usage: {sys.argv[0]} <unpack> <file.g1m> <folder>')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'unpack':
            if len(sys.argv) == 4:
                unpack(sys.argv[2], sys.argv[3])
            else:
                print_usage()
                sys.exit(1)
        else:
            print_usage()
            sys.exit(1)
    else:
        print_usage()
        sys.exit(1)
