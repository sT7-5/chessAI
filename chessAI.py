import random


#below, value of each piece. King is 0 as it can never be captured i.e. game will end due to checkmate before it is removed from board
pieceScores = {"K": 0, "Q": 10, "R": 5, "B": 3, "N":3, "P": 1}
#value of outcomes. stalemate better than losing but checkmate is best
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3 #how many moves ahead to look


#Piece board position scores. This is so that pieces that are in certain, more dangerous positions are valued more than those same pieces in less threatening spots
rookBoard = [[4, 3, 4, 4, 4, 4, 3, 4],
             [4, 4, 4, 4, 4, 4, 4, 4],
             [1, 1, 2, 3, 3, 2, 1, 1],
             [1, 2, 3, 4, 4, 3, 2, 1],
             [1, 2, 3, 4, 4, 3, 2, 1],
             [1, 1, 2, 2, 2, 2, 1, 1],
             [4, 4, 4, 4, 4, 4, 4, 4],
             [4, 3, 4, 4, 4, 4, 3, 4]]

knightBoard = [[1, 1, 1, 1, 1, 1, 1, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 1, 1, 1, 1, 1, 1, 1]]

bishopBoard = [[4, 3, 2, 1, 1, 2, 3, 4],
               [3, 4, 3, 2, 2, 3, 4, 3],
               [2, 3, 4, 3, 3, 4, 3, 2],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [2, 3, 4, 3, 3, 4, 3, 2],
               [3, 4, 3, 2, 2, 3, 4, 3],
               [4, 3, 2, 1, 1, 2, 3, 4]]

queenBoard = [[1, 1, 1, 3, 1, 1, 1, 1],
              [1, 2, 3, 3, 3, 1, 1, 1],
              [1, 4, 3, 3, 3, 4, 2, 1],
              [1, 2, 3, 3, 3, 2, 2, 1],
              [1, 2, 3, 3, 3, 2, 2, 1],
              [1, 4, 3, 3, 3, 4, 2, 1],
              [1, 1, 2, 3, 3, 1, 1, 1],
              [1, 1, 1, 3, 1, 1, 1, 1]]

kingBoard = [[1, 1, 1, 1, 1, 1, 1, 1],
             [1, 1, 1, 1, 1, 1, 1, 1],
             [1, 1, 1, 1, 1, 1, 1, 1],
             [1, 1, 1, 1, 1, 1, 1, 1],
             [1, 1, 1, 1, 1, 1, 1, 1],
             [1, 1, 1, 1, 1, 1, 1, 1],
             [1, 1, 1, 1, 1, 1, 1, 1],
             [1, 1, 1, 1, 1, 1, 1, 1],]

wPawnBoard = [[9, 9, 9, 9, 9, 9, 9, 9],
              [8, 8, 8, 8, 8, 8, 8, 8],
              [5, 6, 6, 7, 7, 6, 6, 5],
              [2, 3, 3, 5, 5, 3, 3, 2],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [1, 1, 1, 0, 0, 1, 1, 1],
              [0, 0, 0, 0, 0, 0, 0, 0]]

bPawnBoard = [[0, 0, 0, 0, 0, 0, 0, 0],
              [1, 1, 1, 0, 0, 1, 1, 1],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [2, 3, 3, 5, 5, 3, 3, 2],
              [5, 6, 6, 7, 7, 6, 6, 5],
              [8, 8, 8, 8, 8, 8, 8, 8],
              [9, 9, 9, 9, 9, 9, 9, 9]]


pieceScoreBoard = {"N": knightBoard, "wP": wPawnBoard, "bP": bPawnBoard, "B": bishopBoard, "R": rookBoard, "Q": queenBoard}


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]


'''
#looking from black's perspective, i.e. want score to be as negative as possible so we start from highest and try to et scores that are lower
def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1

    #with MinMax, we want to minimize their maximum score
    #(carrying on) we assume opp will always make the best move, so we
    # try to find the move that leads to them making the best move with the lowest score
    #e.g. if one move leads to them making a best move taking a queen but another move leads them to make a best move of taking nothing
    #we make the move that leads to them taking nothing

    oppMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        #we make our move
        #then we run every move the opponent can make and find out the best move they can make
        #if their best move for that move we just made is less than their best move for a previous move we've made (oppMinMaxScore)
        #then we update the values, i.e. new bestPlayerMove and new MinMax opp score
        gs.makeTheMove(playerMove)
        oppMoves = gs.getValidMoves()
        if gs.stalemate:
            oppMaxScore = STALEMATE
        elif gs.checkmate:
            oppMaxScore = -CHECKMATE
        else:
            oppMaxScore = -CHECKMATE
            for moves in oppMoves:
                gs.makeTheMove(moves)
                gs.getValidMoves()
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board) #becomes negative if black's turn
                if score > oppMaxScore:
                    oppMaxScore = score
                gs.undoTheMove()
        if oppMaxScore < oppMinMaxScore: #the minimisation part. i.e. we update values if the best of the opponent is the lowest best move value of theirs so far
            oppMinMaxScore = oppMinMaxScore
            bestPlayerMove = playerMove
        gs.undoTheMove()
    return bestPlayerMove
'''


