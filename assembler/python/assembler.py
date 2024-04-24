# Steps for the assembler:
#   Read and parse the input file
#   Remove comments
#   Read the list of instructions
#   Generate the metadata table
#   Check for syntax errors and length errors
#   Replace variables and macros with their values
#   Generate the binary code for the instructions
#   Write the binary code to a file using LogisimMemoryFile

# add the path to the pythonlib folder
import sys
import os
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))) # add the path to the pythonlib folder

import re
from pythonlib.data import Instruction, REGEX_COMM, Macro, Registers, Memory
from pythonlib.logisim import LogisimMemoryFile

INSTRUCTIONS_LIST_FILE = 'data/instructions.txt'
MACROS_FILE = 'data/macros.txt'

ADDRESSES_SIZE = 16
PC_SIZE = 10

global LINE_NUMBER, LINE_TEXT, VERBOSE, FORCE
FORCE = False
VERBOSE = False
LINE_NUMBER = 0
LINE_TEXT = ""

class AssemblerError(Exception):
    def __init__(self, line_number, line_text, message):
        self.line_number = line_number
        self.line_text = line_text
        self.message = message
        super().__init__(f"Error at line {line_number}: {message}") 

class SyntaxError(AssemblerError):
    def __init__(self, message):
        super().__init__(LINE_NUMBER, LINE_TEXT, f"Syntax error: {message}")

class LengthError(AssemblerError):
    def __init__(self, message):
        super().__init__(LINE_NUMBER, LINE_TEXT, f"Length error: {message}")

class MacroError(AssemblerError):
    def __init__(self, message):
        super().__init__(LINE_NUMBER, LINE_TEXT, f"Macro error: {message}")

class VariableError(AssemblerError):
    def __init__(self, message):
        super().__init__(LINE_NUMBER, LINE_TEXT, f"Variable error: {message}")

class RegisterError(AssemblerError):
    def __init__(self, message):
        super().__init__(LINE_NUMBER, LINE_TEXT, f"Register error: {message}")

class LabelError(AssemblerError):
    def __init__(self, message):
        super().__init__(LINE_NUMBER, LINE_TEXT, f"Label error: {message}")

