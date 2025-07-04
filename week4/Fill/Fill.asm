// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

//// Replace this comment with your code.

(LOOP)
    @KBD
    D=M
    @DRAW_BLACK
    D;JNE
    @DRAW_WHITE
    0;JMP

// ========== DRAW BLACK ==========
(DRAW_BLACK)
    @8192         // total number of screen words (256x512 / 16)
    D=A
    @counter
    M=D

    @SCREEN
    D=A
    @addr
    M=D

    @color
    M=-1          // black (all bits set)

(DRAW_LOOP_BLACK)
    @counter
    D=M
    @LOOP
    D;JEQ         // done drawing, go back to checking keyboard

    @color
    D=M
    @addr
    A=M
    M=D           // set pixel

    @addr
    M=M+1         // addr++

    @counter
    M=M-1         // counter--

    @DRAW_LOOP_BLACK
    0;JMP

// ========== DRAW WHITE ==========
(DRAW_WHITE)
    @8192
    D=A
    @counter
    M=D

    @SCREEN
    D=A
    @addr
    M=D

    @color
    M=0           // white (all bits clear)

(DRAW_LOOP_WHITE)
    @counter
    D=M
    @LOOP
    D;JEQ

    @color
    D=M
    @addr
    A=M
    M=D

    @addr
    M=M+1

    @counter
    M=M-1

    @DRAW_LOOP_WHITE
    0;JMP