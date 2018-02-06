from decoder import G1mFile, CasioProgram
from machine import CasioInterpreter

def main(filepath):
    g1mfile = G1mFile(filepath)

    print 'Processing G1M file...'
    programs = g1mfile.load()

    num_programs = len(programs)
    print 'Done, found %d programs:' % (num_programs,)
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
    from sys import exit, argv as args

    if len(args) == 2:
        # debugging: remove assignment
        exit(main(args[1]))
    else:
        print 'Usage: %s <file.g1m>' % (args[0],)
        exit(1)
