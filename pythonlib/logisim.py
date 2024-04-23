import os

class LogisimMemoryFile:
    def __init__(self, adress_size: int, data_size: int):
        self.adress_size = adress_size
        self.data_size = data_size
        self.content = [0] * 2**adress_size
        
    def insert(self, adress:int, data:int) -> 'LogisimMemoryFile':
        if data > 2**self.data_size: raise ValueError("Data is too big for the memory")
        if adress > 2**self.adress_size: raise ValueError("Adress is too big for the memory")
        self.content[adress] = data
        return self
        
    def insert_list(self, data: list, starting_adress:int=0) -> 'LogisimMemoryFile':
        for i, d in enumerate(data):
            self.insert(starting_adress+i, d)
        return self
            
    def insert_dict(self, data: dict) -> 'LogisimMemoryFile':
        for i, d in data.items():
            self.insert(i, d)
        return self
    
    def get(self, adress:int):
        return self.content[adress]
        
    def to_file(self, filename:str='my_memory', force=False) -> None:
        if not force and os.path.exists(filename):
            raise FileExistsError("File already exists")
        file_str = "v3.0 hex words addressed\n"
        adress = 0
        while adress < 2**self.adress_size:
            line_adress = f"{format(adress, 'x').zfill(self.adress_size//4)}: "
            line_data = [f"{format(self.content[adress+i], 'x').zfill(self.data_size//4)}" for i in range(16)]
            file_str += line_adress + " ".join(line_data) + "\n"
            adress += 16
            
        with open(filename, 'w') as f: f.write(file_str)
            
if __name__ == '__main__':
    pass