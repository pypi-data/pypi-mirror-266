from pathlib import Path
import string

class Compteur:
    def __init__(self, name: str, limit: int=5):
        """Create a counter object

        Args:
            name (str): part of the counter file (.compeur_[name]) that will be created in the home directory
            limit (int, optional): used by isLimit function. Defaults to 5.

        Raises:
            ValueError: name variable must be ascii letters only
        """
        if any([ not x in string.ascii_letters for x in name]): raise ValueError("Only ascii characters are allowed for name")
        
        self.file = Path.home() / f".compteur_{name}"
        self.limit = limit
        
        try:
            self.__read()
        except:
            self.cpt = 0
            
    def __write(self):
        """Write counter to the file"""
        with open(self.file, 'w') as f:
            f.write(str(self.cpt))
            
    def __read(self):
        """Read counter from the file"""
        with open(self.file, "r") as f:
            self.cpt = int(f.read())
            
    def reset(self):
        """Reset counter (delete .compteur file)"""
        try:
            Path.unlink(self.file)
        except:
            pass
            
    def inc(self):
        """Add 1 to the counter"""
        self.cpt += 1
        self.__write()
        
    def isLimit(self):
        """Check if limit is reached

        Returns:
            bool: return True if counter is greater or equal to limit
        """
        return self.cpt >= self.limit