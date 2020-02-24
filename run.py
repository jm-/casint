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

from decoder import load_programs_from_ucb_dir, load_programs_from_g1m_file
from machine import CasioMachine, InterpreterQuitException
from casiosystem import ProgramMenu


def main(path):
    # if the path is a dir, load programs from ucb.
    # else, read as g1m.
    if os.path.isfile(path):
        print(f'Processing G1M file: {path}')
        programs = load_programs_from_g1m_file(path)
    elif os.path.isdir(path):
        print(f'Processing UCB dir: {path}')
        programs = load_programs_from_ucb_dir(path)
    else:
        print('Could not load programs: unknown input')
        return 2

    with CasioMachine(programs) as casio:
        menu = ProgramMenu(casio, programs)

        try:
            while True:
                # display a program selection using the machine
                selection = menu.show()
                casio.run(programs[selection].name)
                casio.wait_for_any_key()
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
    else:
        print(f'Usage: {sys.argv[0]} <file.g1m>')
        sys.exit(1)
