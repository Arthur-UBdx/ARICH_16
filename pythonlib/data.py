import re

REGEX_MACRO_LIST = r"([a-z]+),([0-9]+),([0-9]+);"
REGEX_COMM = r"//.*"
REGEX_INSTRUCTIONS_LIST = r"([A-Z]+),0x([0-9A-F][0-9A-F]),([0-9]),([0-9]);"

class Memory:
    def __init__(self, size:int, stack_base_address:int=0):
        self.stack_base_address = stack_base_address
        self.size = size
        self.used_addresses = set([])
        
    def assign_address(self, address=None) -> int:
        if address is None:
            address = self.stack_base_address+1
            while address in self.used_addresses:
                address += 1
            self.used_addresses.add(address)
            return address
        else:
            if address in self.used_addresses:
                raise ValueError(f"Address {address} already used, use #deref to free it")
            self.used_addresses.add(address)
            return address
        
    def _is_enough_space(self, side:int, start_address:int):
            for addr in range(start_address, start_address+side):
                if addr in self.used_addresses:
                    return False
            return True
        
    def assign_addresses_table(self, size:int, start_address:int=None) -> list:
        if start_address is None:
            start_address = self.stack_base_address+1
        while self._is_enough_space(size, start_address):
            start_address += 1
        for i in range(size):
            self.used_addresses.add(start_address+i)
        return [start_address+i for i in range(size)]

class Macro:
    def __init__(self, keyword:str, nb_operands:int, optional_operands:int):
        self.keyword = keyword
        self.nb_operands = int(nb_operands)
        self.optional_operands = int(optional_operands)
        
    def __str__(self) -> str:
        return f"{self.keyword}, {self.nb_operands}, {self.optional_operands}"
    
    def __repr__(self) -> str:
        return f"Macro({self.__str__()})"
    
    def from_string(string:str, debug=False) -> 'Macro':
        if debug:
            print(f"s: {string}")
        return Macro(*re.search(REGEX_MACRO_LIST, string).groups())
    
    def from_file(filename:str='data/macros.txt') -> list:
        with open(filename) as f:
            lines:list = f.readlines()
        lines = [x.strip() for x in lines if not re.match(REGEX_COMM, x)]
            
        return [Macro.from_string(x) for x in lines]
    
    def into_dict(macros:list) -> dict:
        return {m.keyword: m for m in macros}


class Instruction:
    def __init__(self, mnemonic:str, opcode:int, nb_operands:int, output_operand:int):
        self.mnemonic = mnemonic
        self.opcode = int(opcode, 16)
        self.nb_operands = int(nb_operands)
        self.output_operand = int(output_operand)
        
    def __str__(self) -> str:
        return f"{self.mnemonic}, 0x{hex(self.opcode)}, {self.nb_operands}, {self.output_operand}"
    
    def __repr__(self) -> str:
        return f"Instruction({self.__str__()})"
    
    def from_string(string:str, debug=False) -> 'Instruction':
        if debug:
            print(f"s: {string}")
        #use REGEX_INSTRUCTIONS with the capture groups to get the values
        return Instruction(*re.search(REGEX_INSTRUCTIONS_LIST, string).groups())
    
    def from_file(filename:str="instructions_list") -> list:
        with open(filename) as f:
            instructions:list = f.readlines()
        
        instructions = [x.strip() for x in instructions]
        instructions = [re.sub(REGEX_COMM, "", x) for x in instructions if not re.match(REGEX_COMM, x)]
        instructions = [Instruction.from_string(x) for x in instructions]
        return instructions
    
    def generate_metadata_table(instructions:list) -> dict:
        table = {}
        for i in instructions:
            table[i.opcode] = i.nb_operands << 2 | i.output_operand
        return table
    
class Registers:
    def __init__(self, filename:str='data/registers.txt'):
        with open(filename) as f:
            file:list = f.readlines()
        file = [x.strip() for x in file if not re.match(REGEX_COMM, x)]
        self.registers = {x.split(',')[0]: int(x.split(',')[1][2:-1], 16) for x in file}
        

if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # add the path to the pythonlib folder