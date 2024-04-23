# un fichier pour générer les tables de recherche des métadonnées des instructions

import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # add the path to the pythonlib folder

from pythonlib.data import Instruction
from pythonlib.logisim import LogisimMemoryFile
    
if __name__ == "__main__":
    DEBUG = "-d" in sys.argv

    if "-f" in sys.argv:
        sys.argv = sys.argv[1:]
        try: 
            filename = sys.argv[sys.argv.index("-f")+1]
        except IndexError: 
            raise RuntimeError("No filename provided")
        
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"File '{filename}' not found")
    else:
        filename = "data/instructions.txt"
        
    if "-o" in sys.argv:
        sys.argv = sys.argv[1:]
        try: 
            output_filename = sys.argv[sys.argv.index("-o")+1]
        except IndexError: 
            raise RuntimeError("No output filename provided")
    else:
        output_filename = "instructions_metadata_table"
    
    instructions = Instruction.from_file(filename)
    data = Instruction.generate_metadata_table(instructions)
    if DEBUG: print("data"+[f"{hex(i)}: {format(data[i], 'b').zfill(4)}" for i in data].__str__())
    file = LogisimMemoryFile(8, 4).insert_dict(data).to_file(output_filename)
    