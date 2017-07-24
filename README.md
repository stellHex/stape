# Stape

An office-supplies-based esoteric programming language.

## Structure

A running Stape program consists of a tape, an instruction pointer (IP), some number of days pointers (DPs), and a buffer. The tape is a looping tape of cells, initialized by the program. The IP moves along it, auto-incrementing each instruction step. DPs also move along the tape, but only one of them is active at a time, and it can move in either direction at a program-defined speed, although by default they auto-decrement. The buffer is a transient floating memory cell, of the same type as those on the tape.

### Staples

Stape's tape emulates a real, if unusually resilient, strip of paper, in that it can be "stapled" into loops, demarcated by `[]`. This is best described using a diagram:
``` 
    v
----A--[]-------
      /  \
    /      \
   |        |
    \  v   /
      -B--
```
If a pointer at spot A moves rightwards along the tape, it can't pass the staples (`[]`), and will treat the loop as if it were a single cell (even though it looks like 2 in the diagram, and in programs). If a pointer at spot B moves to the right, it can't pass the staples (`][`), and will end up passing over the cell of the staples and repeating what it just did--so the "loops of paper" also serve as actual loops for control flow. The loops never "go the other way"; that would waste staples, and interpreters who waste staples lose stapler privileges.

Every stapled loop has exactly one DP. The active DP is the one in the same loop as the IP, and it only moves when the DP moves. When a loop is stapled, its DP is created at its `][` cell. When a loop is unstapled, its DP is destroyed.


### Program

A valid Stape program is any string with all unescaped `[]` balanced. The escape character is `\`. Newlines and leading whitespace are ignored, unless they are escaped. Unlike in many other syntaxes, an escaped character which has no escaped meaning is ignored entirely, instead of treated as unescaped.

When the interpreter runs a Stape program, it first makes sure the program is valid, then it "staples" all loops recursively, starting from those with no subloops. It then treats the entire program as if it were enclosed in `[]`, and staples the ends into a loop, called the main loop. The IP starts at the `][` cell of the main loop.

## Execution

The Stape tape functions as both data storage and program. Each execution step, the pointers first move, then the instruction in the cell under the IP is executed with the cell under the DP as the operand. Execution ends when the main loop is exited or unstapled.

### Type Classifications

Operations fail silently if they get a cell which does not conform to its expected type.

Name | Description
--- | ---
-|Any cell (for nullary operations)
Any|Any cell except `][` cells
Loop|`[]` cells
Character|Any cell except `][` and `[]` cells
Int|`[]` cells, `0`-`9` cells, and `-` cells

### Operators

All characters not included in this list are nops.

Any operator with more than 1 definition uses the definition with the strictest applicable type.

Op|Type|Effect|Mnemonic
--- | --- | --- | ---
`[]`|-|nop|staples
`][`|-|nop|staples
`:`|-|standard nop|staple holes
`<`|Any|copy the operand to the buffer, staple a new loop between the operator and the operand (non-inclusive), and delete the operand's cell (as if it had been stapled over)|stapler
`>`|Any|Same as `>`, except the IP also moves into the resulting loop at its 0 cell|stapler
`=`|Loop|move the IP into the operand, at its `][` cell|stack
`_`|-|move the IP out of the current loop, appearing at the corresponding `[]` in the parent loop|stack
`{`|Loop|unstaple the operand, adding a `:` at the end|unstapler
`}`|-|unstaple the current loop, adding a `:` at the end|unstapler
`@`|Int|"roll" the current loop backwards by moving the IP and DP forwards, a number of stops equal to the operand|tape dispenser
`%`|Int|set the speed of the DP (in cells/step) to the operand|date
`C`|Any|copy the operand to the buffer|"copy"
`X`|Any|copy the operand to the buffer and replace it on the tape with `:`|scissors
`V`|Any|replace the operand with the buffer, and clear the buffer; fails silently if the buffer is empty|XCV
`I`|Int|read a number of characters equal to the twice the operand and staple them into a loop which goes in the buffer.|"in"
`O`|Any|write the buffer to stdout, not including the outermost staples and not expanding any sub-loops, and clear the buffer|"out"
`#`|Character|put the operand's ASCII value, stapled as a `0`-padded 3-digit base 10 number, into the buffer|keypad
`#`|Loop|read the operand as an integer and put the nicely-formatted (matching `/-?\d+/`) result  in the buffer|keypad
`M`|Int|put the operand's corresponding ASCII character into the buffer|"letter"
`+`|Int|add the operand and the buffer (if the buffer is empty or not an integer, treat it as 0), and put the result in the buffer as a stapled base 10 number|+
`*`|Int|same as `*`, except with multiplication|\*

When an operator asks for an int, and gets a character aside from `0`-`9` or `-`, it silently fails. When it asks for an int and gets `-`, it takes that to be -1. When it asks for an int and gets a loop, all decimal digits inside of the loop are extracted (non-recursively), put in order, interpreted as a number, and then multiplied by -1 to the power of the number of `-`s inside the loop. If there are no digits inside the loop, the result is 0.

## Representation

It is difficult to read a Stape program as a linear string, and difficult to tell which loop pointers are meant to be occupying. Generating ASCII art has its own set of difficulties. Therefore, I propose the following method of representation. The program
```                                 v
[abcdefg[hij]klmnop[qrst[uvw]xyz[012345]6789]]
           '       '        '   '     '
```
becomes
```
[abcdefg[0]klmnop[1]]
                  '
  0 [hij]
       '
  1 [qrst[0]xyz[1]6789]
                '
      1.0 [uvw]
          '   
      1.1 [012345]
           ^    '
```
For representations of program states in which the IP is in the same spot as a DP, the `"` character is recommended. For representations in both formatting and monospace, it is recommended to use highlighting to represent data pointers, nearly halving the size of the representation. 
