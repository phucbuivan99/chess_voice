from commands import Commands
import copy
class GamePosition:
    def __init__(self,board,player,castling_rights,EnP_Target,HMC,history = {}):

        # Making an object of Commands Class
        self.c=Commands()
        # A 2D array containing information about piece postitions. Check main function to see an example of such
        # a representation.
        self.board = board
        # Stores 0 or 1. If white to play, equals 0. If black to play, stores 1.
        self.player = player
        # A list that contains castling rights for white and black. Each castling right is a list that contains right
        # to castle kingside and queenside.
        # Stores the coordinates of a square that can be targeted by en passant capture.
        self.EnP = EnP_Target
        self.castling = castling_rights
        # Half move clock. Stores the number of irreversible moves made so far, in order to help
        # detect draw by 50 moves without any capture or pawn movement.
        self.HMC = HMC
        # A dictionary that stores as key a position (hashed) and the value of each of
        # these keys represents the number of times each of these positions was repeated in order for this
        # position to be reached.
        self.history = history
        
    def getboard(self):
        return self.board
    def setboard(self,board):
        self.board = board
    def getplayer(self):
        return self.player
    def setplayer(self,player):
        self.player = player
    def getCastleRights(self):
        return self.castling
    def setCastleRights(self,castling_rights):
        self.castling = castling_rights
    def getEnP(self):
        return self.EnP
    def setEnP(self, EnP_Target):
        self.EnP = EnP_Target
    def getHMC(self):
        return self.HMC
    def setHMC(self,HMC):
        self.HMC = HMC
    def checkRepition(self):
        # Returns True if any of of the values in the history dictionary is greater than 3.
        # This would mean a position had been repeated at least thrice in order to reach the
        # current position in this game.
        return any(value>=3 for value in self.history.values())
    def addtoHistory(self,position):
        # Generate a unique key out of the current position:
        key = self.c.pos2key(position)
        #Add it to the history dictionary.
        self.history[key] = self.history.get(key,0) + 1
    def gethistory(self):
        return self.history
    def clone(self):
        # This method returns another instance of the current object with exactly the same
        # parameters but independent of the current object.
        clone = GamePosition(copy.deepcopy(self.board),    #  Independent copy
                             self.player,
                             copy.deepcopy(self.castling), #  Independent copy
                             self.EnP,
                             self.HMC)
        return clone