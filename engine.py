"""STORES INFO ABOUT CURRENT STATE AND KEEPS LOG OF ALL MOVES  """
from ctypes import c_char
from typing import final


class GameState():
    def __init__(self):

        #board is a 8x8 2d list
        #first letter is colour, second is piece type. "K", "N", "P" are king, knight, pawn...

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],

        ]

        self.getMoveFunctions = {"P": self.getPawnMoves, "R": self.getRookMoves,
                                 "N": self.getKnightMoves, "B": self.getBishopMoves,
                                 "Q": self.getQueenMoves, "K": self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []

        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.stalemate = False
        self.checkmate = False

        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enpassantPossible = () #stores square that could possibly be used for an en passant
        self.enpassantLog = [self.enpassantPossible]

        self.currentCastleRights = CastleRights(True, True, True, True)
        self.castleRightsLog =  [CastleRights(True, True, True, True)]

    def makeTheMove(self, move):
        
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved

        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

        #if king moved update their locators

        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.pawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        #if pawn moved 2 spaces, make space above/below it enpassantable
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
            average = (move.startRow + move.endRow) // 2
            self.enpassantPossible = (average, move.endCol)
        else:#if move just made was not a pawn, next move cannot do enpassant so reset
            self.enpassantPossible = ()

        if move.isCastle:
            if move.startCol - move.endCol == 2: #if it's a queen side castle
                
                rook = self.board[move.startRow][0]
                self.board[move.startRow][0] = "--" #make original rook pos empty
                self.board[move.startRow][move.startCol-1] = rook #place rook to right  of king
            elif move.startCol - move.endCol == -2: #if it's a king side castle
                rook = self.board[move.startRow][7]
                self.board[move.startRow][7] = "--" #make original rook pos empty
                self.board[move.startRow][move.startCol+1] = rook #place rook to left of king


        self.enpassantLog.append(self.enpassantPossible)

        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastleRights.bks, self.currentCastleRights.bqs, self.currentCastleRights.wks, self.currentCastleRights.wqs))



    def undoTheMove(self):
        if len(self.moveLog) != 0:
            prevMove = self.moveLog.pop() #start square, end square and board
            self.board[prevMove.startRow][prevMove.startCol] = prevMove.pieceMoved
            self.board[prevMove.endRow][prevMove.endCol] = prevMove.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # Update the king's location if needed
            if prevMove.pieceMoved == "wK":
                self.whiteKingLocation = (prevMove.startRow, prevMove.startCol)
            elif prevMove.pieceMoved == "bK":
                self.blackKingLocation = (prevMove.startRow, prevMove.startCol)
            self.getValidMoves()



            if prevMove.isEnpassantMove: #if it was an enpassant move, then correctly re-place the pieces
                self.board[prevMove.endRow][prevMove.endCol] = "--"
                if prevMove.pieceMoved[0] == "w":
                    self.board[prevMove.startRow][prevMove.endCol] = "bP"
                else:
                    self.board[prevMove.startRow][prevMove.endCol] = "wP"


            self.enpassantLog.pop()
            self.enpassantPossible = self.enpassantLog[-1]



            self.castleRightsLog.pop()
            temp = self.castleRightsLog[-1]
            self.currentCastleRights = CastleRights(temp.bks, temp.bqs, temp.wks, temp.wqs) #-1 index in list refers to last index or most recently added item

            if prevMove.isCastle:
                if prevMove.endCol - prevMove.startCol == 2: #if king side castle
                    self.board[prevMove.endRow][prevMove.endCol + 1] = self.board[prevMove.endRow][prevMove.endCol - 1]
                    self.board[prevMove.endRow][prevMove.endCol-1] = "--"
                else: #if queen side castle
                    self.board[prevMove.endRow][prevMove.endCol-2] = self.board[prevMove.endRow][prevMove.endCol+1]
                    self.board[prevMove.endRow][prevMove.endCol+1] = "--"

            self.checkmate = False
            self.stalemate = False




    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastleRights.wks = False
            self.currentCastleRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastleRights.bks = False
            self.currentCastleRights.bqs = False

        elif move.pieceMoved == "wR":
            #left white rook i.e wqs, white queen side, rook
            if move.startRow == 7 and move.startCol == 0:
                self.currentCastleRights.wqs = False
            #right white rook, wks rook
            elif move.startRow == 7 and move.startCol == 7:
                self.currentCastleRights.wks = False
        elif move.pieceMoved == "bR":
            #left black rook, bqs rook
            if move.startRow == 0 and move.startCol == 0:
                self.currentCastleRights.bqs = False
            elif move.startRow == 0 and move.startCol == 7:
                self.currentCastleRights.bks = False

        if move.pieceCaptured == "wR":
            if move.endCol == 0:  # left rook
                self.currentCastleRights.wqs = False
            elif move.endCol == 7:  # right rook
                self.currentCastleRights.wks = False
        elif move.pieceCaptured == "bR":
            if move.endCol == 0:  # left rook
                self.currentCastleRights.bqs = False
            elif move.endCol == 7:  # right rook
                self.currentCastleRights.bks = False






    def getValidMoves(self):

        tempEnpassantPossible = self.enpassantPossible

        moves = []
        kingRow = 0
        kingCol = 0

        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        elif not self.whiteToMove:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]



        if self.inCheck:
            if len(self.checks) == 1: #if there's only 1 check, you can block or move the king
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                piece = self.board[checkRow][checkCol]

                validSquares = [] #squares the pieces can move to
                if piece[1] == "N": #if knight must capture the knight or move the king
                    validSquares = [(checkRow, checkCol)] #pieces can only move to the knight so that it is captured
                else: #if other piece, can block
                    for i in range (1,8):
                        validSquare = (kingRow + check[2]*i, kingCol + check[3]*i) #moving away from king in the direction of the piece causing the check
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: #if the current valid square is the location of the piece, break as no point moving pieces further away
                            break

                for i in range (len(moves)-1, -1, -1):
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: #if the move that could be made is not valid, remove it from valid moves
                            moves.remove(moves[i])

            else:
                self.getKingMoves(kingRow, kingCol, moves)

        else:
            moves = self.getAllPossibleMoves()
            self.getCastleMoves(kingRow, kingCol, moves)

        if len(moves) == 0:
            if self.inCheck :
                self.checkmate = True
            else:
                # TODO stalemate on repeated moves
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False


        self.enpassantPossible = tempEnpassantPossible
        return moves
    


    def getAllPossibleMoves(self):
        #moves = [Move((6,4), (4,4), self.board)]
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0] #gets the first letter of the board piece ie, w from wK
                if(turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    currentPiece = self.board[row][col][1] #gets second letter to know what type of piece it is
                    self.getMoveFunctions[currentPiece](row, col, moves)
        return moves


    def inCheck(self):

        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, row, col):

        self.whiteToMove = not self.whiteToMove  # switch to opponent's point of view
        opponents_moves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in opponents_moves:
            if move.endRow == row and move.endCol == col:  # square is under attack
                return True
        return False


