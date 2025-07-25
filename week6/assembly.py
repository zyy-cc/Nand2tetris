# Parser api, read instructions

from enum import Enum 

class Instruction(Enum):
    A_INSTRUCTION = 0
    C_INSTRUCTION = 1
    L_INSTRUCTION = 2

class Parser:
    def __init__(self, file_name):
        self.instructions = []
        # read the instructions, ignoring the white space and comments //
        try:
            with open(file_name, "r") as f:
                for line in f:
                    line = line.strip() # strip() removes the white spaces on both ends
                    if line == "" or line.startswith("//"):
                        continue 
                    l = line.split("//")[0].strip()
                    self.instructions.append(l)
        except FileNotFoundError:
            print(f"File {file_name} not found")
            return 
        
        self.current_idx = 0
        self.num_instruction = len(self.instructions)
        self.current_instruction = None

    def hasMoreLines(self):
        """
        check if there is more work to do 
        """
        return self.current_idx < self.num_instruction
        
    
    def advance(self):
        """
        gets the next instruction and makes it the current instruction
        """
        if self.hasMoreLines():
            self.current_instruction = self.instructions[self.current_idx]
            self.current_idx += 1
            return self.current_instruction
        return None 
    
    def instructionType(self):
        """
        return the instruction type
        """
        if self.current_instruction.startswith("@"):
            return Instruction.A_INSTRUCTION
        elif self.current_instruction.startswith("(") and self.current_instruction.endswith(")"):
            return Instruction.L_INSTRUCTION
        else:
            return Instruction.C_INSTRUCTION
        
    def symbol(self):
        """
        return the symbol (string) for A and L
        """
        if self.instructionType() == Instruction.A_INSTRUCTION:
            return self.current_instruction[1:].strip()
        elif self.instructionType() == Instruction.L_INSTRUCTION:
            return self.current_instruction[1:-1].strip()
        return None
    
    def dest(self):
        """
        dest = comp; jmp
        """
        if self.instructionType() == Instruction.C_INSTRUCTION:
            if "=" in self.current_instruction:
                return self.current_instruction.split("=")[0].strip()
            else:
                return "null"
        return None
    
    def comp(self):
        """
        dest = comp; jmp
        """
        if self.instructionType() == Instruction.C_INSTRUCTION:
            comp = self.current_instruction
            if "=" in comp:
                comp = comp.split("=")[1]
            if ";" in comp:
                comp = comp.split(";")[0]
            return comp.strip()
        return None
    
    def jump(self):
        if self.instructionType() == Instruction.C_INSTRUCTION:
            if ";" in self.current_instruction:
                return self.current_instruction.split(";")[1].strip()
            else:
                return "null"
        return None

class Code:
    def __init__(self):
        self.jump_dict = {
            "null": "000",
            "JGT"  : "001",
            "JEQ"  : "010",
            "JGE"  : "011",
            "JLT"  : "100",
            "JNE"  : "101",
            "JLE"  : "110",
            "JMP"  : "111"
        }

        self.comp_dict = {
        # a=0 group 
        "0"   : "0101010",
        "1"   : "0111111",
        "-1"  : "0111010",
        "D"   : "0001100",
        "A"   : "0110000",
        "!D"  : "0001101",
        "!A"  : "0110001",
        "-D"  : "0001111",
        "-A"  : "0110011",
        "D+1" : "0011111",
        "A+1" : "0110111",
        "D-1" : "0001110",
        "A-1" : "0110010",
        "D+A" : "0000010",
        "D-A" : "0010011",
        "A-D" : "0000111",
        "D&A" : "0000000",
        "D|A" : "0010101",

        # a=1 group 
        "M"   : "1110000",
        "!M"  : "1110001",
        "-M"  : "1110011",
        "M+1" : "1110111",
        "M-1" : "1110010",
        "D+M" : "1000010",
        "D-M" : "1010011",
        "M-D" : "1000111",
        "D&M" : "1000000",
        "D|M" : "1010101",
    }
    
    def dest(self, dest_mnemonic):
        """
        3 bits as a string
        """
        # string is immutable
        res = "000"
        if "M" in dest_mnemonic:
            res = res[:2] + "1"
        if "D" in dest_mnemonic:
            res = res[:1] + "1" + res[2:]
        if "A" in dest_mnemonic:
            res = "1" + res[1:]
        return res

    def comp(self, comp_mnemonic):
        """
        7 bits as a string
        """
        return self.comp_dict.get(comp_mnemonic, "0000000")
        
        

    def jump(self, jump_mnemonic):
        # value = dict.get(key, default_value)
        """
        3 bits as a string
        """
        return self.jump_dict.get(jump_mnemonic, "000")
            
    
