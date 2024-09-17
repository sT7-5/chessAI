'''
handles user input and UI
'''



from copyreg import pickle
from os import close

import pygame as p
from Chess import engine, chessAI
from multiprocessing import Process, Queue



BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_WIDTH = BOARD_WIDTH/2
MOVE_LOG_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT / DIMENSION #size of each board square
MAX_FPS = 15
IMGS = {} #a dictionary, stores a key:value pair, similar to hashmap in java

def loadImages():
    pieces = ["bB", "bK", "bN", "bP", "bQ", "bR", "wB", "wK", "wN", "wP", "wQ", "wR"]

    for piece in pieces:
        IMGS[piece] = p.transform.scale(p.image.load("imgs/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))



def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = engine.GameState()

    validMoves = gs.getValidMoves()
    validMoveMade = False #doing getValidMoves is expensive so will only call the method again
                          #if this is true meaning valid move has been made
    animate = False

    loadImages() #only want to do this once as loading images is a taxing thing for pygame
    #print(gs.board)
    running = True
    gamePlay = True

    playerOne = True #true if human is playing as white, false if AI is playing as white
    playerTwo = False #see above but for black

    AiThinking = False
    moveFinderProcess = None

    moveUndone = False

    moveLogFont = p.font.SysFont("Arial", 12, False, False)

    sqSelected = () #keeps track of last square selected
    playerClicks = [] #keeps track of user clicks, e.g. clicks 2,1 then 4,3 ([(2,1), (4,3)])
    while running: #the game loop, this is run 15 times second
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            elif event.type == p.MOUSEBUTTONDOWN:
                if gamePlay:
                    location = p.mouse.get_pos() #return x,y coordinate
                    col = int(location[0] // SQ_SIZE)
                    row = int(location[1] // SQ_SIZE)
                    if sqSelected == (row, col) or col >= 8: #if clicked on same square twice or clicked on move log, deselect
                        sqSelected = () #deselect
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2 and humanTurn:
                        moveObj = engine.Move(playerClicks[0], playerClicks[1], gs.board)  # create the move
                        print(moveObj.getChessNotation())
                        for i in range(len(validMoves)):
                            if moveObj == validMoves[i]:
                                gs.makeTheMove(validMoves[i])  # if it is, make the move
                                validMoveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                                print("valid move made")
                        if not validMoveMade:
                            playerClicks = [sqSelected]


            elif event.type == p.KEYDOWN: #can reset game when it has finished or whilst game is happening
                if event.key == p.K_c:
                    gs.undoTheMove()
                    validMoveMade = True
                    gamePlay = True
                    animate = False
                    if AiThinking:
                        moveFinderProcess.terminate()
                        AiThinking = False
                    moveUndone = True

                elif event.key == p.K_r:
                    gs = engine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    animate = False
                    validMoveMade = False
                    gamePlay = True
                    if AiThinking:
                        moveFinderProcess.terminate()
                        AiThinking = False
                    moveUndone = True



        #AI
        if gamePlay and not humanTurn and not moveUndone: #if ai's turn to move, then (for now) make random move
            if not AiThinking: #if Ai is not thinking then come up with a turn
                AiThinking = True
                returnQueue = Queue() #passes data between threads as threads don't share resources
                moveFinderProcess = Process(target=chessAI.findBestMove, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start() #calls the findBestMove method (same as aiMove = chessAI.findBestMove(gs, validMoves), but in a new thread, allowing rest of the code to run

            if not moveFinderProcess.is_alive(): #when the thread has finished calling the findBestMove method then do stuff
                aiMove = returnQueue.get()
                if aiMove is None:
                    print("can't find best move, making random move")
                    aiMove = chessAI.findRandomMove(validMoves)
                else:
                    print("made best move")
                gs.makeTheMove(aiMove)
                validMoveMade = True
                animate = True
                AiThinking = False



        if validMoveMade : #valid move made so now need to set flag back to false and generate the new set of valid moves
            if animate:
                print("animating move")
                animatingMove(gs.moveLog[-1], screen, gs.board, clock)
                animate = False
            print("getting valid moves again")
            validMoves = gs.getValidMoves()
            validMoveMade = False
            moveUndone = False 


        drawGameState(screen, gs, validMoves, sqSelected, gs.moveLog, moveLogFont)

        if gs.checkmate:
            gamePlay = False
            if gs.whiteToMove:
                drawEndText(screen, "BlACK WINS BY CHECKMATE")
            else:
                drawEndText(screen, "WHITE WINS BY CHECKMATE")
        elif gs.stalemate:
            gamePlay = False
            drawEndText(screen, "STALEMATE")

        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs, validMoves, sqSelected, moveLog, font):
    drawBoard(screen)
    highlightMoves(screen, gs, validMoves, sqSelected, moveLog)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, font)

def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_WIDTH, MOVE_LOG_HEIGHT)   #where the move log will be drawn on
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveTexts = []
    moveLog = gs.moveLog

    for j in range(0, len(moveLog), 2): #getting the move log in text format
        tempStr = str(j//2 + 1) + ". " + moveLog[j].getChessNotation()
        if j + 1 < len(moveLog):
            tempStr += " " + moveLog[j + 1].getChessNotation() + " "
        moveTexts.append(tempStr)
    padding = 5
    textY = 5
    rowsCompleted = 1 #used as a multiplier so that when a row is completed in the move log panel, to start the next row, you move a row over and then begin printing text downwards again

    #if in check or checkmate append correct notation
    # the checkmate symbol works correctly but the check symbol doesn't as the check symbol disappears if the next move takes the king out of check 
    if gs.inCheck and not gs.checkmate:
        moveTexts[-1] += "+ "
    if gs.checkmate:
        moveTexts[-1] += "#"
    for i in range(len(moveTexts)):
        tempText = moveTexts[i]
        textObj = font.render(tempText, 0, p.Color('white'))
        textLoc = moveLogRect.move(padding, textY)
        screen.blit(textObj, textLoc)
        textY += textObj.get_height()
        if textY + textObj.get_height() >= MOVE_LOG_HEIGHT:#if reached bottom of move log side panel then move all the way back up and to the right
            padding = 90 * rowsCompleted
            textY = 5
            rowsCompleted += 1



def drawBoard(screen):
    global boardColor
    boardColor = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            currentColour = boardColor[(r+c)%2]
            p.draw.rect(screen, currentColour, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            currentPiece = board[r][c]
            if(currentPiece != "--"):
                screen.blit(IMGS[currentPiece], p.Rect(c*SQ_SIZE, r *SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlightMoves(screen, gs, validMoves, sqSelected, moveLog):
     if sqSelected != ():
        row, col = sqSelected
        if gs.board[row][col][0] == ("w" if gs.whiteToMove else "b"):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s, (col*SQ_SIZE, row*SQ_SIZE))
            s.fill(p.Color("yellow"))
            for moves in validMoves:
                if moves.startRow == row and moves.startCol == col:
                    screen.blit(s, (moves.endCol*SQ_SIZE, moves.endRow*SQ_SIZE))
            #if previous move has been made, then highlight the piece moved, and it's original position in red
            if len(moveLog) > 0:
                s.fill(p.Color("red"))
                lastMove = moveLog[-1]
                screen.blit(s, (lastMove.startCol*SQ_SIZE, lastMove.startRow*SQ_SIZE))
                screen.blit(s, (lastMove.endCol*SQ_SIZE, lastMove.endRow*SQ_SIZE))


def animatingMove(move, screen, board, clock):
    global boardColor
    dR = move.endRow - move.startRow #how many squares between start and end
    dC = move.endCol - move.startCol
    framesPerSquare = 5 #how many frames to move 1 square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare #total num of frames needed
    for frame in range(frameCount + 1):
        row, col = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #board[move.endRow][move.endCol] = "--" #drawPieces will draw the piece already at its final destination so need to erase it
        colour = boardColor[(move.endRow + move.endCol) %2]
        endSq = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, colour, endSq)
        if move.pieceCaptured != "--":
            screen.blit(IMGS[move.pieceCaptured], endSq)
        screen.blit(IMGS[move.pieceMoved], p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawEndText(screen, text):
    font = p.font.SysFont("Arial", 32, True, False)
    textObj = font.render(text, 0, p.Color('Black'))
    textLoc = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObj.get_width() / 2, BOARD_HEIGHT / 2 - textObj.get_height() / 2)
    screen.blit(textObj, textLoc)


if __name__ == "__main__": #needed to prevent new tabs/windows opening when ai thinks. Allows the process to only be
                           # created "moveFinderProcess = Process(target=chessAI.findBestMove, args=(gs, validMoves, returnQueue))"
                           # when this specific main.py file is being run directly
    main()