def findBestMove(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    #findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    #findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE,1 if gs.whiteToMove else -1)
    returnQueue.put(nextMove) #putting in the queue so other thread can access it

#depth is how far down the tree we want to go
#essentially this method does same thing as findBestMove but recursively. see comments on that method to re-visit how this works
#basically tries all the current player's moves and then tries all the moves the next player can make after those moves.
#algorithm assume's that other player will always make most optimal move so it will try to make the move that leads to the opponent making the lowest optimal move out of all the optimal moves
def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreBoard(gs)

    if whiteToMove: #if white to move then try to maximise score
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeTheMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoTheMove()
        return maxScore
    else:
        minScore = CHECKMATE #if black to move then try to minimse score
        for move in validMoves:
            gs.makeTheMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoTheMove()
        return minScore



#this algorithm will always try to find a maximum value, then just use the turnMultiplier for the score depending on who's turn it is
#this shorter to write
def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):

    global nextMove
    if depth == 0:
        #algorithm will try to maximise so the higher the score the better
        #the turn multiplier just makes it so that the maximised score is negative if it's black's turn meaning a very good black move etc..
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeTheMove(move)
        nextMoves = gs.getValidMoves()
        #score = negative of findMoveNegaMax. this is so that we don't choose the move that leads to the opponent making their best move
        #since the algorithm is always trying to maximise the score, if the result of calling findMoveNegaMax here is positive, then it
        #means the move was really good for the opponent thus, we need to make this result negative so that it isn't or isn't much greater than
        # the current maxScore, hoping a later move will make the function call return a less positive or even negative value meaning that move
        #was less beneficial for the opponent, essentially the -ve sign makes it so that whatever was good for them will be bad for us and
        #whatever was bad for them is good for us allowing us to then pick the best move for us
        score = -findMoveNegaMax(gs, nextMoves, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoTheMove()
    return maxScore


#improvement of negamax/minmax. it disregards move paths/tree paths if we already know of a better path
#alpha = max, beta = min
def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turn_multiplier):
    global nextMove
    if depth == 0:
        return turn_multiplier * scoreBoard(gs)
    # NOTES FOR MYSELF...
    # example of this working. If white makes the final move and pov switches to black, when it's black's turn and it runs scoreBoard(gs)
    # if it's really negative, then it's good for black but then the turn multiplier switches it to positive.
    # then the positive score is returned 6 lines of code downwards and then made into a negative number. This means that the resulting score
    # is a large negative number, which from white's pov is bad so, it will know to not want to do this move
    # same for if after white makes the final move and black runs scoreBoard(gs), if new position is bad for black, i.e the function returns
    # a large positive number, it will be turned to negative then returned. then 6 lines of code down, that large negative number
    # now becomes a large positive number, meaning it's good for white from its pov
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeTheMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
                print(move, maxScore)
        gs.undoTheMove()
        #the pruning
        #NOTES FOR MYSELF...
        #beta is the opposing player's current worst case scenario
        #if alpha becomes greater than beta, then that means we've found a scenario that is even worse for the opposing player
        #since the opposing player is trying to minimise us, we can disregard this path as they will never let us have the opportunity
        #to make the new best move (for us)
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

'''
positive score = good for white, negative score = goood for black
'''
def scoreBoard(gs):

    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE #black has won so return negative score
        else:
            return CHECKMATE #white won so return positive score
    elif gs.stalemate:
        return STALEMATE

    #scoring accoring to how many pieces there are
    score = 0 #more positive = good for white, more negative = good for black
    for row in range(8):
        for col in range(8):
            #getting the current piece's score board
            pieceValue = 0
            if gs.board[row][col] != "--":
                piece = gs.board[row][col] #e.g "wP", "bK", "bB", "wN"
                if piece[1] != "K": #king has no position table
                    if piece[1] == "P":
                        pieceValue = pieceScoreBoard[piece][row][col]
                    else:
                        pieceValue = pieceScoreBoard[piece[1]][row][col]

                if gs.board[row][col][0] == "w":
                    score += pieceScores[piece[1]] + pieceValue
                elif gs.board[row][col][0] == "b":
                    score -= pieceScores[piece[1]] + pieceValue
    return score







