#Initialize the board:

class Board:
    def __init__(self):
        self.create_board()
    
    def create_board(self):
        self.chess=[[0]*8 for i in range(8)]
        list_w=['Rw','Nw','Bw','Qw','Kw','Bw','Nw','Rw']
        list_b=['Rb','Nb','Bb','Qb','Kb','Bb','Nb','Rb']
        for i in range(2):
            for j in range (8):
                if i==0:
                    self.chess[i][j]=list_b[j]
                else:
                    self.chess[i][j]='Pb'
        for i in range(6,8):
            for j in range (8):
                if i==7:
                    self.chess[i][j]=list_w[j]
                else:
                    self.chess[i][j]='Pw'
    def getChess(self):
        return self.chess