class SymbolTable:
    def __init__(self):

        self.table = {
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
            "R0": 0,
            "R1": 1,
            "R2": 2,
            "R3": 3,
            "R4": 4,
            "R5": 5,
            "R6": 6,
            "R7": 7,
            "R8": 8,
            "R9": 9,
            "R10": 10,
            "R11": 11,
            "R12": 12,
            "R13": 13,
            "R14": 14,
            "R15": 15,
            "SCREEN": 16384,
            "KBD": 24576
        }
    
    def addEntry(self, symbol, address):
        """
        add <symbol, address> to the table
        """
        self.table[symbol] = address

    def contains(self, symbol):
        """
        check if symbol exists in the table
        """
        return symbol in self.table
        

    def getAddress(self, symbol):
        """
        returns the address associated with symbol
        """
        return self.table[symbol]
    
class HackAssembler:
    def __init__(self, file_name):
        self.file_name = file_name
        self.parser = Parser(file_name)
        self.code = Code()
        self.table = SymbolTable()
        self.next_ram_address = 16

    def first_pass(self):
        """
        focus on the (label) 
        adds the found labels to the symbol table
        """
        rom_address = 0
        while self.parser.hasMoreLines():
            instruction = self.parser.advance() 
            if self.parser.instructionType() == Instruction.L_INSTRUCTION:
                symbol = self.parser.symbol()
                if not self.table.contains(symbol):
                    self.table.addEntry(symbol, rom_address)
            
            else:
                rom_address += 1

    def second_pass(self, output_file):
        # reset the parser for the second pass 
        self.parser = Parser(self.file_name)

        with open(output_file, "w") as f:
            while self.parser.hasMoreLines():
                instruction = self.parser.advance()
                instruction_type = self.parser.instructionType()
                if instruction_type == Instruction.C_INSTRUCTION:
                    # dest = comp; jmp 
                    dest_bits = self.code.dest(self.parser.dest())
                    comp_bits = self.code.comp(self.parser.comp())
                    jump_bits = self.code.jump(self.parser.jump())

                    res = "111" + comp_bits + dest_bits + jump_bits + "\n"
                    f.write(res)
                elif instruction_type == Instruction.A_INSTRUCTION:
                    symbol = self.parser.symbol()
                    if symbol.isdigit():
                        # case 1: if xxx is a decimal value > 16-bit representation 
                        res = int(symbol)
                    else:
                        # case 2: if xxx is a symbol, get its address
                        if not self.table.contains(symbol):
                            self.table.addEntry(symbol, self.next_ram_address)
                            self.next_ram_address += 1
                        res = self.table.getAddress(symbol)
                    res = format(res, "016b")  # "016": pad the binary number with leading zeros so that it's exactly 16 bits long
                    f.write(res + "\n")


        
if __name__ == "__main__":
    file_name = "06/Rect.asm"
    out_name = file_name.replace(".asm", ".hack")
    assembler = HackAssembler(file_name)
    assembler.first_pass()
    assembler.second_pass(out_name)
    print(f"finish translating from {file_name} to {out_name}")



        






