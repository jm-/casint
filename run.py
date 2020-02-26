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

from casint.loader import load_programs_from_ucb_dir, load_programs_from_g1m_file
from casint.machine import CasioMachine, InterpreterQuitException
from casint.casiosystem import ProgramMenu


def main(path, prog_name=None):
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

    # check to see if we're loading a program with the given name
    selection = None
    if prog_name:
        # run program with the given name
        for index, program in enumerate(programs):
            if program.stringname == prog_name:
                selection = index
                break
        if selection is None:
            program_names = ', '.join(map(lambda p: p.stringname, programs))
            print(
                f'Could not find program "{prog_name}". '
                f'Available: {program_names}'
            )
            return 2

    with CasioMachine(programs) as casio:
        menu = ProgramMenu(casio, programs)

        try:
            while True:
                if selection is None:
                    # display a program selection using the machine
                    selection = menu.show()
                program = programs[selection]
                print(f'Running program: "{program.stringname}"')
                casio.run(program.name)
                casio.wait_for_any_key()
                selection = None
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
