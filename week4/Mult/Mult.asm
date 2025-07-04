// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

//// Replace this comment with your code.

@R0
D=M
@multiply
M=D

@R1
D=M
@counter
M=D

@R2
M=0 //initialize result

(LOOP)
    @counter
    D=M
    @END
    D;JEQ //if counter == 0, jump to end

    //add R1
    @multiply
    D=M
    @R2
    M=D+M

    //decrement counter
    @counter
    M=M-1
    // go to loop
    @LOOP
    0;JMP
(END)
    @END
    0;JMP