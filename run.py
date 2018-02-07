import os
import sys

try:
    import sdl2
except ImportError:
    import platform
    arch, osname = platform.architecture()
    if osname == 'WindowsPE':
        os.environ['PYSDL2_DLL_PATH'] = 'lib/32' if arch == '32bit' else 'lib/64'

from decoder import G1mFile, CasioProgram
from machine import CasioInterpreter

def main(filepath):
    g1mfile = G1mFile(filepath)

    print 'Processing G1M file...'
    programs = g1mfile.load()

    num_programs = len(programs)
    print 'Done, loaded %d programs:' % (num_programs,)
    for i in range(num_programs):
        print '%2d: %s' % (i, programs[i])

    selection = -1
    while not (0 <= selection < num_programs):
        try:
            selection = input('choose: ')
        except KeyboardInterrupt:
            return 0
        except:
            selection = -1

    with CasioInterpreter(programs) as interpreter:
        try:
            interpreter.run(programs[selection].name)
        except:
            import sys, traceback
            e = sys.exc_info()
            trace = '' if e[0] is None else ''.join(traceback.format_exception(*e))
            print trace
            #return 2

        # wait for user to close program
        interpreter.idle()

    return 0

if __name__ == '__main__':

    if len(sys.argv) == 2:
        # debugging: remove assignment
        sys.exit(main(sys.argv[1]))
    else:
        print 'Usage: %s <file.g1m>' % (sys.argv[0],)
        sys.exit(1)
