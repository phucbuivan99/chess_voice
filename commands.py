
class Commands:
    """
    this class works with variables that hold the information about game state.
    it contains chess processing functions
    """

    def isOccupied(self,board,x,y):
        # isOccupied(board,x,y) - Returns true if a given coordinate on the board is not empty, and
        # false otherwise.
        if board[int(y)][int(x)] == 0:
        # The square has nothing on it.
            return False
        return True

    def isOccupiedby(self,board,x,y,color):
        # isOccupiedby(board,x,y,color) - Same as above, but only returns true if the square
        # specified by the coordinates is of the specific color inputted.
        if board[y][x] == 0:
            # the square has nothing on it.
            return False
        if board[y][x][1] == color[0]:
            # The square has a piece of the color inputted.
            return True
        # The square has a piece of the opposite color.
        return False

    def filterbyColor(self,board,listofTuples,color):
        # filterbyColor(board,listofTuples,color) - This function takes the board state, a list
        # of coordinates, and a color as input. It will return the same list, but without
        # coordinates that are out of bounds of the board and also without those occupied by the
        # pieces of the particular color passed to this function as an argument. In other words,
        # if 'white' is passed in, it will not return any white occupied square.
        filtered_list = []
        # Go through each coordinate:
        for pos in listofTuples:
            x = pos[0]
            y = pos[1]
            if x>=0 and x<=7 and y>=0 and y<=7 and not self.isOccupiedby(board,x,y,color):
                # coordinates are on-board and no same-color piece is on the square.
                filtered_list.append(pos)
        return filtered_list

    def lookfor(self,board,piece):
        # lookfor(board,piece) - This functions takes the 2D array that represents a board and finds
        # the indices of all the locations that is occupied by the specified piece. The list of
        # indices is returned.
        listofLocations = []
        for row in range(8):
            for col in range(8):
                if board[row][col] == piece:
                    x = col
                    y = row
                    listofLocations.append((x,y))
        return listofLocations

    def isAttackedby(self,position,target_x,target_y,color):
        # isAttackedby(position,target_x,target_y,color) - This function checks if the square specified
        # by (target_x,target_y) coordinates is being attacked by any of a specific colored set of pieces.

        # Get board
        board = position.getboard()
        # Get b from black or w from white
        color = color[0]
        # Get all the squares that are attacked by the particular side:
        listofAttackedSquares = []
        for x in range(8):
            for y in range(8):
                if board[y][x]!=0 and board[y][x][1]==color:
                    listofAttackedSquares.extend(
                        self.findPossibleSquares(position,x,y,True)) #The true argument
                    # prevents infinite recursion.
        # Check if the target square falls under the range of attack by the specified
        # side, and return it:
        return (target_x,target_y) in listofAttackedSquares             

    def findPossibleSquares(self,position,x,y,AttackSearch=False):
        # findPossibleSquares(position,x,y,AttackSearch=False) - This function takes as its input the
        # current state of the chessboard, and a particular x and y coordinate. It will return for the
        # piece on that board a list of possible coordinates it could move to, including captures and
        # excluding illegal moves (eg moves that leave a king under check). AtttackSearch is an
        # argument used to ensure infinite recursions do not occur.

        # Get individual component data from the position object:
        board = position.getboard()
        player = position.getplayer()
        castling_rights = position.getCastleRights()
        EnP_Target = position.getEnP()

        # In case something goes wrong:
        piece = board[y][x][0] #Pawn, rook, etc.
        color = board[y][x][1] #w or b.

        # Have the complimentary color stored for convenience:
        enemy_color = self.opp(color)
        listofTuples = [] #Holds list of attacked squares.

        if piece == 'P': #The piece is a pawn.
            if color=='w': #The piece is white
                if not self.isOccupied(board,x,y-1) and not AttackSearch:
                    #The piece immediately above is not occupied, append it.
                    listofTuples.append((x,y-1))
                    
                    if y == 6 and not self.isOccupied(board,x,y-2):
                        #If pawn is at its initial position, it can move two squares.
                        listofTuples.append((x,y-2))
                
                if x!=0 and self.isOccupiedby(board,x-1,y-1,'black'):
                    #The piece diagonally up and left of this pawn is a black piece.
                    #Also, this is not an 'a' file pawn (left edge pawn)
                    listofTuples.append((x-1,y-1))
                if x!=7 and self.isOccupiedby(board,x+1,y-1,'black'):
                    #The piece diagonally up and right of this pawn is a black one.
                    #Also, this is not an 'h' file pawn.
                    listofTuples.append((x+1,y-1))
                if EnP_Target!=-1: #There is a possible en pasant target:
                    if EnP_Target == (x-1,y-1) or EnP_Target == (x+1,y-1):
                        #We're at the correct location to potentially perform en
                        #passant:
                        listofTuples.append(EnP_Target)
                
            elif color=='b': #The piece is black, same as above but opposite side.
                if not self.isOccupied(board,x,y+1) and not AttackSearch:
                    listofTuples.append((x,y+1))
                    if y == 1 and not self.isOccupied(board,x,y+2):
                        listofTuples.append((x,y+2))
                if x!=0 and self.isOccupiedby(board,x-1,y+1,'white'):
                    listofTuples.append((x-1,y+1))
                if x!=7 and self.isOccupiedby(board,x+1,y+1,'white'):
                    listofTuples.append((x+1,y+1))
                if EnP_Target == (x-1,y+1) or EnP_Target == (x+1,y+1):
                    listofTuples.append(EnP_Target)

        elif piece == 'R': #The piece is a rook.
            #Get all the horizontal squares:
            for i in [-1,1]:
                #i is -1 then +1. This allows for searching right and left.
                kx = x #This variable stores the x coordinate being looked at.
                while True: #loop till break.
                    kx = kx + i #Searching left or right
                    if kx<=7 and kx>=0: #Making sure we're still in board.
                        
                        if not self.isOccupied(board,kx,y):
                            #The square being looked at it empty. Our rook can move
                            #here.
                            listofTuples.append((kx,y))
                        else:
                            #The sqaure being looked at is occupied. If an enemy
                            #piece is occupying it, it can be captured so its a valid
                            #move. 
                            if self.isOccupiedby(board,kx,y,enemy_color):
                                listofTuples.append((kx,y))
                            #Regardless of the occupying piece color, the rook cannot
                            #jump over. No point continuing search beyond in this
                            #direction:
                            break
                            
                    else: #We have exceeded the limits of the board
                        break
            #Now using the same method, get the vertical squares:
            for i in [-1,1]:
                ky = y
                while True:
                    ky = ky + i 
                    if ky<=7 and ky>=0: 
                        if not self.isOccupied(board,x,ky):
                            listofTuples.append((x,ky))
                        else:
                            if self.isOccupiedby(board,x,ky,enemy_color):
                                listofTuples.append((x,ky))
                            break
                    else:
                        break
            
        elif piece == 'N': #The piece is a knight.
            #The knight can jump across a board. It can jump either two or one
            #squares in the x or y direction, but must jump the complimentary amount
            #in the other. In other words, if it jumps 2 sqaures in the x direction,
            #it must jump one square in the y direction and vice versa.
            for dx in [-2,-1,1,2]:
                if abs(dx)==1:
                    sy = 2
                else:
                    sy = 1
                for dy in [-sy,+sy]:
                    listofTuples.append((x+dx,y+dy))
            #Filter the list of tuples so that only valid squares exist.
            listofTuples = self.filterbyColor(board,listofTuples,color)
        elif piece == 'B': # A bishop.
            #A bishop moves diagonally. This means a change in x is accompanied by a
            #change in y-coordiante when the piece moves. The changes are exactly the
            #same in magnitude and direction.
            for dx in [-1,1]: #Allow two directions in x.
                for dy in [-1,1]: #Similarly, up and down for y.
                    kx = x #These varibales store the coordinates of the square being
                           #observed.
                    ky = y
                    while True: #loop till broken.
                        kx = kx + dx #change x
                        ky = ky + dy #change y
                        if kx<=7 and kx>=0 and ky<=7 and ky>=0:
                            #square is on the board
                            if not self.isOccupied(board,kx,ky):
                                #The square is empty, so our bishop can go there.
                                listofTuples.append((kx,ky))
                            else:
                                #The square is not empty. If it has a piece of the
                                #enemy,our bishop can capture it:
                                if self.isOccupiedby(board,kx,ky,enemy_color):
                                    listofTuples.append((kx,ky))
                                #Bishops cannot jump over other pieces so terminate
                                #the search here:
                                break    
                        else:
                            #Square is not on board. Stop looking for more in this
                            #direction:
                            break
        
        elif piece == 'Q': #A queen
            #A queen's possible targets are the union of all targets that a rook and
            #a bishop could have made from the same location
            #Temporarily pretend there is a rook on the spot:
            board[y][x] = 'R' + color
            list_rook = self.findPossibleSquares(position,x,y,True)
            #Temporarily pretend there is a bishop:
            board[y][x] = 'B' + color
            list_bishop = self.findPossibleSquares(position,x,y,True)
            #Merge the lists:
            listofTuples = list_rook + list_bishop
            #Change the piece back to a queen:
            board[y][x] = 'Q' + color
        elif piece == 'K': # A king!
            #A king can make one step in any direction:
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    listofTuples.append((x+dx,y+dy))
            #Make sure the targets aren't our own piece or off-board:
            listofTuples = self.filterbyColor(board,listofTuples,color)
            if not AttackSearch:
                #Kings can potentially castle:
                right = castling_rights[player]
                #Kingside
                if (right[0] and #has right to castle
                board[y][7]!=0 and #The rook square is not empty
                board[y][7][0]=='R' and #There is a rook at the appropriate place
                not self.isOccupied(board,x+1,y) and #The square on its right is empty
                not self.isOccupied(board,x+2,y) and #The second square beyond is also empty
                not self.isAttackedby(position,x,y,enemy_color) and #The king isn't under atack
                not self.isAttackedby(position,x+1,y,enemy_color) and #Or the path through which
                not self.isAttackedby(position,x+2,y,enemy_color)):#it will move
                    listofTuples.append((x+2,y))
                #Queenside
                if (right[1] and #has right to castle
                board[y][0]!=0 and #The rook square is not empty
                board[y][0][0]=='R' and #The rook square is not empty
                not self.isOccupied(board,x-1,y)and #The square on its left is empty
                not self.isOccupied(board,x-2,y)and #The second square beyond is also empty
                not self.isOccupied(board,x-3,y) and #And the one beyond.
                not self.isAttackedby(position,x,y,enemy_color) and #The king isn't under atack
                not self.isAttackedby(position,x-1,y,enemy_color) and #Or the path through which
                not self.isAttackedby(position,x-2,y,enemy_color)):#it will move
                    listofTuples.append((x-2,y)) #Let castling be an option.

        # Make sure the king is not under attack as a result of this move:
        if not AttackSearch:
            new_list = []
            for tupleq in listofTuples:
                x2 = int(tupleq[0])
                y2 = int(tupleq[1])
                temp_pos = position.clone()
                self.makemove(temp_pos,x,y,x2,y2)
                if not self.isCheck(temp_pos,color):
                    new_list.append(tupleq)
            listofTuples = new_list
        return listofTuples

    def makemove(self,position,x,y,x2,y2):
        # makemove(position,x,y,x2,y2) - This function makes a move on the board. The position object
        # gets updated here with new information. (x,y) are coordinates of the piece to be moved, and
        # (x2,y2) are coordinates of the destination. (x2,y2) being correct destination (ie the move
        # a valid one) is not checked for and is assumed to be the case.

        # Get data from the position:
        x = int(x)
        y = int(y)
        x2 = int(x2)
        y2 = int(y2)
        board = position.getboard()
        piece = board[y][x]
        if piece==0:
            return
        piece=piece[0]
        color = board[y][x][1]
        #Get the individual game components:
        player = position.getplayer()
        castling_rights = position.getCastleRights()
        EnP_Target = position.getEnP()
        half_move_clock = position.getHMC()
        #Update the half move clock:
        if self.isOccupied(board,x2,y2) or piece=='P':
            #Either a capture was made or a pawn has moved:
            half_move_clock = 0
        else:
            #An irreversible move was played:
            half_move_clock += 1

        #Make the move:
        board[y2][x2] = board[y][x]
        board[y][x] = 0
        
        #Special piece requirements:
        #King:
        if piece == 'K':
            #Ensure that since a King is moved, the castling
            #rights are lost:
            castling_rights[player] = [False,False]
            #If castling occured, place the rook at the appropriate location:
            if abs(x2-x) == 2:
                if color=='w':
                    l = 7
                else:
                    l = 0
                
                if x2>x:
                        board[l][5] = 'R'+color
                        board[l][7] = 0
                else:
                        board[l][3] = 'R'+color
                        board[l][0] = 0
        #Rook:
        if piece=='R':
            #The rook moved. Castling right for this rook must be removed.
            if x==0 and y==0:
                #Black queenside
                castling_rights[1][1] = False
            elif x==7 and y==0:
                #Black kingside
                castling_rights[1][0] = False
            elif x==0 and y==7:
                #White queenside
                castling_rights[0][1] = False
            elif x==7 and y==7:
                #White kingside
                castling_rights[0][0] = False
        #Pawn:
        if piece == 'P':
            #If an en passant kill was made, the target enemy must die:
            if EnP_Target == (x2,y2):
                if color=='w':
                    board[y2+1][x2] = 0
                else:
                    board[y2-1][x2] = 0
            #If a pawn moved two steps, there is a potential en passant
            #target. Otherise, there isn't. Update the variable:
            if abs(y2-y)==2:
                EnP_Target = (x,(y+y2)/2)
            else:
                EnP_Target = -1
            #If a pawn moves towards the end of the board, it needs to 
            #be promoted. Note that in this game a pawn is being promoted
            #to a queen regardless of user choice.
            if y2==0:
                board[y2][x2] = 'Qw'
            elif y2 == 7:
                board[y2][x2] = 'Qb'
        else:
            #If a pawn did not move, the en passsant target is gone as well,
            #since a turn has passed:
            EnP_Target = -1

        #Since a move has been made, the other player
        #should be the 'side to move'
        player = 1 - player
        #Update the position data:       
        position.setplayer(player)
        position.setCastleRights(castling_rights)
        position.setEnP(EnP_Target)
        position.setHMC(half_move_clock)
    def opp(self,color):
        # opp(color) - Returns the complimentary color to the one passed. So inputting 'black' returns
        # 'w', for example.
        color = color[0]
        if color == 'w':
            oppcolor = 'b'
        else:
            oppcolor = 'w'
        return oppcolor
    def isCheck(self,position,color):
        # isCheck(position,color) - This function takes a position as its input and checks if the
        # King of the specified color is under attack by the enemy. Returns true if that is the case,
        # and false otherwise.
        #Get data:
        board = position.getboard()
        color = color[0]
        enemy = self.opp(color)
        piece = 'K' + color
        #Get the coordinates of the king:
        x,y = self.lookfor(board,piece)[0]
        #Check if the position of the king is attacked by
        #the enemy and return the result:
        return self.isAttackedby(position,x,y,enemy)
    def isCheckmate(self,position,color=-1):
        # isCheckmate(position,color=-1) - This function tells you if a position is a checkmate.
        # Color is an optional argument that may be passed to specifically check for mate against a
        # specific color.
        if color==-1:
            return self.isCheckmate(position,'white') or self.isCheckmate(position,'b')
        color = color[0]
        if self.isCheck(position,color) and self.allMoves(position,color)==[]:
            #The king casis under attack, and there are no possible moves for this side to make:
                return True
        #Either the king is not under attack or there are possible moves to be played:
        return False
    def isStalemate(self,position):
        # isStalemate(position) - This function checks if a particular position is a stalemate.
        # If it is, it returns true, otherwise it returns false.
        #Get player to move:
        player = position.getplayer()
        #Get color:
        if player==0:
            color = 'w'
        else:
            color = 'b'
        if not self.isCheck(position,color) and self.allMoves(position,color)==[]:
            #The player to move is not under check yet cannot make a move.
            #It is a stalemate.
            return True
        return False
    def getallpieces(self,position,color):
        # getallpieces(position,color) - This function returns a list of positions of all the pieces on
        # the board of a particular color.

        #Get the board:
        board = position.getboard()
        listofpos = []
        for j in range(8):
            for i in range(8):
                if self.isOccupiedby(board,i,j,color):
                    listofpos.append((i,j))
        return listofpos
    def allMoves(self,position, color):
        # allMoves(position, color) - This function takes as its argument a position and a color/colorsign
        # that represents a side. It generates a list of all possible moves for that side and returns it.
        #Find if it is white to play or black:
        if color==1:
            color = 'white'
        elif color ==-1:
            color = 'black'
        color = color[0]
        #Get all pieces controlled by this side:
        listofpieces = self.getallpieces(position,color)
        moves = []
        #Loop through each piece:
        for pos in listofpieces:
            #For each piece, find all the targets it can attack:
            targets = self.findPossibleSquares(position,pos[0],pos[1])
            for target in targets:
                #Save them all as possible moves:
                 moves.append([pos,target])
        return moves
    def pos2key(self,position):
        # pos2key(position) - This function takes a position as input argument. For this particular
        # position, it will generate a unique key that can be used in a dictionary by making it hashable.
        #Get board:
        board = position.getboard()
        #Convert the board into a tuple so it is hashable:
        boardTuple = []
        for row in board:
            boardTuple.append(tuple(row))
        boardTuple = tuple(boardTuple)
        #Get castling rights:
        rights = position.getCastleRights()
        #Convert to a tuple:
        tuplerights = (tuple(rights[0]),tuple(rights[1]))
        #Generate the key, which is a tuple that also takes into account the side to play:
        key = (boardTuple,position.getplayer(),
               tuplerights)
        #Return the key:
        return key