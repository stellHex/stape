from __future__ import print_function
from stapler import Loop, StapeRun
import os, sys, re, time
q = quit
tutorial = '''Commands:
      :\texecute one cycle
   INT:\texecute INT cycles
tFLOAT:\tsets cycle delay to FLOAT seconds; at <0.01 the interpreter does not show intermediate states.
     r:\trestart the program
  mINT:\tsets max number of cycle executed at once (default 1024); cycles are also bounded by 300/delay
     a:\texecutes max number of cycles
     h:\tshow this help screen'''

def r_cmd(run, delay, val):
    val = int(val)
    t = 300
    if delay == 0:
        run.next(val)
        return delay
    while val > 0:
        clear()
        run.next(1)
        print(next)

def clear():
    if sys.platform[0] == 'w': os.system('cls')
    else: os.system('clear')

def gooey(run, interactive=False):
    if not interactive:
        cycles = 16384
        run.next(cycles)
        while(True):
            run.next(cycles)
            if run.done: break
            if raw_input('\n' + str(cycles*2) + ' cycles elapsed. Keep trying? (Y/n): ') not in 'Yy': break
            cycles *= 2
        return
    delay = 0.1
    maxim = 1024
    repeat = 1
    clear()
    print(run.main)
    print(tutorial)
    while True:
        inp = raw_input('[]> ').strip()
        for input in inp.split(' '):
            try:
                if not input: input = '1'
                try:
                    int(input)
                    input = '0'+input
                except ValueError: pass
                cmd = input[0]
                if '0' == cmd or 'a' == cmd:
                    if cmd == 'm': input = maxim
                    input = min(int(input), maxim)
                    if input != 1: repeat = input
                    val, t = input,300
                    if delay < 0.01:
                        run.next(input)
                        clear()
                        print('Output: ', run.output)
                        print('Buffer: ', run.buffer)
                        print(run.main)
                    else:
                        while val > 0 and t > 0:
                            run.next()
                            clear()
                            print('Output: ', run.output)
                            print('Buffer: ', run.buffer)
                            print(run.main)
                            if run.done: break
                            val -= 1
                            t -= delay
                            if val > 0: time.sleep(delay)
                elif 'r' == cmd: 
                    run.restart()
                    clear()
                    print('Output: ', run.output)
                    print('Buffer: ', run.buffer)
                    print(run.main)
                elif 'l' == cmd: 
                    try: 
                        newRun = stapleFromFile(sys.argv[1])
                        if newRun is not None: run = newRun
                    except IndexError:
                        print('No file specified!')
                        continue
                    clear()
                    print('Output:', run.output)
                    print('Buffer:', run.buffer)
                    print(run.main)
                elif 't' == cmd: delay = float(input[1:])
                elif 'm' == cmd: maxim = int(input[1:])
                elif 'h' == cmd: print(tutorial)
                elif 'q' not in input: 
                    print('Whats "{}"?'.format(cmd))
                    break
                if run.done: break
            except ValueError: print('I don\'t think that\'s a number.')
        if 'q' in inp: break

theRun = None
def stapleFromFile(path):
    try:
        return StapeRun(open(path).read())
    except IOError:
        try:
            return StapeRun(open(path+'.stape').read())
        except IOError:
            print('No such file!')
            return None

try:
    theRun = stapleFromFile(sys.argv[1])
    if theRun is not None: gooey(theRun, sys.flags.interactive)
except IndexError: 
    if not sys.flags.interactive: print('No file specified!')
