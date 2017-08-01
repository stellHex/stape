from __future__ import print_function
from stapler import Loop, StapeRun
import os, sys, re, time
q = quit
tutorial = '''Commands:
      :\texecute one cycle
   INT:\texecute INT cycles
tFLOAT:\tsets cycle delay to FLOAT seconds; at <0.01 the interpreter does not show intermediate states.
     r:\texecute number of cycles last specified
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
        cycles = 512
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
      try:
        input = raw_input('[]> ').strip()
        if 'q'.lower() in input: break
        if not input: input = '1'
        try:
            int(input)
            input = '0'+input
        except ValueError: pass
        cmd = input[0]
        if '0' == cmd or 'r' == cmd or 'a' == cmd:
            if cmd == 'r': input = repeat
            if cmd == 'm': input = maxim
            input = min(int(input), maxim)
            if input != 1: repeat = input
            val, t = input,300
            if delay < 0.01:
                run.next(input)
                clear()
                print('Buffer:', run.buffer)
                print(run.main)
            while val > 0 and t > 0:
                clear()
                run.next(1)
                print('Output:', run.output)
                print('Buffer:', run.buffer)
                print(run.main)
                if run.done: break
                val -= 1
                t -= delay
                if val > 0: time.sleep(delay)
        elif 't' == cmd: delay = float(input[1:])
        elif 'm' == cmd: maxim = int(input[1:])
        elif 'h' == cmd: print(tutorial)
        else: print('Huh?')
        if run.done: break
      except ValueError: print('I don\'t think that\'s a number.')

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