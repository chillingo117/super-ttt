import json
from WinPatterns import WIN_PATTERNS
from Constants import *
from datetime import datetime


def convertXYToBoardIndex(x, y):
    index = x + 3 * (2 - y)
    return index


def generateSuperBoard():
    superBoard = []
    for index in range(9):
        superBoard.append(TTTSubBoard(index))
    return superBoard


class TTTSubBoard():
    def __init__(self, index, squares=None, winner=None):
        if squares is None:
            self.squares = [0, 0, 0,
                            0, 0, 0,
                            0, 0, 0, ]
        else:
            self.squares = squares
        if winner is None:
            self.winner = BLANK
        else:
            self.winner = winner
        self.index = index

    def isFull(self):
        return all(self.squares)

    def toJson(self):
        return {
            "squares": self.squares,
            "winner": self.winner
        }


class TTTInstance:
    def __init__(self):
        self.winner = BLANK
        self.superBoard = generateSuperBoard()
        self.currentPlayer = STARTING_PLAYER
        self.currentSubBoard = self.superBoard[CENTER_INDEX]
        self.lastPingTime = datetime.now()
        self.history = []
        self.history.append(self.getBoard())

    def clone(self):
        clone = TTTInstance()
        cloneJson = json.loads(self.getBoard())
        clone.winner = cloneJson["winner"]
        clone.currentPlayer = cloneJson["currentPlayer"]
        clone.superBoard = []
        for i in range(len(cloneJson["subBoards"])):
            subBoard = cloneJson["subBoards"][i]
            subBoard = TTTSubBoard(i, subBoard["squares"], subBoard["winner"])
            clone.superBoard.append(subBoard)
        clone.currentSubBoard = clone.superBoard[cloneJson["currentSubBoard"]]
        return clone

    def getHistory(self):
        return self.history

    def jumpToHistory(self, step):
        self.history = self.history[:step + 1]
        latest = json.loads(self.history[len(self.history) - 1])
        self.winner = latest["winner"]
        self.currentPlayer = latest["currentPlayer"]
        self.superBoard = []
        for i in range(len(latest["subBoards"])):
            subBoard = latest["subBoards"][i]
            subBoard = TTTSubBoard(i, subBoard["squares"], subBoard["winner"])
            self.superBoard.append(subBoard)
        self.currentSubBoard = self.superBoard[latest["currentSubBoard"]]


    def placeSymbol(self, index):
        self.currentSubBoard.squares[index] = self.currentPlayer
        self.checkSubBoardWinCondition()
        self.checkSuperBoardWinCondition()
        self.checkTie()
        self.currentSubBoard = self.superBoard[index]
        self.currentPlayer = self.currentPlayer * - 1

    def play(self, index):
        if self.isCurrentSubBoardFull():
            self.currentSubBoard = self.superBoard[index]
        else:
            self.placeSymbol(index)
        self.history.append(self.getBoard())

    def checkSuperBoardWinCondition(self):
        for pattern in WIN_PATTERNS:
            sumNum = sum(i[0] * i[1].winner for i in zip(pattern, self.superBoard))
            if sumNum == (3 * PLAYER1):
                self.winner = PLAYER1
                break
            elif sumNum == (3 * PLAYER2):
                self.winner = PLAYER2
                break
                
    def checkTie(self):
        allSquares = []
        for subBoard in self.superBoard:
            allSquares += subBoard.squares
        if(all(allSquares)):
            self.winner = TIE

    def checkSubBoardWinCondition(self):
        for pattern in WIN_PATTERNS:
            sumNum = sum(i[0] * i[1] for i in zip(pattern, self.currentSubBoard.squares))
            if sumNum == (3 * PLAYER1):
                self.currentSubBoard.winner = PLAYER1
                break
            elif sumNum == (3 * PLAYER2):
                self.currentSubBoard.winner = PLAYER2
                break

    def isCurrentSubBoardCellBlank(self, index):
        return self.currentSubBoard.squares[index] == BLANK

    def isCurrentSubBoardFull(self):
        return all(self.currentSubBoard.squares)

    def hasGameEnded(self):
        winner = None
        if self.winner == PLAYER2:
            winner = "Player " + PLAYER2_SYMBOL
        elif self.winner == PLAYER1:
            winner = "Player " + PLAYER1_SYMBOL
        elif self.winner == TIE:
            winner = "Tie"
        return (self.winner != BLANK), winner

    def getBoard(self):
        boardsAsJson = []
        for i in range(9):
            boardsAsJson.append(self.superBoard[i].toJson())
        selfAsJson = {
            "subBoards": boardsAsJson,
            "currentSubBoard": self.currentSubBoard.index,
            "currentPlayer": self.currentPlayer,
            "winner": self.winner,
            "historyLength": len(self.history),
        }
        return json.dumps(selfAsJson)

    def close(self):
        self.superBoard = None

    def ping(self):
        self.lastPingTime = datetime.now()
