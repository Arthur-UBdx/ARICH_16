# Instructions ARICH-16

## Instructions

### General Purpose Instructions

| Mnemonic | Description                                    | Opcode | Operands | Usage      |
|----------|-------------                                   |--------|----------| -------      |
| NOOP     | No operation                                   | 0x--00   |          | NOP          |
| MOV      | Move from operand A to C                       | 0x--01   | 2        | MOV \<A> \<C>|
| PUSH     | Push A onto the stack                          | 0x--02   | 1        | PUSH \<A>     |
| POP      | Pop from the stack to C                        | 0x--03   | 1        | POP \<C>    |
| STR      | Store B into the memory at adress MemAddr      | 0x--04   | 2        | STR \<MemAddr> \<B> |
| LDR      | Load from memory at address MemAddr into C     | 0x--05   | 2        | LDR \<MemAddr> \<C> |
| ... | *Reserved* | 0x--06-0x--0F | | |

### Arithmetic Instructions

| Mnemonic | Description                             | Opcode | Operands | Usage      |
|----------|-------------                            |--------|----------| -------      |
| ADD      | Add A and B and stores it in C          | 0x--10   | 3        | ADD \<A> \<B> \<C> |
| SUB      | Subtract A and B and stores it in C     | 0x--11   | 3        | SUB \<A> \<B> \<C> |
| MUL      | Multiply A and B and stores it in C     | 0x--12   | 3        | MUL \<A> \<B> \<C> |
| INC      | Increment A by 1 and stores it in C     | 0x--13   | 1        | INC \<A> |
| DEC      | Decrement A by 1 and stores it in C     | 0x--14   | 1        | DEC \<A> |

### Logical Instructions

| Mnemonic | Description                                            | Opcode   | Operands | Usage                 |
|----------|-------------                                           |--------  |----------| -------               |
| AND      | Bitwise AND of A and B and stores it in C              | 0x--15   | 3        | AND \<A> \<B> \<C>    |
| OR       | Bitwise OR of A and B and stores it in C               | 0x--16   | 3        | OR \<A> \<B> \<C>     |
| XOR      | Bitwise XOR of A and B and stores it in C              | 0x--17   | 3        | XOR \<A> \<B> \<C>    |
| NOT      | Bitwise NOT of A                                       | 0x--18   | 1        | NOT \<A>              |
| SHL      | Shift A left by B bits                                 | 0x--19   | 2        | SHL \<A> \<B>         |
| SHR      | Shift A right by B bits                                | 0x--1A   | 2        | SHR \<A> \<B>         |
| ASHR     | Arithmetic shift A right by B bits                     | 0x--1B   | 2        | ASHR \<A> \<B>        |
| ROL      | Rotate A left by B bits                                | 0x--1C   | 2        | ROL \<A> \<B>         |
| ROR      | Rotate A right by B bits                               | 0x--1D   | 2        | ROR \<A> \<B>         |
| ... | *Reserved* | 0x--1E-0x--1F | | |

### Comparison Instructions

| Mnemonic | Description                             | Opcode | Operands | Usage|
|----------|-------------                            |--------|----------| -------|
| JMP      | Jump to address                         | 0x--20   | 1        | JMP \<PCAddr>|
| IFLE     | Jump to address if A <= B               | 0x--21   | 3        | IFLE \<A> \<B> \<PCAddr> |
| IFLT     | Jump to address if A < B                | 0x--22   | 3        | IFLT \<A> \<B> \<PCAddr> |
| IFEQ     | Jump to address if A == B               | 0x--23   | 3        | IFEQ \<A> \<B> \<PCAddr> |
| IFGE     | Jump to address if A >= B               | 0x--24   | 3        | IFGE \<A> \<B> \<PCAddr> |
| IFGT     | Jump to address if A > B                | 0x--25   | 3        | IFGT \<A> \<B> \<PCAddr> |
| IFNE     | Jump to address if A != B               | 0x--26   | 3        | IFNE \<A> \<B> \<PCAddr> |
| IFNZ     | Jump to address if A != 0               | 0x--27   | 2        | IFNZ \<A> \<PCAddr> |
| IFZ      | Jump to address if A == 0               | 0x--28   | 2        | IFZ \<A> \<PCAddr> |
| ... | *Reserved* | 0x--38-0x--3F | | |

