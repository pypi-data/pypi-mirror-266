# gasm
The Gheith ISA assembler.

For students in Dr. Gheith's CS 429H course completing pipelining.

## Quick Start

```
python3 -m pip install gasm
```
And, you're good to go. 👍

## Usage

### Assembling:

```
gasm <path to assembly file> <OPTIONAL: path to desired output file>
```

There are relatively few restrictions on the assembly file. The file extension, for example, is entirely unimportant. However, designations `r` for registers and `#` for literals are now required.

Take the following as a basic example:

```
// place at memory location 0
@0
movl r0, #104 // print 'h'
movl r0, #101 // print 'e'
movl r0, #108 // print 'l'
movl r0, #108 // print 'l'
movl r0, #111 // print 'o'
movl r0, #10  // print '\n'
end
```

You may choose to end your assembly with an `end` directive. Doing so, the assembler will provide the hex instruction `ffff` in its place.

### Disassembling:

```
dasm <path to .hex file> <OPTIONAL: path to desired output file>
```

The file you want to disassemble should be valid `.hex`. It may, however, end with an `ffff`, though the instruction is not officially recognized.

### Numerical Literals:

In the case of the `movl` and `movh` instructions, you may use either hex or decimal to represent numerical literals. gasm assumes decimal by default; to use hex, prefix the literal with `0x`:

```
@0
movl r1, #0x21
```

### Character Literals:

gasm supports the use of character literals in place of numerical ones. Suppose you wanted to store the ASCII value for 'a' into `r1`:

```
@0
movl r1, 'a'
```

### Labels:

To assist in creating programs with branches, gasm supports use of labels. Create a label like so:

```
my_first_label:
<instruction 1>
<instruction 2>
...
```

Reference them in `movl` or `movh` with the label name.

```
@0
movl r1, my_first_label
...
```

#### Misaligned Labels

There may also be cases where one wishes to create misaligned labels (as in, `byte_addr + 1`). Here, one may use the `!mis_` prefix to the label.

```
!mis_my_first_label:
...
```

#### Generated Comments

All labels generate a comment in the `.hex` of the form:

```
// [PC: <PC>] <<LABEL>>:
```

### Directive Blocks:

gasm supports a few different directives that are outlined here. Directives start with an `@BEGIN` and end with an `@END`. Directive bounds are placed in comments; use the below example for reference:

```
// @BEGIN <DIRECTIVE NAME>
...
// @END <DIRECTIVE NAME>
```

#### Data

Programs may find it helpful to have a data section occasionally. Now, you can specify that a section of memory contains data instead of instructions with the `DATA` directive.

```
@0
movl r1, #0
movl r2, #33
st r1, r2       // mem[0x21] <= 0
                // should form:
                //
                // @10
                // 0061
                // 0000
                //
movl r3, #32    // get word at 0x10
ld r0, r3       // print ascii('0x61') ('a')

// @BEGIN DATA
@10
ff61            // now, gasm is sure that these
00ff            // are not instructions
// @END DATA
```

#### Misalignment

Some programs may leverage misalignment for one reason or another. As such, gasm supports writing instructions that will be stored in a misaligned fashion with the `MISALIGNED` directive. It is used functionally the same as the `DATA` directive.

```
@0
movl r1, !mis_first_jmp
jnz r1, r1

// @BEGIN MISALIGNED
!mis_first_jmp:
movl r0, #97
movl r0, #98
movl r1, second_jmp
jnz r1, r1
// @END MISALIGNED

second_jmp:
movl r0, #99
end
```

The above code assembles to:

```
@0
8051
e111

// @BEGIN MISALIGNED
// [PC: 0x5] <!mis_first_jmp>:
10ff
2086
e186
1180
ffe1
// @END MISALIGNED

// [PC: 0xe] <second_jmp>:
8630
ffff
```

The misaligned instructions are padded with `ff`; you can verify that the above translation is correct.

Another aspect to note is the use of the `!mis_` label.

### Comments:

You may find it important to comment your `.hex` output for test case quality. gasm supports this functionality, and should maintain your comments when assembling. For example, the above code assembles to:

```
// place at memory location 0
@0
8680	// print 'h'
8650	// print 'e'
86c0	// print 'l'
86c0	// print 'l'
86f0	// print 'o'
80a0	// print '\n'
ffff
```

Note that within `MISALIGNED` blocks, comments are not preserved. There is not a great uniform standard, so you will need to comment this portion of your `.hex` manually.

dasm also supports having comments in the `.hex`, though I chose not to display them because of clutter.
