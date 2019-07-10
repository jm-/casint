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

from decoder import G1mFile, CasioProgram
from machine import CasioMachine, InterpreterQuitException
from casiosystem import ProgramMenu


def main(filepath):
    g1mfile = G1mFile(filepath, debug=False)

    print(f'Processing G1M file: {filepath}')
    programs = g1mfile.load()
    num_programs = len(programs)

    with CasioMachine(programs) as casio:
        menu = ProgramMenu(casio, programs)

        try:
            while True:
                # TODO: replace with choose_program method
                # for i in range(num_programs):
                #     print(f'{i:2d} {programs[i]}')
                # selection = -1
                # while not (0 <= selection < num_programs):
                #     try:
                #         selection = int(input('choose: '))
                #     except KeyboardInterrupt:
                #         return 0
                #     except:
                #         selection = -1
                
                # display a program selection using the machine
                selection = menu.show()
                casio.run(programs[selection].name)
        except InterpreterQuitException:
            return 0
        except:
            e = sys.exc_info()
            trace = '' if e[0] is None else ''.join(traceback.format_exception(*e))
            print(trace)
            #print((casio.vars))
            #print((casio.mats))
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
