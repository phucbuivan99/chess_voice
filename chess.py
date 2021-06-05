
from gamePosition import *
from commands import *
from piece import *
from shades import *
from board import *
from pieceTable import *
import pygame 
from pygame.locals import *
import copy 
import pickle 
import random 
from collections import defaultdict 
from collections import Counter 
import threading 
import time
import speech_recognition as sr

play_sound=True

class AI:

    def __init__(self):
        self.c=Commands()
        
    def negamax( self,position,depth,alpha,beta,colorsign,bestMoveReturn,openings,searched,root=True):
        #First check if the position is already stored in the opening database dictionary:
        if root:
            #Generate key from current position:
            key = self.c.pos2key(position)
            if key in openings:
                #Return the best move to be played:
                bestMoveReturn[:] = random.choice(openings[key])
                return
        #Access global variable that will store scores of positions already evaluated:
        
        #If the depth is zero, we are at a leaf node (no more depth to be analysed):
        if depth==0:
            return colorsign*self.evaluate(position)
        #Generate all the moves that can be played:
        moves = self.c.allMoves(position, colorsign)
        #If there are no moves to be played, just evaluate the position and return it:
        if moves==[]:
            return colorsign*self.evaluate(position)
        #Initialize a best move for the root node:
        if root:
            bestMove = moves[0]
        #Initialize the best move's value:
        bestValue = -100000
        #Go through each move:
        for move in moves:
            #Make a clone of the current move and perform the move on it:
            newpos = position.clone()
            self.c.makemove(newpos,move[0][0],move[0][1],move[1][0],move[1][1])
            #Generate the key for the new resulting position:
            key = self.c.pos2key(newpos)
            #If this position was already searched before, retrieve its node value.
            #Otherwise, calculate its node value and store it in the dictionary:
            if key in searched:
                value = searched[key]
            else:
                value = -self.negamax(newpos,depth-1, -beta,-alpha,-colorsign,[],openings,searched,False)
                searched[key] = value
            #If this move is better than the best so far:
            if value>bestValue:
                #Store it
                bestValue = value
                #If we're at root node, store the move as the best move:
                if root:
                    bestMove = move
            #Update the lower bound for this node:
            alpha = max(alpha,value)
            if alpha>=beta:
                #If our lower bound is higher than the upper bound for this node, there
                #is no need to look at further moves:
                break
        #If this is the root node, return the best move:
        if root:
            searched = {}
            bestMoveReturn[:] = bestMove
            return
        #Otherwise, return the bestValue (i.e. value for this node.)
        return bestValue
    def evaluate(self,position):
        
        if self.c.isCheckmate(position,'white'):
            #Major advantage to black
            return -20000
        if self.c.isCheckmate(position,'black'):
            #Major advantage to white
            return 20000
        #Get the board:
        board = position.getboard()
        #Flatten the board to a 1D array for faster calculations:
        flatboard = [x for row in board for x in row]
        #Create a counter object to count number of each pieces:
        c = Counter(flatboard)
        Qw = c['Qw']
        Qb = c['Qb']
        Rw = c['Rw']
        Rb = c['Rb']
        Bw = c['Bw']
        Bb = c['Bb']
        Nw = c['Nw']
        Nb = c['Nb']
        Pw = c['Pw']
        Pb = c['Pb']
        #Note: The above choices to flatten the board and to use a library
        #to count pieces were attempts at making the AI more efficient.
        #Perhaps using a 1D board throughout the entire program is one way
        #to make the code more efficient.
        #Calculate amount of material on both sides and the number of moves
        #played so far in order to determine game phase:
        whiteMaterial = 9*Qw + 5*Rw + 3*Nw + 3*Bw + 1*Pw
        blackMaterial = 9*Qb + 5*Rb + 3*Nb + 3*Bb + 1*Pb
        numofmoves = len(position.gethistory())
        gamephase = 'opening'
        if numofmoves>40 or (whiteMaterial<14 and blackMaterial<14):
            gamephase = 'ending'
        #A note again: Determining game phase is again one the attempts
        #to make the AI smarter when analysing boards and has not been 
        #implemented to its full potential.
        #Calculate number of doubled, blocked, and isolated pawns for 
        #both sides:
        Dw = self.doubledPawns(board,'white')
        Db = self.doubledPawns(board,'black')
        Sw = self.blockedPawns(board,'white')
        Sb = self.blockedPawns(board,'black')
        Iw = self.isolatedPawns(board,'white')
        Ib = self.isolatedPawns(board,'black')
        #Evaluate position based on above data:
        evaluation1 = 900*(Qw - Qb) + 500*(Rw - Rb) +330*(Bw-Bb
                    )+320*(Nw - Nb) +100*(Pw - Pb) +-30*(Dw-Db + Sw-Sb + Iw- Ib
                    )
        #Evaluate position based on piece square tables:
        evaluation2 = self.pieceSquareTable(flatboard,gamephase)
        #Sum the evaluations:
        evaluation = evaluation1 + evaluation2
        #Return it:
        return evaluation
    def pieceSquareTable(self,flatboard,gamephase):
        #Initialize score:
        p=PieceTable()
        score = 0
        #Go through each square:
        for i in range(64):
            if flatboard[i]==0:
                #Empty square
                continue
            #Get data:
            piece = flatboard[i][0]
            color = flatboard[i][1]
            sign = +1
            #Adjust index if black piece, since piece sqaure tables
            #were designed for white:
            if color=='b':
                i = ((7-i)//8)*8 + i%8
                sign = -1
            #Adjust score:
            if piece=='P':
                score += sign*p.pawn_table[i]
            elif piece=='N':
                score+= sign*p.knight_table[i]
            elif piece=='B':
                score+=sign*p.bishop_table[i]
            elif piece=='R':
                score+=sign*p.rook_table[i]
            elif piece=='Q':
                score+=sign*p.queen_table[i]
            elif piece=='K':
                #King has different table values based on phase
                #of the game:
                if gamephase=='opening':
                    score+=sign*p.king_table[i]
                else:
                    score+=sign*p.king_endgame_table[i]
        return score  
    def doubledPawns(self,board,color):
        
        color = color[0]
        #Get indices of pawns:
        listofpawns = self.c.lookfor(board,'P'+color)
        #Count the number of doubled pawns by counting occurences of
        #repeats in their x-coordinates:
        repeats = 0
        temp = []
        for pawnpos in listofpawns:
            if pawnpos[0] in temp:
                repeats = repeats + 1
            else:
                temp.append(pawnpos[0])
        return repeats
    def blockedPawns(self,board,color):
        
        color = color[0]
        listofpawns = self.c.lookfor(board,'P'+color)
        blocked = 0
        #Self explanatory:
        for pawnpos in listofpawns:
            if ((color=='w' and self.c.isOccupiedby(board,pawnpos[0],pawnpos[1]-1,
                                           'black'))
                or (color=='b' and self.c.isOccupiedby(board,pawnpos[0],pawnpos[1]+1,
                                           'white'))):
                blocked = blocked + 1
        return blocked
    def isolatedPawns(self,board,color):
       
        color = color[0]
        listofpawns = self.c.lookfor(board,'P'+color)
        #Get x coordinates of all the pawns:
        xlist = [x for (x,y) in listofpawns]
        isolated = 0
        for x in xlist:
            if x!=0 and x!=7:
                #For non-edge cases:
                if x-1 not in xlist and x+1 not in xlist:
                    isolated+=1
            elif x==0 and 1 not in xlist:
                #Left edge:
                isolated+=1
            elif x==7 and 6 not in xlist:
                #Right edge:
                isolated+=1
        return isolated

##############################////////GUI FUNCTIONS\\\\\\\\\\\\\#############################
######################################MAIN FUNCTION##########################################
class GUI:

    def __init__(self):
        self.board = Board().getChess()
        self.c = Commands()
        self.a = AI()
        #In chess some data must be stored that is not apparent in the board:
        self.player = 0 #This is the player that makes the next move. 0 is white, 1 is black
        self.castling_rights = [[True, True],[True, True]]
        #The above stores whether or not each of the players are permitted to castle on
        #either side of the king. (Kingside, Queenside)
        self.En_Passant_Target = -1 #This variable will store a coordinate if there is a square that can be
                               #en passant captured on. Otherwise it stores -1, indicating lack of en passant
                               #targets. 
        self.half_move_clock = 0 #This variable stores the number of reversible moves that have been played so far.
        #Generate an instance of GamePosition class to store the above data:
        self.position = GamePosition(self.board,self.player,self.castling_rights,self.En_Passant_Target
                                ,self.half_move_clock)

        #Store the piece square tables here so they can be accessed globally by pieceSquareTable() function:
        
        pygame.init()

        self.size = (640, 640)
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Chess Game")
        self.game_icon = pygame.image.load('Media/ChessImage.png')
        pygame.display.set_icon(self.game_icon)

        self.media()

        self.bg = (49, 60, 43)

        self.startPage = pygame.Surface(self.size)
        self.startPage.fill(self.bg)

        self.diffPage = pygame.Surface(self.size)
        self.diffPage.fill(self.bg)

        self.flipPage = pygame.Surface(self.size)
        self.flipPage.fill(self.bg)

        self.selectPage = pygame.Surface(self.size)
        self.selectPage.fill(self.bg)

        self.colorPage = pygame.Surface(self.size)
        self.colorPage.fill(self.bg)

        # Stored [ x , y , width , height ] of buttons
        self.buttons = {
            1: [460-275, 380-15, 280, 75],
            2: [460-275, 470-15, 280, 75],
            3: [325-275, 280-15, 250, 250],
            4: [625-275, 280-15, 250, 250],
            5: [309-275, 250-15, 180, 180],
            6: [509-275, 250-15, 180, 180],
            7: [709-275, 250-15, 180, 180]
        }

        self.diffMenu = -1
        self.select = -1
        self.level = None
        self.temp = None

        self.box = pygame.image.load('Media/box.png')
        self.box = pygame.transform.scale(self.box, (640, 640))

        self.screen.blit(self.box,(0,0))
        pygame.mixer.Sound.play(self.welcome_sound)
        clock = pygame.time.Clock()  # Helps controlling fps of the game.
        self.initialize()
        pygame.display.update()
        
        #########################INFINITE LOOP#####################################
        #The program remains in this loop until the user quits the application
        while not self.gameEnded:
            if self.isMenu:
                #Menu needs to be shown right now.
                #Blit the background:
                #self.screen.blit(self.background,(0,0))         xxxxxxxxx
                if self.isAI==-1:
                    self.startMenu()
                elif self.isAI==True:
                    if self.diffMenu == -1:
                        self.play1Menu_A()
                    elif self.diffMenu == 1:
                        self.play1Menu_B()
                    if self.select == 1 and self.temp == None:
                        self.selectMenu()
                elif self.isAI==False:
                    self.play2Menu()
                if self.isFlip!=-1 and self.select == 2 :
                    self.call_board()
                    continue
                elif self.isFlip!=-1 and self.select == 3 :
                    self.call_board()
                    pygame.mixer.Sound.play(self.instructions_sound)
                    continue
                if self.isFlip!=-1 and self.temp == -1 :
                    self.call_board()
                    continue
                for event in pygame.event.get():
                    #Handle the events while in menu:
                    if event.type == QUIT:
                        #Window was closed.
                        self.gameEnded = True
                        pygame.mixer.Sound.play(self.exit_sound)
                        break
                    if event.type == MOUSEBUTTONUP:
                        self.onClick()
                        
                #Update the display:
                pygame.display.update()

                #Run at specific fps:
                clock.tick(10)
                continue
            #Menu part was done if this part reached.
            #If the AI is currently thinking the move to play
            #next, show some fancy looking squares to indicate
            #that.
            #Do it every 6 frames so it's not too fast:
            self.numm+=1
            if self.isAIThink and self.numm%10==0:
                self.Thinking()
                      
            for event in pygame.event.get():
                #Deal with all the user inputs:
                if event.type==QUIT:
                    #Window was closed.
                    self.gameEnded = True
                    pygame.mixer.Sound.play(self.exit_sound)
                    break
                #Under the following conditions, user input should be
                #completely ignored:
                if self.chessEnded or self.isTransition or self.isAIThink:
                    continue
                #isDown means a piece is being dragged.
                if self.select<=2:
                    if not self.isDown and event.type == MOUSEBUTTONDOWN:
                        #Mouse was pressed down.
                        #Get the oordinates of the mouse
                        pos = pygame.mouse.get_pos()
                        if pos[0] in range(0,640) and pos[1] in range(0,640):
                        #convert to chess coordinates:
                            chess_coord = self.pixel_coord_to_chess(pos)
                            x = chess_coord[0]
                            y = chess_coord[1]
                            #If the piece clicked on is not occupied by your own piece,
                            #ignore this mouse click:
                            if not self.c.isOccupiedby(self.board,x,y,'wb'[self.player]):
                                continue
                            #Now we're sure the user is holding their mouse on a
                            #piecec that is theirs.
                            #Get reference to the piece that should be dragged around or selected:
                            dragPiece = self.getPiece(chess_coord)
                            #Find the possible squares that this piece could attack:
                            listofTuples = self.c.findPossibleSquares(self.position,x,y)
                            #Highlight all such squares:
                            self.createShades(listofTuples)
                            #A green box should appear on the square which was selected, unless
                            #it's a king under check, in which case it shouldn't because the king
                            #has a red color on it in that case.
                            if dragPiece:
                                if ((dragPiece.pieceinfo[0]=='K') and
                                    (self.c.isCheck(self.position,'white') or self.c.isCheck(self.position,'black'))):
                                    None
                                else:
                                    self.listofShades.append(Shades(self.greenbox_image,(x,y)))
                                #A piece is being dragged:
                            self.isDown = True
                    if (self.isDown or self.isClicked) and event.type == MOUSEBUTTONUP:
                        #Mouse was released.
                        self.isDown = False
                        #Snap the piece back to its coordinate position
                        if dragPiece:
                            dragPiece.setpos((-1,-1))
                        #Get coordinates and convert them:
                        pos = pygame.mouse.get_pos()
                        chess_coord = self.pixel_coord_to_chess(pos)
                        x2 = chess_coord[0]
                        y2 = chess_coord[1]
                        #Initialize:
                        self.isTransition = False
                        if (x,y)==(x2,y2): #NO dragging occured
                            #(ie the mouse was held and released on the same square)
                            if not self.isClicked: #nothing had been clicked previously
                                #This is the first click
                                self.isClicked = True
                                self.prevPos = (x,y) #Store it so next time we know the origin
                            else: #Something had been clicked previously
                                #Find out location of previous click:
                                x,y = self.prevPos
                                if (x,y)==(x2,y2): #User clicked on the same square again.
                                    #So
                                    self.isClicked = False
                                    #Destroy all shades:
                                    self.createShades([])
                                else:
                                    #User clicked elsewhere on this second click:
                                    if self.c.isOccupiedby(self.board,x2,y2,'wb'[self.player]):
                                        #User clicked on a square that is occupied by their
                                        #own piece.
                                        #This is like making a first click on your own piece:
                                        self.isClicked = True
                                        self.prevPos = (x2,y2) #Store it
                                    else:
                                        #The user may or may not have clicked on a valid target square.
                                        self.isClicked = False
                                        #Destory all shades
                                        self.createShades([])
                                        self.isTransition = True #Possibly if the move was valid.


                        if not (x2,y2) in listofTuples:
                            #Move was invalid
                            self.isTransition = False
                            continue
                        #Reaching here means a valid move was selected.
                        #If the recording option was selected, store the move to the opening dictionary:
                        if self.isRecord:
                            key = self.c.pos2key(self.position)
                            #Make sure it isn't already in there:
                            if [(x,y),(x2,y2)] not in self.openings[key]:
                                self.openings[key].append([(x,y),(x2,y2)])

                        #Make the move:
                        self.c.makemove(self.position,x,y,x2,y2)
                        #Update this move to be the 'previous' move (latest move in fact), so that
                        #yellow shades can be shown on it.
                        self.prevMove = [x,y,x2,y2]
                        #Update which player is next to play:
                        self.player = self.position.getplayer()
                        if self.player == 1:
                            pygame.mixer.Sound.play(self.piece_sound)
                        else:
                            pygame.mixer.Sound.play(self.piece_sound)
                        #Add the new position to the history for it:
                        self.position.addtoHistory(self.position)
                        #Check for possibilty of draw:
                        HMC = self.position.getHMC()
                        if HMC>=100 or self.c.isStalemate(self.position) or self.position.checkRepition():
                            #There is a draw:
                            self.isDraw = True
                            self.chessEnded = True
                        #Check for possibilty of checkmate:
                        if self.c.isCheckmate(self.position,'white'):
                            self.winner = 'b'
                            self.chessEnded = True
                        if self.c.isCheckmate(self.position,'black'):
                            self.winner = 'w'
                            self.chessEnded = True
                        #If the AI option was selected and the game still hasn't finished,
                        #let the AI start thinking about its next move:
                        if self.isAI and not self.chessEnded:
                            if self.player==0:
                                colorsign = 1
                            else:
                                colorsign = -1
                            self.bestMoveReturn = []
                            self.move_thread = threading.Thread(target = self.a.negamax,
                                        args = (self.position,self.level,-1000000,1000000,colorsign,self.bestMoveReturn,self.openings,self.searched))
                            self.move_thread.start()
                            self.isAIThink = True

                        #Move the piece to its new destination:
                        dragPiece.setcoord((x2,y2))
                        #There may have been a capture, so the piece list should be regenerated.
                        #However, if animation is ocurring, the the captured piece should still remain visible.
                        if not self.isTransition:
                            self.listofWhitePieces,self.listofBlackPieces = self.createPieces(self.board)
                        else:
                            movingPiece = dragPiece
                            origin = self.chess_coord_to_pixels((x,y))
                            destiny = self.chess_coord_to_pixels((x2,y2))
                            movingPiece.setpos(origin)
                            step = (destiny[0]-origin[0],destiny[1]-origin[1])

                        #Either way shades should be deleted now:
                        self.createShades([])
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                        if self.player==1:
                            self.letters_dict = {'a': 7, 'b': 6, 'c': 5, 'd': 4, 'e': 3, 'f': 2, 'g': 1, 'h': 0}
                            self.numbers_dict = {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7}
                        with sr.Microphone() as source:
                            self.r.adjust_for_ambient_noise(source)
                            pygame.mixer.Sound.play(self.selectpiece_sound)
                            time.sleep(1.5)
                            try:
                                audio = self.r.listen(source,timeout=2,phrase_time_limit=2)
                                print("Recognizing...")
                                query = self.r.recognize_google(audio, language = "vi")
                                print(f"User said: {query}\n")
                                voice = query.lower()
                                if voice=='21':
                                    voice='a1'
                                elif voice == 'à hay' or voice=='à Hài':
                                    voice='a2'
                                elif voice == 'đi 4':
                                    voice='d4'
                                elif voice=='kết thúc':
                                    pygame.mixer.Sound.play(self.exit_sound)
                                    self.gameEnded=True
                                if len(voice) == 2:
                                    letter = voice[0]
                                    number = voice[1]
                                    if letter=='v':
                                        letter='b'
                                    elif letter=='s':
                                        letter='h'
                                    if letter in self.letters_dict.keys() and number in self.numbers_dict.keys():
                                        print(self.letters_dict[letter], self.numbers_dict[number])
                                        chess_coord = (self.letters_dict[letter], self.numbers_dict[number])
                                        x = chess_coord[0]
                                        y = chess_coord[1]
                                        # If the piece clicked on is not occupied by your own piece,
                                        # ignore this mouse click:
                                        if not self.c.isOccupiedby(self.board, x, y, 'wb'[self.player]):
                                            continue
                                        # Now we're sure the user is holding their mouse on a
                                        # piecec that is theirs.
                                        # Get reference to the piece that should be dragged around or selected:
                                        dragPiece = self.getPiece(chess_coord)
                                        # Find the possible squares that this piece could attack:
                                        listofTuples = self.c.findPossibleSquares(self.position, x, y)
                                        # Highlight all such squares:
                                        self.createShades(listofTuples)
                                        # A green box should appear on the square which was selected, unless
                                        # it's a king under check, in which case it shouldn't because the king
                                        # has a red color on it in that case.
                                        if dragPiece:
                                            if ((dragPiece.pieceinfo[0] == 'K') and
                                                    (self.c.isCheck(self.position, 'white') or self.c.isCheck(self.position,
                                                                                                              'black'))):
                                                None
                                            else:
                                                self.listofShades.append(Shades(self.greenbox_image, (x, y)))
                                        self.piece_selected_by_voice = True
                            except sr.UnknownValueError:
                                pygame.mixer.Sound.play(self.repeat_sound)
                            except sr.RequestError:
                                pygame.mixer.Sound.play(self.requesterror_sound)
                            except Exception:
                                pygame.mixer.Sound.play(self.repeat_sound)

                        
                    #Move to Destination Using voice
                    elif self.piece_selected_by_voice and event.type==pygame.MOUSEBUTTONDOWN and event.button==3 :
                        self.piece_selected_by_voice = False
                        with sr.Microphone() as source:
                            while True:
                                self.r.adjust_for_ambient_noise(source)
                                pygame.mixer.Sound.play(self.destination_sound)
                                time.sleep(1.5)
                                try:
                                    audio = self.r.listen(source,timeout=2,phrase_time_limit=2)
                                    print("Recognizing...")
                                    query2 = self.r.recognize_google(audio, language = "vi")
                                    print(f"User said: {query2}\n")
                                    voice2 = query2.lower()
                                    if voice2=='avon':
                                        voice2='a1'
                                    elif voice2 == 'heetu' or voice2=='hetu' or voice2=='do' or voice2 =='tattoo' or voice2 =='airport' or voice2 =='tetu' or voice2 =='edu':
                                        voice2='a2'
                                    elif voice2 == 'a tree' or voice2=='83':
                                        voice2='a3'
                                    elif voice2 == 'krrish 4':
                                        voice2='a4'
                                    elif voice2=='before':
                                        voice2='b4'
                                    elif voice2=='bittu' or voice2=='titu':
                                        voice2='b2'
                                    elif voice2=='ba' or voice2=='b.ed':
                                        voice2='b8'
                                    elif voice2=='shivan' or voice2=='shiva' or voice2=='civil':
                                        voice2='c1'
                                    elif voice2=='ceat':
                                        voice2='c8'
                                    elif voice2=='deewan' or voice2=='d 1' or voice2=='devon' or voice2=='devil':
                                        voice2='d1'
                                    elif voice2=='even' or voice2=='evil' or voice2=='evan' or voice2=='yuvan' or voice2=='t1':
                                        voice='e1'
                                    elif voice2=='youtube' or voice2=='tu':
                                        voice2='e2'
                                    elif voice2=='mi 4':
                                        voice2='e4'
                                    elif voice2=='mi 5':
                                        voice2='e5'
                                    elif voice2=='8':
                                        voice2='e8'
                                    elif voice2=='jivan':
                                        voice2='g1'
                                    elif voice2=='jeetu' or voice2=='jitu':
                                        voice2='g2'
                                    elif voice2=='zefo':
                                        voice2='g4'
                                    elif voice2 == 'kết thúc' or voice2 == 'end' or voice2 == 'close' or voice2=='stop' or voice2=='friend' or voice2=='top' or voice2=='finish' or voice2=='and':
                                        pygame.mixer.Sound.play(self.exit_sound)
                                        self.gameEnded=True
                                        break
                                    if len(voice2) == 2:
                                        letter = voice2[0]
                                        number = voice2[1]
                                        if letter=='v':
                                            letter='b'
                                        elif letter=='s':
                                            letter='h'
                                        if letter in self.letters_dict.keys() and number in self.numbers_dict.keys():
                                            print(self.letters_dict[letter], self.numbers_dict[number])
                                            chess_coord = (self.letters_dict[letter], self.numbers_dict[number])
                                            x2 = chess_coord[0]
                                            y2 = chess_coord[1]
                                            # Initialize:
                                            self.isTransition = False
                                            if not (x2, y2) in listofTuples:
                                                # Move was invalid
                                                self.isTransition = False
                                                continue
                                            # Reaching here means a valid move was selected.
                                            # If the recording option was selected, store the move to the opening dictionary:
                                            if self.isRecord:
                                                key = self.c.pos2key(self.position)
                                                # Make sure it isn't already in there:
                                                if [(x, y), (x2, y2)] not in self.openings[key]:
                                                    self.openings[key].append([(x, y), (x2, y2)])

                                            # Make the move:
                                            self.c.makemove(self.position, x, y, x2, y2)
                                            # Update this move to be the 'previous' move (latest move in fact), so that
                                            # yellow shades can be shown on it.
                                            self.prevMove = [x, y, x2, y2]
                                            # Update which player is next to play:
                                            self.player = self.position.getplayer()
                                            if self.player == 1:
                                                pygame.mixer.Sound.play(self.piece_sound)
                                            else:
                                                pygame.mixer.Sound.play(self.piece_sound)
                                            # Add the new position to the history for it:
                                            self.position.addtoHistory(self.position)
                                            # Check for possibilty of draw:
                                            HMC = self.position.getHMC()
                                            if HMC >= 100 or self.c.isStalemate(self.position) or self.position.checkRepition():
                                                # There is a draw:
                                                self.isDraw = True
                                                self.chessEnded = True
                                            # Check for possibilty of checkmate:
                                            if self.c.isCheckmate(self.position, 'white'):
                                                self.winner = 'b'
                                                self.chessEnded = True
                                            if self.c.isCheckmate(self.position, 'black'):
                                                self.winner = 'w'
                                                self.chessEnded = True
                                            # If the AI option was selected and the game still hasn't finished,
                                            # let the AI start thinking about its next move:
                                            if self.isAI and not self.chessEnded:
                                                if self.player == 0:
                                                    colorsign = 1
                                                else:
                                                    colorsign = -1
                                                self.bestMoveReturn = []
                                                self.move_thread = threading.Thread(target=self.a.negamax,
                                                                                    args=(self.position, self.level, -1000000, 1000000,
                                                                                          colorsign,
                                                                                          self.bestMoveReturn, self.openings,
                                                                                          self.searched))
                                                self.move_thread.start()
                                                self.isAIThink = True

                                            # Move the piece to its new destination:
                                            dragPiece.setcoord((x2, y2))
                                            # There may have been a capture, so the piece list should be regenerated.
                                            # However, if animation is ocurring, the the captured piece should still remain visible.
                                            if not self.isTransition:
                                                self.listofWhitePieces, self.listofBlackPieces = self.createPieces(self.board)
                                            else:
                                                movingPiece = dragPiece
                                                origin = self.chess_coord_to_pixels((x, y))
                                                destiny = self.chess_coord_to_pixels((x2, y2))
                                                movingPiece.setpos(origin)
                                                step = (destiny[0] - origin[0], destiny[1] - origin[1])

                                            # Either way shades should be deleted now:
                                            self.createShades([])
                                            break

                                except sr.UnknownValueError:
                                    pygame.mixer.Sound.play(self.repeat_sound)
                                except sr.RequestError:
                                    pygame.mixer.Sound.play(self.requesterror_sound)
                                except Exception:
                                    pygame.mixer.Sound.play(self.repeat_sound)



            #If an animation is supposed to happen, make it happen:
            if self.isTransition:
                p,q = movingPiece.getpos()
                dx2,dy2 = destiny
                n= 30.0
                if abs(p-dx2)<=abs(step[0]/n) and abs(q-dy2)<=abs(step[1]/n):
                    #The moving piece has reached its destination:
                    #Snap it back to its grid position:
                    movingPiece.setpos((-1,-1))
                    #Generate new piece list in case one got captured:
                    self.listofWhitePieces,self.listofBlackPieces = self.createPieces(self.board)
                    #No more transitioning:
                    self.isTransition = False
                    self.createShades([])
                else:
                    #Move it closer to its destination.
                    movingPiece.setpos((p+step[0]/n,q+step[1]/n))
            #If a piece is being dragged let the dragging piece follow the mouse:
            if self.isDown:
                m,k = pygame.mouse.get_pos()
                if dragPiece:
                    dragPiece.setpos((m-self.square_width/2,k-self.square_height/2))
            #If the AI is thinking, make sure to check if it isn't done thinking yet.
            #Also, if a piece is currently being animated don't ask the AI if it's
            #done thining, in case it replied in the affirmative and starts moving 
            #at the same time as your piece is moving:
            if self.isAIThink and not self.isTransition:
                if not self.move_thread.is_alive():
                    #The AI has made a decision.
                    #It's no longer thinking
                    self.isAIThink = False
                    #Destroy any shades:
                    self.createShades([])
                    #Get the move proposed:
                    if len(self.bestMoveReturn)==2:
                        [x,y],[x2,y2] = self.bestMoveReturn
                    else:
                        self.c.allMoves(self.position,color)
                    #Do everything just as if the user made a move by click-click movement:
                    self.c.makemove(self.position,x,y,x2,y2)
                    self.prevMove = [x,y,x2,y2]
                    self.player = self.position.getplayer()
                    HMC = self.position.getHMC()
                    self.position.addtoHistory(self.position)
                    if HMC>=100 or self.c.isStalemate(self.position) or self.position.checkRepition():
                        self.isDraw = True
                        self.chessEnded = True
                    if self.c.isCheckmate(self.position,'white'):
                        self.winner = 'b'
                        self.chessEnded = True
                    if self.c.isCheckmate(self.position,'black'):
                        self.winner = 'w'
                        self.chessEnded = True
                    #Animate the movement:
                    self.isTransition = True
                    movingPiece = self.getPiece((x,y))
                    origin = self.chess_coord_to_pixels((x,y))
                    destiny = self.chess_coord_to_pixels((x2,y2))
                    movingPiece.setpos(origin)
                    step = (destiny[0]-origin[0],destiny[1]-origin[1])
                    pygame.mixer.Sound.play(self.piece_sound)
            #Update positions of all images:
            self.drawBoard()
            #Update the display:
            pygame.display.update()

            #Run at specific fps:
            clock.tick(60)

        #Out of loop. Quit pygame:
        time.sleep(2)
        pygame.quit()
        #In case recording mode was on, save the openings dictionary to a file:
        if self.isRecord:
            file_handle.seek(0)
            pickle.dump(self.openings,file_handle)
            file_handle.truncate()
            file_handle.close()

    def DisplayPage(self, pageName):
        self.SurfacesAtTop = self.SurfacesAtTop.fromkeys(self.SurfacesAtTop, False)
        self.screen.blit(self.Surfaces[pageName], (0, 0))
        self.SurfacesAtTop[pageName] = True

    def chess_coord_to_pixels(self,chess_coord):
        x,y = chess_coord

        #There are two sets of coordinates that this function could choose to return.
        #One is the coordinates that would be usually returned, the other is one that
        #would be returned if the board were to be flipped.
        #Note that square width and height variables are defined in the main function and 
        #so are accessible here as global variables.

        if self.isAI:
            if self.AIPlayer==0:
                #This means you're playing against the AI and are playing as black:
                return ((7-x)*self.square_width, (7-y)*self.square_height)
            else:
                return (x*self.square_width, y*self.square_height)
        #Being here means two player game is being played.
        #If the flipping mode is enabled, and the player to play is black,
        #the board should flip, but not until the transition animation for 
        #white movement is complete:

        if not self.isFlip or self.player==0 ^ self.isTransition:
            return (x*self.square_width, y*self.square_height)
        else:
            return ((7-x)*self.square_width, (7-y)*self.square_height)
    def pixel_coord_to_chess(self,pixel_coord):
        if pixel_coord[0] in range(0,640) and pixel_coord[1] in range(0,640):
            x,y = (pixel_coord[0])//self.square_width, (pixel_coord[1])//self.square_height

            #See comments for chess_coord_to_pixels() for an explanation of the
            #conditions seen here:

            if self.isAI:
                if self.AIPlayer==0:
                    return (7-x,7-y)
                else:
                    return (x,y)
            if not self.isFlip or self.player==0 ^ self.isTransition:
                return (x,y)
            else:
                return (7-x,7-y)
    def getPiece(self,chess_coord):
        for piece in self.listofWhitePieces+self.listofBlackPieces:

            #piece.getInfo()[0] represents the chess coordinate occupied
            #by piece.

            if piece.getInfo()[0] == chess_coord:
                return piece
    def createPieces(self,board):
        #Initialize containers:
        self.listofWhitePieces = []
        self.listofBlackPieces = []
        #Loop through all squares:
        for i in range(8):
            for k in range(8):
                if board[i][k]!=0:
                    #The square is not empty, create a piece object:
                    p = Piece(board[i][k],(k,i), self.square_width, self.square_height)
                    #Append the reference to the object to the appropriate
                    #list:
                    if board[i][k][1]=='w':
                        self.listofWhitePieces.append(p)
                    else:
                        self.listofBlackPieces.append(p)
        #Return both:
        return [self.listofWhitePieces,self.listofBlackPieces]
    def createShades(self,listofTuples):
        
        
        #Empty the list
        self.listofShades = []
        if self.isTransition:
            #Nothing should be shaded when a piece is being animated:
            return
        if self.isDraw:
            #The game ended with a draw. Make yellow circle shades for
            #both the kings to show this is the case:

            coord = self.c.lookfor(self.board,'Kw')[0]
            shade = Shades(self.circle_image_yellow,coord)
            self.listofShades.append(shade)
            coord = self.c.lookfor(self.board,'Kb')[0]
            shade = Shades(self.circle_image_yellow,coord)
            self.listofShades.append(shade)
            pygame.mixer.Sound.play(self.draw_sound)
            #There is no need to go further:
            return
        if self.chessEnded:

            #The game has ended, with a checkmate because it cannot be a
            #draw if the code reached here.
            #Give the winning king a green circle shade:

            coord = self.c.lookfor(self.board,'K'+self.winner)[0]
            shade = Shades(self.circle_image_green_big,coord)
            self.listofShades.append(shade)
            if self.winner=='w':
                pygame.mixer.Sound.play(self.whitewin_sound)
            else:
                pygame.mixer.Sound.play(self.blackwin_sound)

        #If either king is under attack, give them a red circle:

        if self.c.isCheck(self.position,'white'):
            coord = self.c.lookfor(self.board,'Kw')[0]
            shade = Shades(self.circle_image_red,coord)
            self.listofShades.append(shade)
            pygame.mixer.Sound.play(self.checkmate_sound)
        if self.c.isCheck(self.position,'black'):
            coord = self.c.lookfor(self.board,'Kb')[0]
            shade = Shades(self.circle_image_red,coord)
            self.listofShades.append(shade)
            pygame.mixer.Sound.play(self.checkmate_sound)
        #Go through all the target squares inputted:
        for pos in listofTuples:
            #If the target square is occupied, it can be captured.
            #For a capturable square, there is a different shade.
            #Create the appropriate shade for each target square:
            if self.c.isOccupied(self.board,pos[0],pos[1]):
                img = self.circle_image_capture
            else:
                img = self.circle_image_green
            shade = Shades(img,pos)
            #Append:
            self.listofShades.append(shade)
    def drawBoard(self):
        #Blit the background:
        self.screen.blit(self.background,(0,0))

        #Choose the order in which to blit the pieces.
        #If black is about to play for example, white pieces
        #should be blitted first, so that when black is capturing,
        #the piece appears above:

        if self.player==1:
            order = [self.listofWhitePieces,self.listofBlackPieces]
        else:
            order = [self.listofBlackPieces,self.listofWhitePieces]
        if self.isTransition:
            #If a piece is being animated, the player info is changed despite
            #white still capturing over black, for example. Reverse the order:
            order = list(reversed(order))

        #The shades which appear during the following three conditions need to be
        #blitted first to appear under the pieces:

        if self.isDraw or self.chessEnded or self.isAIThink:
            #Shades
            for shade in self.listofShades:
                img,chess_coord = shade.getInfo()
                pixel_coord = self.chess_coord_to_pixels(chess_coord)
                self.screen.blit(img,pixel_coord)

        #Make shades to show what the previous move played was:
        if self.prevMove[0]!=-1 and not self.isTransition:
            x,y,x2,y2 = self.prevMove
            self.screen.blit(self.yellowbox_image,self.chess_coord_to_pixels((x,y)))
            self.screen.blit(self.yellowbox_image,self.chess_coord_to_pixels((x2,y2)))

        #Blit the Pieces:
        #Notw that one side has to be below the green circular shades to show
        #that they are being targeted, and the other side if dragged to such
        # a square should be blitted on top to show that it is capturing:

        #Potentially captured pieces:
        for piece in order[0]:
            
            chess_coord,subsection,pos = piece.getInfo()
            pixel_coord = self.chess_coord_to_pixels(chess_coord)
            if pos==(-1,-1):
                #Blit to default square:
                self.screen.blit(self.pieces_image,pixel_coord,subsection)
            else:
                #Blit to the specific coordinates:
                self.screen.blit(self.pieces_image,pos,subsection)

        #Blit the shades in between:
        if not (self.isDraw or self.chessEnded or self.isAIThink):
            for shade in self.listofShades:
                img,chess_coord = shade.getInfo()
                pixel_coord = self.chess_coord_to_pixels(chess_coord)
                self.screen.blit(img,pixel_coord)

        #Potentially capturing pieces:
        for piece in order[1]:
            chess_coord,subsection,pos = piece.getInfo()
            pixel_coord = self.chess_coord_to_pixels(chess_coord)
            if pos==(-1,-1):
                #Default square
                self.screen.blit(self.pieces_image,pixel_coord,subsection)
            else:
                #Specifc pixels:
                self.screen.blit(self.pieces_image,pos,subsection)

    def media(self):

        #Load all the images:
        #Load the background chess board image:
        self.background = pygame.image.load('Media\\board2.png').convert()

        #Load an image with all the pieces on it:
        pieces_image = pygame.image.load('Media\\Chess_Pieces_Sprite.png').convert_alpha()
        circle_image_green = pygame.image.load('Media\\green_circle_small.png').convert_alpha()
        circle_image_capture = pygame.image.load('Media\\green_circle_neg.png').convert_alpha()
        circle_image_red = pygame.image.load('Media\\red_circle_big.png').convert_alpha()
        greenbox_image = pygame.image.load('Media\\green_box.png').convert_alpha()
        circle_image_yellow = pygame.image.load('Media\\yellow_circle_big.png').convert_alpha()
        circle_image_green_big = pygame.image.load('Media\\green_circle_big.png').convert_alpha()
        yellowbox_image = pygame.image.load('Media\\yellow_box.png').convert_alpha()

       

        #Getting sizes:
        #Get background size:
        self.size_of_bg = self.background.get_rect().size

        #Get size of the individual squares
        self.square_width = (self.size_of_bg[0]-50)//8
        self.square_height = (self.size_of_bg[1] - 65)//8


        #Rescale the images so that each piece can fit in a square:

        self.pieces_image = pygame.transform.scale(pieces_image,
                                              (self.square_width*6,self.square_height*2))
        self.circle_image_green = pygame.transform.scale(circle_image_green,
                                              (self.square_width, self.square_height))
        self.circle_image_capture = pygame.transform.scale(circle_image_capture,
                                              (self.square_width-3, self.square_height-3))
        self.circle_image_red = pygame.transform.scale(circle_image_red,
                                              (self.square_width, self.square_height))
        self.greenbox_image = pygame.transform.scale(greenbox_image,
                                              (self.square_width-3, self.square_height-3))
        self.yellowbox_image = pygame.transform.scale(yellowbox_image,
                                              (self.square_width-3, self.square_height-3))
        self.circle_image_yellow = pygame.transform.scale(circle_image_yellow,
                                                     (self.square_width, self.square_height))
        self.circle_image_green_big = pygame.transform.scale(circle_image_green_big,
                                                     (self.square_width, self.square_height))
        

        #Loading Sounds
        self.welcome_sound = pygame.mixer.Sound("Voice\welcome.wav")
        self.exit_sound = pygame.mixer.Sound("Voice\exit.wav")
        self.flip_sound = pygame.mixer.Sound("Voice\Flip.wav")
        self.color_sound = pygame.mixer.Sound("Voice\color.wav")
        self.thinking_sound = pygame.mixer.Sound("Voice\Thinking.wav")
        self.difficulty_sound=pygame.mixer.Sound("Voice\difficulty.wav")
        self.turn_sound=pygame.mixer.Sound("Voice\Turn.wav")
        self.checkmate_sound = pygame.mixer.Sound("Voice\check.wav")
        self.draw_sound = pygame.mixer.Sound("Voice\draw.wav")
        self.whitewin_sound = pygame.mixer.Sound("Voice\whitewins.wav")
        self.blackwin_sound = pygame.mixer.Sound("Voice\Blackwins.wav")
        self.blackturn_sound = pygame.mixer.Sound("Voice\Blackturn.wav")
        self.whiteturn_sound = pygame.mixer.Sound("Voice\whiteturn.wav")
        self.piece_sound=pygame.mixer.Sound("Voice\piecehit.wav")
        self.destination_sound=pygame.mixer.Sound("Voice\destination.wav")
        self.instructions_sound = pygame.mixer.Sound("Voice\instructions.wav")
        self.repeat_sound = pygame.mixer.Sound("Voice\Repeat.wav")
        self.selectpiece_sound = pygame.mixer.Sound("Voice\selectpiece.wav")
        self.requesterror_sound = pygame.mixer.Sound("Voice\Requesterror.wav")
        self.control_sound = pygame.mixer.Sound("Voice\control.wav")



    def initialize(self):

        
        #Generate a list of pieces that should be drawn on the board:
        self.listofWhitePieces,self.listofBlackPieces = self.createPieces(self.board)

        #(the list contains references to objects of the class Piece)
        #Initialize a list of shades:
        self.listofShades = []
        self.isDown = False #Variable that shows if the mouse is being held down
                       #onto a piece 
        self.isClicked = False #To keep track of whether a piece was clicked in order
        #to indicate intention to move by the user.
        self.isTransition = False #Keeps track of whether or not a piece is being animated.
        self.isDraw = False #Will store True if the game ended with a draw
        self.chessEnded = False #Will become True once the chess game ends by checkmate, stalemate, etc.
        self.isRecord = False #Set this to True if you want to record moves to the Opening Book. Do not
        #set this to True unless you're 100% sure of what you're doing. The program will never modify
        #this value.
        self.isAIThink = False #Stores whether or not the AI is calculating the best move to be played.
        # Initialize the opening book dictionary, and set its values to be lists by default:
        self.openings = defaultdict(list)
        #If openingTable.txt exists, read from it and load the opening moves to the local dictionary.
        #If it doesn't, create a new one to write to if Recording is enabled:
        try:
            file_handle = open('openingTable.txt','r')
            self.openings = pickle.loads(file_handle.read())
        except:
            if self.isRecord:
                file_handle = open('openingTable.txt','w')

        self.letters_dict = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}#dictionary for voice
        self.numbers_dict = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}#dictionary for voice
        self.piece_selected_by_voice=False
        self.r = sr.Recognizer()#speechrecognition class object
        self.r.dynamic_energy_threshold = False
        self.r.energy_threshold = 400
        self.searched = {} #Global variable that allows negamax to keep track of nodes that have
        #already been evaluated.
        self.prevMove = [-1,-1,-1,-1] #Also a global varible that stores the last move played, to 
        #allow drawBoard() to create Shades on the squares.
        #Initialize some more values:
        #For animating AI thinking graphics:
        self.ax,self.ay=0,0
        self.numm = 0
        #For showing the menu and keeping track of user choices:
        self.isMenu = True
        self.isAI = -1
        self.isFlip = -1
        self.AIPlayer = -1
        #Finally, a variable to keep false until the user wants to quit:
        self.gameEnded = False

    def startMenu(self):
        #The user has not selected between playing against the AI
        #or playing against a friend.
        #So allow them to choose between playing with a friend or the AI:

        self.boardImage = pygame.image.load('Media/ChessImage.png')
        self.boardImage = pygame.transform.scale(self.boardImage, (1, 1))
        self.player1 = pygame.image.load('Media/play1.png')
        self.player1 = pygame.transform.scale(self.player1, (300, 100))
        self.player2 = pygame.image.load('Media/play2.png')
        self.player2 = pygame.transform.scale(self.player2, (300, 100))

        self.startPage.blit(self.box,(0,0))

        # self.startPage.blit(self.boardImage, (450-275, 60-15))
        self.startPage.blit(self.player1, (460-275, 380-15))
        self.startPage.blit(self.player2, (460-275, 470-15))

        self.screen.blit(self.startPage, (0, 0))

    def play1Menu_A(self):
        #The user has selected to play against the AI.
        #Allow the user to play as white or black:
        #self.screen.blit(self.playwhite_pic,(0,self.square_height*2))
        #self.screen.blit(self.playblack_pic,(self.square_width*4,self.square_height*2))

        self.selectcolor = pygame.image.load('Media/selectColor.png')
        self.selectcolor = pygame.transform.scale(self.selectcolor, (340, 80))
        self.playasblack = pygame.image.load('Media/playBlack.png')
        self.playasblack = pygame.transform.scale(self.playasblack, (200, 200))
        self.playaswhite = pygame.image.load('Media/playWhite.png')
        self.playaswhite = pygame.transform.scale(self.playaswhite, (200, 200))

        self.colorPage.blit(self.box,(0,0))

        self.colorPage.blit(self.selectcolor, (425-275, 80-15))
        self.colorPage.blit(self.playasblack, (325-250, 320-15))
        self.colorPage.blit(self.playaswhite, (625-250, 320-15))

        self.screen.blit(self.colorPage, (0, 0))
        global play_sound
        if play_sound:
            play_sound = False
            pygame.mixer.Sound.play(self.color_sound)


    def play1Menu_B(self):
        #The user has selected to play against the AI.
        #Allow the user to play as white or black:
        #self.screen.blit(self.playwhite_pic,(0,self.square_height*2))
        #self.screen.blit(self.playblack_pic,(self.square_width*4,self.square_height*2))

        self.selectDifficulty = pygame.image.load('Media/selectDifficulty.png')
        self.selectDifficulty = pygame.transform.scale(self.selectDifficulty, (340, 80))
        self.Easy = pygame.image.load('Media/Easy.png')
        self.Easy = pygame.transform.scale(self.Easy, (180, 180))
        self.Medium = pygame.image.load('Media/Medium.png')
        self.Medium = pygame.transform.scale(self.Medium, (180, 180))
        self.Hard = pygame.image.load('Media/Hard.png')
        self.Hard = pygame.transform.scale(self.Hard, (180, 180))

        self.diffPage.blit(self.box,(0,0))

        self.diffPage.blit(self.selectDifficulty, (425-275, 80-15))
        self.diffPage.blit(self.Easy, (309-275, 350-15))
        self.diffPage.blit(self.Medium, (509-275, 350-15))
        self.diffPage.blit(self.Hard, (709-275, 350-15))

        self.screen.blit(self.diffPage, (0, 0))
        self.diffMenu = 0
        global play_sound
        if play_sound:
            play_sound = False
            pygame.mixer.Sound.play(self.difficulty_sound)

    def play2Menu(self):
        #The user has selected to play with a friend.
        #Allow choice of flipping the board or not flipping the board:
        #self.screen.blit(self.flipDisabled_pic,(0,self.square_height*2))
        #self.screen.blit(self.flipEnabled_pic,(self.square_width*4,self.square_height*2))
        self.selectflip = pygame.image.load('Media/Flip.png')
        self.selectflip = pygame.transform.scale(self.selectflip, (340, 80))
        self.enableflip = pygame.image.load('Media/enableFlip.png')
        self.enableflip = pygame.transform.scale(self.enableflip, (200, 200))
        self.disableflip = pygame.image.load('Media/disableFlip.png')
        self.disableflip = pygame.transform.scale(self.disableflip, (200, 200))

        self.flipPage.blit(self.box,(0,0))

        self.flipPage.blit(self.selectflip, (425-275, 80-15))
        self.flipPage.blit(self.enableflip, (325-250, 320-15))
        self.flipPage.blit(self.disableflip, (625-250, 320-15))

        self.screen.blit(self.flipPage, (0, 0))
        global play_sound
        if play_sound:
            play_sound = False
            pygame.mixer.Sound.play(self.flip_sound)

    def selectMenu(self):
        self.selectmode = pygame.image.load('Media/selectMode.png')
        self.selectmode = pygame.transform.scale(self.selectmode, (340, 80))
        self.bymouse = pygame.image.load('Media/controlMouse.png')
        self.bymouse = pygame.transform.scale(self.bymouse, (200, 200))
        self.byvoice = pygame.image.load('Media/controlVoice.png')
        self.byvoice = pygame.transform.scale(self.byvoice, (200, 200))

        self.selectPage.blit(self.box, (0, 0))

        self.selectPage.blit(self.selectmode, (425 - 275, 80 - 15))
        self.selectPage.blit(self.bymouse, (325 - 250, 320 - 15))
        self.selectPage.blit(self.byvoice, (625 - 250, 320 - 15))

        self.screen.blit(self.selectPage, (0, 0))
        global play_sound
        if play_sound:
            play_sound = False
            pygame.mixer.Sound.play(self.control_sound)

    def call_board(self):
        #All settings have already been specified.
        #Draw all the pieces onto the board:
        self.drawBoard()
        #Don't let the menu ever appear again:
        self.isMenu = False
        #In case the player chose to play against the AI and decided to 
        #play as black, call upon the AI to make a move:
        if self.isAI and self.AIPlayer==0:
            colorsign=1
            self.bestMoveReturn = []
            self.move_thread = threading.Thread(target = self.a.negamax,
                        args = (self.position,self.level,-1000000,1000000,colorsign,self.bestMoveReturn,self.openings,self.searched))
            self.move_thread.start()
            self.isAIThink = True

    def onClick(self):
        global play_sound
        #The mouse was clicked somewhere.
        #Get the coordinates of click:

        posx, posy = pygame.mouse.get_pos()

        if self.buttons[1][0] < posx < self.buttons[1][0] + self.buttons[1][2]:
            if self.buttons[1][1] < posy < self.buttons[1][1] + self.buttons[1][3] and self.isAI == -1 :
                self.isAI = True
                posx , posy = (0 , 0)

        if self.buttons[2][0] < posx < self.buttons[2][0] + self.buttons[2][2] :
            if self.buttons[2][1] < posy < self.buttons[2][1] + self.buttons[2][3] and self.isAI == -1:
                self.isAI = False
                posx, posy = (0, 0)

        if self.buttons[3][0] < posx < self.buttons[3][0] + self.buttons[3][2]:
            if self.buttons[3][1] < posy < self.buttons[3][1] + self.buttons[3][3]:
                if self.isAI == True:
                    if self.diffMenu == -1:
                        self.AIPlayer = 0
                        self.isFlip = False
                        self.diffMenu = 1
                        posx, posy = (0, 0)
                        play_sound=True
                    elif self.isAI == True and self.select == 1:
                        self.select = 2
                        self.temp = 1
                        posx, posy = (0, 0)
                        print("Mouse Operated")
                elif self.isAI == False:
                    self.isFlip = True
                    self.temp = -1
                    posx, posy = (0, 0)
        if self.buttons[4][0] < posx < self.buttons[4][0] + self.buttons[4][2]:
            if self.buttons[4][1] < posy < self.buttons[4][1] + self.buttons[4][3]:
                if self.isAI == True:
                    if self.diffMenu == -1:
                        self.AIPlayer = 1
                        self.isFlip = False
                        self.diffMenu = 1
                        posx, posy = (0, 0)
                        play_sound = True
                    elif self.isAI == True and self.select == 1:
                        self.select = 3
                        self.temp = 1
                        posx, posy = (0, 0)
                        print("Voice Operated")
                elif self.isAI == False:
                    self.isFlip = False
                    self.temp = -1
                    posx, posy = (0, 0)

        if self.buttons[5][0] < posx < self.buttons[5][0] + self.buttons[5][2]:
            if self.buttons[5][1] < posy < self.buttons[5][1] + self.buttons[5][3]:
                self.level = 1
                self.select = 1
                posx, posy = (0, 0)
                play_sound = True

        if self.buttons[6][0] < posx < self.buttons[6][0] + self.buttons[6][2]:
            if self.buttons[6][1] < posy < self.buttons[6][1] + self.buttons[6][3]:
                self.level = 2
                self.select = 1
                posx, posy = (0, 0)
                play_sound = True

        if self.buttons[7][0] < posx < self.buttons[7][0] + self.buttons[7][2]:
            if self.buttons[7][1] < posy < self.buttons[7][1] + self.buttons[7][3]:
                self.level = 3
                self.select = 1
                posx, posy = (0, 0)
                play_sound = True

    def Thinking(self):
        ####while AI is thinking we will cause some fancy movements on screen
        self.ax+=1
        if self.ax==8:
            self.ay+=1
            self.ax=0
        if self.ay==8:
            self.ax,self.ay=0,0
        if self.ax%4==0:
            self.createShades([])
        #If the AI is white, start from the opposite side (since the board is flipped)
        if self.AIPlayer==0:
            self.listofShades.append(Shades(self.greenbox_image,(7-self.ax,7-self.ay)))
        else:
            self.listofShades.append(Shades(self.greenbox_image,(self.ax,self.ay)))

GUI()