#PIECE MOVES

    def getPawnMoves(self, row, col, moves):

        piecePinned = False
        pinnedDirection = ()

        for i in range(len(self.pins)-1, -1, -1):
            #if a pinned position is the position of the pawn, then record info and remove that pin from the list
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinnedDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = - 1
            startRow = 6
            enemyCol = "b"
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
            enemyR = "bR"
            enemyQ = "bQ"
        else:
            moveAmount = 1
            startRow = 1
            enemyCol = "w"
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
            enemyR = "wR"
            enemyQ = "wQ"

        if self.board[row+moveAmount][col] == "--":#if there's nothing in front
            if not piecePinned or pinnedDirection == (moveAmount, 0): #if it's not pinned or if the piece pinning it is in the direction it wants to move
                moves.append(Move((row,col), (row+moveAmount, col), self.board))
                if row == startRow and self.board[row+2*moveAmount][col] == "--":
                    moves.append(Move((row,col), (row+2*moveAmount, col), self.board))

        #captures
        if col - 1 >= 0: #checking for capturing to the left diagonally
            if not piecePinned or pinnedDirection == (moveAmount, -1):
                if self.board[row+moveAmount][col-1][0] == enemyCol: #if there's a black piece diagonally 1 space left then can capture
                    moves.append(Move((row,col), (row+moveAmount, col-1), self.board))
                elif (row+moveAmount, col-1) == self.enpassantPossible:
                    #checking if doing enpassant move ends up leaving king in check
                    blockingPiece = moveDisabled = False
                    if kingRow == row:
                        if kingCol < col:#king to the left
                            #inside range = between king and pawn, outside range = between pawn and edge of board
                            insideRange = range(kingCol+1, col-1)
                            outsideRange = range(col+1, 8)
                        else:#king to the right
                            insideRange = range(kingCol - 1, col, -1)
                            outsideRange = range(col-2, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square == enemyR or square == enemyQ:
                                if not blockingPiece:#if there's no blocking piece between the pawn and the outside attacking piece
                                    moveDisabled = True
                            elif square != "--" :
                                blockingPiece = True
                    if not moveDisabled:
                        moves.append(Move((row, col), (row + moveAmount, col - 1), self.board, enpassantMove=True))

        if col + 1 <= 7: #checking for capturing to the right diagonally
            if not piecePinned or pinnedDirection == (moveAmount, 1):
                if self.board[row+moveAmount][col+1][0] == enemyCol:
                    moves.append(Move((row,col), (row+moveAmount, col+1), self.board))
                elif (row+moveAmount, col+1) == self.enpassantPossible:
                    moveDisabled = blockingPiece = False
                    if kingRow == row:
                        if kingCol < col:#king to the left
                            #inside range = between king and pawn, outside range = between pawn and edge of board
                            insideRange = range(kingCol+1, col)
                            outsideRange = range(col+2, 8)
                        else:#king to the right
                            insideRange = range(kingCol - 1, col+1 , -1)
                            outsideRange = range(col-1, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square == enemyR or square == enemyQ:
                                if not blockingPiece:#if no blocking piece between pawn and outside attacking piece, then enpassant not allowed
                                    moveDisabled = True
                            elif square != "--" :
                                blockingPiece = True
                    if not moveDisabled:
                        moves.append(Move((row,col), (row+moveAmount, col+1), self.board, enpassantMove=True))



    def getKingMoves(self, row, col, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        sameCol = "w" if self.whiteToMove else "b"

        for i in range(8):
            finalRow = row + rowMoves[i]
            finalCol = col + colMoves[i]
            if 0<=finalRow<=7 and 0<=finalCol<=7:
                endPiece = self.board[finalRow][finalCol]
                if endPiece[0] != sameCol:

                    #moving the king in the direction and then checking if it causes it to be in check
                    if sameCol == "w":
                        self.whiteKingLocation = (finalRow, finalCol)
                    else:
                        self.blackKingLocation = (finalRow, finalCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((row, col), (finalRow, finalCol), self.board))
                    if sameCol == "w":
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)

    def getKnightMoves(self, row, col, moves):

        piecePinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break


        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        sameCol = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            finalRow = row + m[0]
            finalCol = col + m[1]
            if 0<=finalRow<8 and 0<=finalCol<8:
                if not piecePinned: # no need for additional or pinnedDirection = (...) as knight cant move vertically up/down or diagonally
                    endPiece = self.board[finalRow][finalCol]
                    if endPiece[0] != sameCol:
                        moves.append(Move((row, col), (finalRow, finalCol), self.board))

    def getBishopMoves(self, row, col, moves):

        piecePinned = False
        pinnedDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinnedDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        bishopMoves = ((-1, -1), (-1, 1), (1, -1), (1,1))
        enemyCol = "b" if self.whiteToMove else "w"
        for m in bishopMoves:
            for i in range (1,8):
                endRow = row + m[0]*i
                endCol = col + m[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    if not piecePinned or pinnedDirection == m or pinnedDirection == (-m[0], -m[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyCol:
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getRookMoves(self, row, col, moves):

        piecePinned = False
        pinnedDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinnedDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != "Q":
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0,-1), (1,0), (0,1))
        enemyCol = "b" if self.whiteToMove else "w"

        for d in directions:
            for i in range (1,8):
                endRow = row + d[0]*i
                endCol = col + d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    #if not pinned or moving in the same direction or opposite direction as the pin, can move
                    if not piecePinned or pinnedDirection == d or pinnedDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyCol:
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            allyCol = "w"
            enemyCol = "b"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            allyCol = "b"
            enemyCol = "w"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        #moving horizontally, vertically and diagonally from king position.
        #if we find ally piece we
        directions = ((-1,0), (0,-1), (1,0), (0,1), (-1,-1), (-1, 1), (1, -1), (1,1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePins=()
            for i in range(1,8):
                endRow = startRow + d[0]*i
                endCol = startCol + d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyCol and endPiece[1] != "K":
                        if possiblePins == (): #if it's the first friendly piece in that direction only then could it be a pinned piece
                            possiblePins = (endRow, endCol, d[0], d[1])
                        else:
                            break #if second friendly piece occurs, then no need to worry about pins in this direction
                    elif endPiece[0] == enemyCol:
                        pieceType = endPiece[1]
                        # first 4 moves in kingMoves are directions rook can attack from
                        # last 4 moves in kingMoves are directions bishop can attack from
                        # all moves in kingMoves are directions queen can attack from
                        # another king can attack when it's 1 square away (next to) the current king.
                        # if i == 0, then that means we're exploring squares only 1 away from king
                        # pawn can attack if diagonally 1 square away from king
                        if (0<=j<=3 and pieceType == "R") or (4<=j<=7 and pieceType == "B") or (pieceType == "Q") or (i==1 and pieceType == "K") or (i==1 and pieceType  == "P" and ((enemyCol == "w" and 6<=j<=7) or (enemyCol=="b" and 4<=j<=5))) :
                            if possiblePins == (): #if there's no piece blocking the king, then it's in check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePins)
                                break
                        else: #if there's no checks being applied then just break
                            break
                else:
                    break
        knightMoves = ((-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2,1), (2,-1,), (1, -2))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0<=endRow<8 and 0<=endCol<8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyCol and endPiece[1] == "N":
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks


    def getCastleMoves(self, row, col, moves):
        if self.squareUnderAttack(row, col):
            return
        if (self.whiteToMove and self.currentCastleRights.wks) or (not self.whiteToMove and self.currentCastleRights.bks):
            self.getKSCastleMoves(row, col, moves)
        if (self.whiteToMove and self.currentCastleRights.wqs) or (not self.whiteToMove and self.currentCastleRights.bqs):

            self.getQSCastleMoves(row, col, moves)

    def getKSCastleMoves(self, row, col, moves):
        #if 2 spaces to right of king are free
        if self.board[row][col+1] == "--" and self.board[row][col+2] == "--":
            #if 2 spaces to the right of king are not in check
            if not self.squareUnderAttack(row, col+1) and not self.squareUnderAttack(row, col+2):
                moves.append(Move((row, col), (row, col+2), self.board, castle=True))

    def getQSCastleMoves(self, row, col, moves):
        #if 2 spaces left of king are free
        if self.board[row][col-1] == "--" and self.board[row][col-2] == "--" and self.board[row][col-3] == "--":
            #if 2 spaces left of king are not in check
            if not self.squareUnderAttack(row, col-1) and not self.squareUnderAttack(row, col-2):
                moves.append(Move((row, col), (row, col-2), self.board, castle=True))









#class to keep track of castle rights
class CastleRights():
    def __init__(self, bks, bqs, wks, wqs):
        self.bks = bks
        self.bqs = bqs
        self.wqs = wqs
        self.wks = wks

class Move():

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enpassantMove=False, castle=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isEnpassantMove = False
        self.isCapture = board[self.endRow][self.endCol] != "--"


        self.pawnPromotion = False
        if (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7):
            self.pawnPromotion = True

        self.isEnpassantMove = enpassantMove
        self.isCastle = castle

        #generatign a unique id for this move so that we can compare it in the __eq__ method. basically a hash of the move
        self.moveId = self.startRow*1000 + self.startCol*100 + self.endRow*100 + self.endCol


    # overriding the equal's method.
    # this is used so that we can compare and check if a move object generated from a mouse click
    # is the same as one generated in the code using given numbers i.e Move((6,4), (4,4), self.board)
    def __eq__(self, other):
        if isinstance(other, Move):
            if other.startRow == self.startRow and other.startCol == self.startCol:
                return other.moveId == self.moveId
            return False


    def getChessNotation(self):
        if self.isCastle:
            if self.startCol - self.endCol == -2: #if king side castle return proper notation
                return "O-O"
            else: #if queen side castle then return proper notation
                return "O-O-O"

        elif self.isCapture: #if capture
            if self.pieceMoved[1] == "P": #if pawn capture return correct notation
                if self.pawnPromotion: #if pawn capture and promotion
                    return self.colsToFiles[self.startCol] + "x" + self.getRankFile(self.endRow, self.endCol) + "=Q"
                else:#if just pawn capture
                    return self.colsToFiles[self.startCol] + "x" + self.getRankFile(self.endRow, self.endCol)
            else:#if not pawn capture then return correct notation
                return self.pieceMoved[1] + "x" + self.getRankFile(self.endRow, self.endCol)

        elif self.pawnPromotion and not self.isCapture:#if pawn promotion but not capture
            return self.getRankFile(self.endRow, self.endCol)+"=Q"
        else:
            if self.pieceMoved[1] == "P":
                return self.getRankFile(self.endRow, self.endCol)
            else:
                return self.pieceMoved[1] + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]
