
class Piece:
    """
    Piece clips the sprite into pieces to display on the board
    """
    def __init__(self,pieceinfo,chess_coord,square_width, square_height):
        # pieceinfo is a string such as 'Qb'. The Q represents Queen and b
        # shows the fact that it is black:
        piece = pieceinfo[0]
        color = pieceinfo[1]
        # Get the information about where the image for this piece is stored
        # on the overall sprite image with all the pieces. Note that
        # square_width and square_height represent the size of a square on the
        # chess board.
        if piece=='K':
            index = 0
        elif piece=='Q':
            index = 1
        elif piece=='B':
            index = 2
        elif piece == 'N':
            index = 3
        elif piece == 'R':
            index = 4
        elif piece == 'P':
            index = 5
        left_x =square_width*index
        if color == 'w':
            left_y = 0
        else:
            left_y = square_height
        
        self.pieceinfo = pieceinfo
        # subsection defines the part of the sprite image that represents our
        # piece
        self.subsection = (left_x,left_y,square_width,square_height)
        # There are two ways that the position of a piece is defined on the
        # board.
        # The default one used is the chess_coord, which stores something
        # like (3,2). It represents the chess coordinate where our piece image should
        # be blitted. On the other hand, is pos does not hold the default value
        # of (-1,-1), it will hold pixel coordinates such as (420,360) that represents
        # the location in the window that the piece should be blitted on. This is
        # useful for example if our piece is transitioning from a square to another:
        self.chess_coord = chess_coord
        self.pos = (-1,-1)

    def getInfo(self):
        return [self.chess_coord, self.subsection,self.pos]
    def setpos(self,pos):
        self.pos = pos
    def getpos(self):
        return self.pos
    def setcoord(self,coord):
        self.chess_coord = coord