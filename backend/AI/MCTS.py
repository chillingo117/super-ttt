import numpy as np
from collections import defaultdict
from Constants import *


class Node:
    def __init__(self, state, player, parent=None, parentAction=None):
        self.state = state
        self.player = player
        self.parent = parent
        self.parentAction = parentAction
        self.children = []
        self.numberOfVisits = 0
        self.results = defaultdict(int)
        self.results[1] = 0
        self.results[-1] = 0
        self._untriedActions = None
        self._untriedActions = self.untriedActions()
        return

    def untriedActions(self):
        self._untriedActions = self.getLegalActions()
        return self._untriedActions

    def q(self):
        wins = self.results[1]
        loses = self.results[-1]
        return wins - loses

    def n(self):
        return self.numberOfVisits

    def expand(self):
        action = self._untriedActions.pop()
        nextState = self.move(action)
        childNode = Node( nextState, player=self.player, parent=self, parentAction=action )
        self.children.append(childNode)
        return childNode

    def isTerminalNode(self):
        return self.isGameOver()

    def rollout(self):
        while not self.isGameOver():
            possibleMoves = self.getLegalActions()

            action = self.rolloutPolicy(possibleMoves)
            self.state = self.move(action)
        return self.gameResult()

    def backpropagate(self, result):
        self.numberOfVisits += 1.
        self.results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)

    def isFullyExpanded(self):
        return len(self._untriedActions) == 0

    def bestChild(self, cParam=0.1):
        choicesWeights = [(c.q() / c.n()) + cParam * np.sqrt((2 * np.log(self.n()) / c.n())) for c in self.children]
        return self.children[np.argmax(choicesWeights)]

    def rolloutPolicy(self, possibleMoves):
        return possibleMoves[np.random.randint(len(possibleMoves))]

    def treePolicy(self):
        currentNode = self
        while not currentNode.isTerminalNode():
    
            if not currentNode.isFullyExpanded():
                return currentNode.expand()
            else:
                currentNode = currentNode.bestChild()
        return currentNode

    def bestAction(self, simCount):
        for i in range(simCount):
            v = self.treePolicy()
            reward = v.rollout()
            v.backpropagate(reward)
    
        return self.bestChild(cParam=0.).parentAction

    def getLegalActions(self):
        legalIndexes = []
        if self.state.isCurrentSubBoardFull():
            for i in range(9):
                if not self.state.superBoard[i].isFull():
                    legalIndexes.append(i)
        else:
            for i in range(9):
                if self.state.isCurrentSubBoardCellBlank(i):
                    legalIndexes.append(i)
        return legalIndexes

    def isGameOver(self):
        return self.state.winner != BLANK

    def gameResult(self):
        if(self.state.winner == TIE):
            return np.random.randint(2)
        elif self.state.winner == self.player:
            return 1
        else:
            return -1
    
    def move(self,action):
        newState = self.state.clone()
        newState.play(action)
        return newState
    
class MCTS:
    def GetPlayFromState(self, state, simCount):
        if(state.winner == 0):
            root = Node( state = state, player = state.currentPlayer)
            return root.bestAction(simCount)
        else:
            return None
