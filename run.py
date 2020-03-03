import os
import sys
import traceback

try:
    import sdl2
except ImportError:
    import platform
    arch, osname = platform.architecture()
    if osname == 'WindowsPE':
        os.environ['PYSDL2_DLL_PATH'] = 'lib/32' if arch == '32bit' else 'lib/64'
    import sdl2

from casint.common import translate_ascii_bytes_to_casio
from casint.loader import (
    CasioProgram,
    CasioPict,
    load_items_from_g1m_file,
    load_items_from_ucb_dir
)
from casint.machine import InterpreterQuitException
from casint.system import CasioSystem


def main(path, prog_name=None):
    # if the path is a dir, load items from ucb.
    # else, read as g1m.
    if os.path.isfile(path):
        print(f'Processing G1M file: {path}')
        items = load_items_from_g1m_file(path)
    elif os.path.isdir(path):
        print(f'Processing UCB dir: {path}')
        items = load_items_from_ucb_dir(path)
    else:
        print('Could not load items: unknown input')
        return 2

    if items.program_count == 0:
        print(f'No programs could be loaded')
        return 2

    # check to see if we're loading a program with the given name
    program = None
    if prog_name:
        prog_name_casio = translate_ascii_bytes_to_casio(prog_name.encode('ascii'))
        program = items.get_program_by_name(prog_name_casio)
        if program is None:
            program_names = ', '.join(items.get_program_names())
            print(
                f'Could not find program "{prog_name}". '
                f'Available: {program_names}'
            )
            return 2

    with CasioSystem(items) as casio:
        try:
            while True:
                if program is None:
                    # display a program selection using the machine
                    program = casio.show_menu()
                print(f'Running program: "{program.stringname}"')
                casio.run(program.name)
                casio.wait_for_any_key()
                program = None
        except InterpreterQuitException:
            return 0
        except:
            e = sys.exc_info()
            trace = '' if e[0] is None else ''.join(traceback.format_exception(*e))
            print(trace)
            print((casio.vars))
            print((casio.mats))
            return 2

        # wait for user to close program
        #casio.idle()

    return 0


if __name__ == '__main__':
    if len(sys.argv) == 2:
        sys.exit(main(sys.argv[1]))
    if len(sys.argv) == 3:
        sys.exit(main(sys.argv[1], sys.argv[2]))
    else:
        print(f'Usage: {sys.argv[0]} <file.g1m> [PROG_NAME]')
        sys.exit(1)
