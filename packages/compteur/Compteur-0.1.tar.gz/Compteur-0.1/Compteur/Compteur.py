from pathlib import Path
import string

class Compteur:
    def __init__(self, name: str, limit: int=5):
        if True in [ not x in string.ascii_letters for x in name]: raise ValueError("Only ascii characters are allowed for name")
        
        self.file = Path.home() / f".compteur_{name}"
        self.limit = limit
        
        try:
            self.__read()
        except:
            self.cpt = 0
            
    def __write(self):
        with open(self.file, 'w') as f:
            f.write(str(self.cpt))
            
    def __read(self):
        with open(self.file, "r") as f:
            self.cpt = int(f.read())
            
    def reset(self):
        try:
            Path.unlink(self.file)
        except:
            pass
            
    def inc(self):
        self.cpt += 1
        self.__write()
        
    def isLimit(self):
        return self.cpt >= self.limit