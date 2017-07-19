# Stape

An office-supplies-based programming language

## Structure

A running Stape program consists of a tape, an instruction pointer, sometimes a staple pointer, and a buffer. The tape is a loop of sort-of ASCII characters, initialized by the program. The instruction pointer moves along it, auto-incrementing each instruction step. The buffer is a transient floating memory cell, of the same type as those on the tape.

### Staples

Stape's tape emulates a real, if unusually long and resilient, strip of paper, in that it can be "stapled" into loops, demarcated by `[]`. This is best described using a diagram:
``` 
    v
----A--[]-------
      /  \
    /      \
   |        |
    \  v   /
      -B--
```
If a pointer at spot A moves rightwards along the tape, it can't pass the staples, and will treat the loop as if it were a single cell (even though it looks like 2 in the diagram, and in programs). If a pointer at spot B moves to the right, it can't pass the staples, and will end up passing over the cell of the staples and repeating what it just did--so the "loops of paper" also serve as actual loops for control flow. The loops never "go the other way"; that would be useless, and people who waste staples don't get stapler privileges.


### Program

When the interpreter runs a Stape program, it first strips all newlines and leading spaces, and then makes sure that the `[]` are balanced; if they are not, the program fails to compile. Then it "staples" all loops recursively, starting from those with no subloops. Each time it staples a loop, the program makes sure it contains an odd number of cells (an even number of cells not counting the `[]` being stapled); if it does not, the program fails to run. It then treats the entire program as if it were enclosed in [], and staples the ends, again failing if the resulting tape has even parity. The pointer starts at cell 0, the `][` cell created by the last stapling.

## Execution

The Stape tape functions as both data storage and program. Each execution step, the instruction pointer first moves right, then reads its current cell as an operator and *the cell in the opposite index*, reflected over the `][` of the current loop, as the argument. When the pointer is inside a loop, the cell containing the staples is considered to be cell 0, with the indices being modular mod the length of the loop. Loops always have an odd number of cells, so `][`, which is a nop, will always be the only one with no opposite cell.

### Operators

All operations fail silently if they get an incompatible type.

Op|Type|Effect|Mnemonic
--- | --- | --- | ---
`[]`|Any|nop|staples
`][`|Any|nop|staples
`:`|Any|standard nop|staple holes
`<`|Any||stapler
`>`|Any|copy the operand to the buffer, staple a new loop between the operator and the operand (non-inclusive), and delete the operand (as if it had been stapled over)|stapler
`{`|Loop|unroll loop, adding a `:` at the end|unstapler
`C`|Any|copy the operand to the buffer|"copy"
`X`|Loop|copy the operand to the buffer and replace it on the tape with `:`|scissors
`V`|Any|replace the operand with the buffer, and clear the buffer; fails silently if the buffer is empty|XCV
`I`|Int|read a number of characters equal to the twice the operand and staple them into a loop which goes in buffer; if the operand is negative, read until EOF/EOT instead; if the operand isn't an int, read a single character and don't staple|"in"
`O`|Any|write the buffer to stdout, not including the outermost staples and not expanding any sub-loops, and clear the buffer|"out"
`#`|Nonloop|Put the operand's ASCII value, stapled as a 0-padded 4-digit base 10 number, into the buffer|keypad
`+`|Int|Add the operand and the buffer (if the buffer is empty or not an integer, treat it as 0), and put the result in the buffer as a potentially-0-padded even-digited base 10 number|+

When an operator asks for an int, and gets a character aside from 0-9, it silently fails unless otherwise specified. When it asks for an int and gets a loop, all decimal digits inside of the loop are extracted (non-recursively), put in order, interpreted as a number, and then multiplied by -1 to the power of the number of `-`s inside the loop.
