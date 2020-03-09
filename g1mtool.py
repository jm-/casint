import os
import sys

from casint.loader import (
    G1mFile,
    load_items_from_g1m_file,
    load_items_from_ucb_dir
)


def prepare_output_folder(output_folder):
    os.makedirs(output_folder, exist_ok=True)


def unpack(filepath, output_folder):
    # load the input
    items = load_items_from_g1m_file(filepath)
    # get output ready
    prepare_output_folder(output_folder)
    # write items
    for item in items:
        item_filename = item.get_ucb_filename()
        item_filepath = os.path.join(output_folder, item_filename)
        with open(item_filepath, 'wb') as fp:
            item.write_ucb(fp)


def pack(input_folder, filepath):
    # load the input
    items = load_items_from_ucb_dir(input_folder)
    # get output ready
    g1m_folder = os.path.dirname(filepath)
    if g1m_folder:
        prepare_output_folder(g1m_folder)
    # create a g1m file to write items to
    g1m = G1mFile(filepath, debug=False)
    g1m.write_items(items)


def print_usage():
    print(f'Usage: {sys.argv[0]} <unpack> <file.g1m> <folder>')
    print(f'       {sys.argv[0]} <pack> <folder> <file.g1m>')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'unpack':
            if len(sys.argv) == 4:
                unpack(sys.argv[2], sys.argv[3])
            else:
                print_usage()
                sys.exit(1)
        elif command == 'pack':
            if len(sys.argv) == 4:
                pack(sys.argv[2], sys.argv[3])
            else:
                print_usage()
                sys.exit(1)
        else:
            print_usage()
            sys.exit(1)
    else:
        print_usage()
        sys.exit(1)