### Control Instructions

| Mnemonic | Description                             | Opcode | Operands | Usage        |
|----------|-------------                            |--------|----------| -------      |
| CALL     | Call a function                         | 0x--30   | 1        | CALL \<PCAddr>|
| RET      | Return from a function with a value     | 0x--31   | 1        | RET \<A>         |
| HALT     | Halt the program                        | 0x--32   | 0        | HALT         |
| ... | *Reserved* | 0x--34-0x--3F | | |

## Registers and Flags

### Registers

| Name      | Adress    | Description |
|------     |-------    |-------------|
| R0-R7     | 0x0000-0x0007 | General purpose registers |
| PC        | 0x0010      | Program Counter, it's not recommanded to modify this register by hand, prefer using JMP instruction |
| SP        | 0x0011      | Stack Pointer; NOTE: The stack moves downwards, so when using POP, the SP will decrement by 1, making it important to set the BP to something else than 0 to avoid stack overflow |
| BP        | 0x0012      | Base Pointer; NOTE: Changing the base pointer value will also modify the stack pointer value |
| FL        | 0x0013      | Flags Register |
| FR        | 0x0014      | Function Return Register |
| FA0-FA3   | 0x0015-0x0018 | Function Arguments Registers|
| ...       | 0x0019-0x001F | *Reserved* |
| ...       | 0x0020-0xFFFF | Other peripherals |

### Flags

| Name | Bit | Description |
|------|-----|-------------|
| AF   | 0   | ALU Flag (Overflow or Sign) |
| SOVF | 1   | Stack Overflow Flag |
| SUDF | 2   | Stack Underflow Flag |
| ...  | 3-16 | *Reserved* |

## OPCODES decoding

| Bit(s) | Use |
|--------|-----|
| 0-7    | OPCODE |
| 8      | Use first operand value as an Immediate Value |
| 9      | Use second operand value as an Immediate Value |
| 10-15  | *Reserved* |

## Special Characters

| Character | Description | Example |
|-----------|-------------|---------|
| %  | Refers to a register | `MOV %R0 %R1` moves the contents of `R0` in the register `R1` |
| &  | Refers to a variable (address in memory) | `LDR &my_var %R0` moves the contents of `my_var` in the register `R0` |
| $  | Use the given value as an immediate value instead of an adress | `MOV $0x10 %R0` moves the value `0x10` in the register `R0` |
| :  | Refers as a label for a jump instruction | `JMP :my_label` jumps to the label `my_label`, which is set by writing `:label` where the label is to be put |
| #  | Is used for macros | `#define my_var 0x10` tells the assembler that the variable `my_var` is at the adress `0x10`|
| // | Is used for comments | `// This is a comment` This is a comment and will be ignored by the assembler |

## Macros

| Keyword | Description | Example | Notes |
|---------|-------------|---------|-------|
| #stack | Defines the size of the stack | `#stack 0x10` tells the assembler that the stack is 16 addresses long | The stack should be defined before any variables, especially if no address for the said variable is given, to avoir the assembler handing addresses that would be used in the stack |
| #define | Defines a replacement macro | `#define value 0x10` tells the assembler that `value` has to be replaced by `0x10` ||
| #let | Defines a variable or a table | `#let my_var 0x10` tells the assembler that the variable `my_var` is at the adress `0x10`| Use `#let my_var[n] 0x10` for defining an array of size `n` starting at `0x10`. If no address are provided, the assembler will try to find an address for the variable/array|
| #deref  | Dereferences a variable or a table | `#deref my_var` tells the assembler that the variable `my_var` is no longer defined | Use `#deref my_var[]` to deref an array|
| #letreg | Defines a register at the given address | `#letreg PORTC 0xf0` tells the assembler that the register `PORTC` is located at address 0xf0 ||
