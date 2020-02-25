import os
import sys

from decoder import G1mFile, CasioProgram


def prepare_output_folder(output_folder):
    try:
        os.makedirs(output_folder)
    except OSError:
        pass


def unpack(filepath, output_folder):
    # load the input
    g1mfile = G1mFile(filepath, debug=False)
    programs = g1mfile.load()
    # get output ready
    prepare_output_folder(output_folder)
    # write programs
    for program in programs:
        program_filename = f"{program.stringname}.ucb"
        program_filepath = os.path.join(output_folder, program_filename)
        with open(program_filepath, 'wb') as fp:
            program.tree.write_ucb(fp, 0)


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