class Assembler:
    def __init__(self, input_filename, output_filename:str='output.lgsim'):
        self.instructions_dict = {i.mnemonic: i for i in Instruction.from_file(INSTRUCTIONS_LIST_FILE)}
        self.macro_dict = Macro.into_dict(Macro.from_file(MACROS_FILE))
        self.registers = Registers().registers
        
        with open(input_filename, 'r') as f:
            self.input_file = f.readlines()
        self.output_file = LogisimMemoryFile(10, 16)
        self.output_filename = output_filename
        
        self.memory = Memory(2**ADDRESSES_SIZE, 0)
        
        self.variables:dict = {}
        self.replacements = {}
        self.labels = {}
        self.binary_code_size = 0
        self.binary_code = []
        
    def debug_log(self, message:str) -> None:
        with open('log.txt', 'a') as f:
            f.write(message + '\n')
                
    def into_number(self,string:str) -> int:
        if isinstance(string, int):
            return string
        elif not isinstance(string, str):
            raise SyntaxError(f"Invalid number {string}")
        try:
            if string.startswith('0x'):
                return int(string, 16)
            elif string.startswith('0b'):
                return int(string, 2)
            return int(string)
        except ValueError as e:
            raise SyntaxError(f"Invalid number {string}") from e
        
    def remove_comments(self, line:str) -> str:
        return re.sub(REGEX_COMM, "", line)
        
    def new_file(filename:str, force=False) -> None:
        if not force and os.path.exists(filename):
            raise FileExistsError(f"File {filename} already exists, use '-f' to overwrite it")
        
        with open('data/example.arich') as f:
            content = f.read()
        with open(f"{filename}", 'w') as f:
            f.write(f"// {filename.split('/')[-1]}\n" + content)
        exit(0)
        
    def parse_macro(self, line:str):
        tokens = line.split()
        tokens[0] = tokens[0][1:]
        if tokens[0] in self.macro_dict:
            macro = self.macro_dict[tokens[0]]
            if len(tokens)-1 < macro.nb_operands - macro.optional_operands:
                raise MacroError(f"Too few operands for macro {macro.keyword}")
            if len(tokens)-1 > macro.nb_operands:
                raise MacroError(f"Too many operands for macro {macro.keyword}")
        else:
            raise MacroError(f"Invalid macro {tokens[0]}")
        
        match macro.keyword:
            case "stack":
                self.binary_code += [0x101, self.into_number(tokens[1]), 0x12] # put the given value as immediate to the base pointer
                self.memory.stack_base_address = self.into_number(tokens[1])
                
            case "define":
                if tokens[1][0].isdigit():
                    raise MacroError(f"Variable/replacement name {tokens[1]} cannot start with a digit")
                if tokens[1] in self.replacements:
                    raise MacroError(f"Replacement macro {tokens[1]} already defined")
                else:
                    self.replacements[tokens[1]] = tokens[2]
                
            case "let":
                if tokens[1][0].isdigit():
                    raise MacroError(f"Variable/replacement name {tokens[1]} cannot start with a digit")
                if tokens[1] in self.variables:
                    raise MacroError(f"Variable {tokens[1]} already defined")
                address = tokens[2] if tokens.__len__() == 3 else None
                
                if re.match(r'\[[0-9]+\]', tokens[1][-3:]): # if trying to define an array
                    if not tokens[1][-2].isdigit():
                        raise MacroError(f"Invalid array size {tokens[1][-2]}")
                    size = int(tokens[1][-2])
                    if size == 0:
                        raise MacroError("Array size cannot be 0")
                    start_address = self.memory.assign_address()
                    addresses = self.memory.assign_addresses_table(size, start_address)
                    for index, address in enumerate(addresses):
                        self.variables[f"{tokens[1][:-3]}[{index}]"] = address
                else:
                    self.variables[tokens[1]] = self.memory.assign_address(self.into_number(address) if address is not None else None)
                
            case "deref":
                if tokens[1][0].isdigit():
                    raise MacroError(f"Variable/replacement name {tokens[1]} cannot start with a digit")
                if tokens[1][-2:] == '[]':
                    if f"{tokens[1][:-2]}[0]" not in self.variables:
                        raise VariableError(f"Variable {tokens[1]} is not defined")
                elif tokens[1] not in self.variables:
                    raise MacroError(f"Variable {tokens[1]} is not defined")
                
                if tokens[1][-2:] == '[]':
                    i=0
                    while f"{tokens[1][:-2]}[{i}]" in self.variables:
                        self.memory.used_addresses.remove(self.variables[f"{tokens[1]}[{i}]"])
                        i += 1
                else:
                    self.memory.used_addresses.remove(self.variables[tokens[1]])
                    
            case "letreg":
                if tokens[1][0].isdigit():
                    raise MacroError(f"Register name {tokens[1]} cannot start with a digit")
                if tokens[1] in self.registers:
                    raise MacroError(f"Register {tokens[1]} already defined")
                self.registers[tokens[1]] = self.into_number(tokens[2])
                
                
    def parse_label(self, line:str, debug=False) -> None:
        if line.split().__len__() != 1:
            raise LabelError(f"Invalid label {line} (label don't contain spaces)")
        if line in self.labels:
            raise LabelError(f"Label {line} already defined")
        self.labels[line[1:]] = self.binary_code_size
        if VERBOSE:
            print(f"Label {line} defined at 0x{self.binary_code_size:03X}")
        if debug:
            self.debug_log(f"Label {line} defined at 0x{self.binary_code_size:03X}")
        
    def pre_process_length(self,debug=False) -> None:
        for line in self.input_file:
            line = self.remove_comments(line).strip()
            if line.isspace() or line == '':
                continue
            if line.startswith('#'):
                continue
            if line.startswith(':'): 
                self.parse_label(line, debug)
                continue
            self.binary_code_size += line.split().__len__()
        
        
    def parse_line(self, line:str, debug=False) -> None:
        line = self.remove_comments(line).strip()
        if line.isspace() or line == '':
            return
        if line.startswith('#'):
            return self.parse_macro(line)
        if line.startswith(':'):
            return
        
        tokens = line.split()
        if tokens[0] not in self.instructions_dict:
            raise SyntaxError(f"Invalid instruction {tokens[0]}")
        instruction = self.instructions_dict[tokens[0]]
        if len(tokens)-1 < instruction.nb_operands:
            raise SyntaxError(f"Too few operands for instruction {instruction.mnemonic}")
        if len(tokens)-1 > instruction.nb_operands:
            raise SyntaxError(f"Too many operands for instruction {instruction.mnemonic}")
        
        opcode = instruction.opcode
        operands = []
        
        for key,value in self.replacements.items(): # 'define' macro replacements
            for index, operand in enumerate(tokens[1:]):
                if operand == key:
                    tokens[index+1] = value
        
        for index, operand in enumerate(tokens[1:]): # replace registers, variables and labels
            match operand[0]:
                case '%':
                    if operand[1:] not in self.registers:
                        raise RegisterError(f"Register {operand[1:]} does not exist")
                    operand = self.registers[operand[1:]]
 
                case '&':
                    if index+1 == instruction.output_operand: #output_operand = 0 -> no output operand, 1 -> first operand etc...
                        raise SyntaxError("The output operand cannot be passed as immediate value")
                    if operand[1:] not in self.variables:
                        raise VariableError(f"Variable {operand[1:]} is not (yet) defined")
                    operand = self.variables[operand[1:]]
                    opcode = opcode | 1 << (8+index) # set the immediate bit (8th for the first operand, 9th for the second)
                    
                case '$':
                    if index+1 == instruction.output_operand:
                        raise SyntaxError("The output operand cannot be passed as immediate value")
                    operand = self.into_number(operand[1:])
                    opcode = opcode | 1 << (8+index) # set the immediate bit (8th for the first operand, 9th for the second)
                    
                case ':':
                    if operand[1:] not in self.labels:
                        raise LabelError(f"Label {operand[1:]} is not (yet) defined")
                    operand = self.labels[operand[1:]]
                case _:
                    operand = self.into_number(operand)
            operands.append(operand)
            
        if VERBOSE:
            print(f"{f'{self.binary_code.__len__():03X}'}:\t{line} {(40-line.__len__())*' '}-> {f'{opcode:04X}' + ' ' + ' '.join([f'{o:04X}' for o in operands])}")
        if debug:
            self.debug_log(f"{f'{self.binary_code.__len__():03X}'}:\t{line} {(40-line.__len__())*' '}-> {f'{opcode:04X}' + ' ' + ' '.join([f'{o:04X}' for o in operands])}")
        self.binary_code += [opcode, *operands]
        
    def assemble(self, debug=False) -> None:
        self.pre_process_length(debug)
        if debug:
            self.debug_log("//")
        
        for line in self.input_file:
            self.parse_line(line, debug)
    
        if VERBOSE:
            print('\nFINAL BINARY CODE: '+' '.join([f'{code:04X}' for code in self.binary_code]))
        if debug:
            self.debug_log('//\nFINAL BINARY CODE: '+' '.join([f'{code:04X}' for code in self.binary_code])+'\n//'+'-'*30+'End of log file'+'-'*30+'\n')
        
        self.output_file.insert_list(self.binary_code).to_file(self.output_filename, force=FORCE)
        
                
        
if __name__ == '__main__':
    class Args:
        pass
    parser = argparse.ArgumentParser(description='Assembler for the ARICH-16 processor')
    parser.add_argument('filename', type=str, help='Input file for the assembler')
    parser.add_argument('-o', '--output', type=str, help='Output file for the assembler', default='output.lgsm')
    parser.add_argument('-n', '--new', help='Creates a new .arich file with the default instructions', action='store_true')
    parser.add_argument('-f', '--force', help='Overwrites the output file if it already exists', action='store_true')
    parser.add_argument('-l', '--list', type=str, help='List of instructions for the assembler', default='instructions_list')
    parser.add_argument('-v', '--verbose', help="Prints the binary code generated", action='store_true')
    parser.add_argument('-d', '--debug', help='Creates a debug file with helpful information', action='store_true')
    args = parser.parse_args(namespace=Args())
    
    VERBOSE = args.verbose
    FORCE = args.force
    
    if args.new:
        Assembler.new_file(args.filename, args.force)
    
    Assembler(args.filename, args.output).assemble(args.debug)