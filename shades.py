
class Shades:
    """
    It is used to shade the board
    """
    def __init__(self,image,coord):
        self.image = image
        self.pos = coord
    def getInfo(self):
        return [self.image,self.pos]