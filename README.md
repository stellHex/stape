# Stape

An office-supplies-based programming language

## Structure

A running Stape program consists of a tape, an instruction pointer, some number of 0 pointers, and a buffer. The tape is a looping tape of cells, initialized by the program. The instruction pointer moves along it, auto-incrementing each instruction step. The buffer is a transient floating memory cell, of the same type as those on the tape.

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

Every stapled loop has exactly one 0 pointer. When a loop is stapled, its 0 pointer is created at its `][` cell. When a loop is unstapled, its 0 pointer is destroyed.


### Program

When the interpreter runs a Stape program, it first strips all newlines and leading spaces, and then makes sure that the `[]` are balanced; if they are not, the program fails to compile. Then it "staples" all loops recursively, starting from those with no subloops. Each time it staples a loop, the program makes sure it contains an odd number of cells (an even number of cells not counting the `[]` being stapled); if it does not, the program fails to run. It then treats the entire program as if it were enclosed in [], and staples the ends, again failing if the resulting tape has even parity. The pointer starts at cell 0, the `][` cell created by the last stapling.

## Execution

The Stape tape functions as both data storage and program. Each execution step, the instruction pointer first moves right, then reads its current cell as an operator and *the cell in the opposite index*, reflected over the 0 pointer of the current loop, as the argument. Instructions fail silently if the instruction pointer is at the same cell as the 0 pointer. When the pointer is inside a loop, the cell containing the staples is considered to be cell 0, with the indices being modular mod the length of the loop.

Execution ends when the main loop is unstapled.

### Type Classifications

Operations fail silently if they get a cell which does not conform to its expected type

Name | Description
--- | ---
-|Any cell (for nullary operations)
Any|Any cell except `][` cells
Loop|`[]` cells
Character|Any cell except `][` and `[]` cells
Int|`[]` cells and `0`-`9` cells

### Operators

All characters not included in this list are nops.

Op|Type|Effect|Mnemonic
--- | --- | --- | ---
`[]`|-|nop|staples
`][`|-|nop|staples
`:`|-|standard nop|staple holes
`<`|Any|copy the operand to the buffer, staple a new loop between the operator and the operand (non-inclusive), and delete the operand's cell (as if it had been stapled over)|stapler
`>`|Any|Same as `>`, except the pointer also moves into the resulting loop at its 0 cell|stapler
`=`|Loop|move the pointer into the operand, at its `][` cell|stack
`_`|-|move the pointer out of the current loop, appearing at the corresponding `[]` in the parent loop|stack
`{`|Loop|unstaple the operand, adding a `:` at the end|unstapler
`}`|-|unstaple the current loop, adding a `:` at the end|unstapler
`@`|-|move the 0 pointer of the current loop to the operand's cell|paperclip
`C`|Any|copy the operand to the buffer|"copy"
`X`|Any|copy the operand to the buffer and replace it on the tape with `:`|scissors
`V`|Any|replace the operand with the buffer, and clear the buffer; fails silently if the buffer is empty|XCV
`I`|Any|if the operand isn't an int, read a character into the buffer; if it is, read a number of characters equal to the twice the operand and staple them into a loop which goes in buffer; if the operand is negative, read until EOF/EOT and `:`-pad to even parity|"in"
`O`|Any|write the buffer to stdout, not including the outermost staples and not expanding any sub-loops, and clear the buffer|"out"
`#`|Character|Put the operand's ASCII value, stapled as a `0`-padded 4-digit base 10 number, into the buffer|keypad
`+`|Int|Add the operand and the buffer (if the buffer is empty or not an integer, treat it as 0), and put the result in the buffer as a 0-padded even-digited base 10 number|+

When an operator asks for an int, and gets a character aside from `0`-`9`, it silently fails. When it asks for an int and gets a loop, all decimal digits inside of the loop are extracted (non-recursively), put in order, interpreted as a number, and then multiplied by -1 to the power of the number of `-`s inside the loop. If there are no digits inside the loop, the result is 0.
