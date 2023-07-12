from random import randint
from BoardClasses import Board
import math
import time

class StudentAI():
    """Just to try if this works."""
    class Node:
        def __init__(self, move, color, parent, c):
            self.move = move
            self.childs = []
            self.simulation = 0
            self.wins = 0
            self.color = color
            self.parent = parent
            self.c = c

        def getUCT(self):
            if self.simulation == 0:
                return float("inf")
            return self.wins / self.simulation + self.c * math.sqrt(math.log(self.parent.simulation) / self.simulation)

        def getMaxChild(self):
            return max(self.childs, key=lambda x: x.getUCT())

        def isLeafNode(self):
            return self.childs == []

    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1: 2, 2: 1}
        self.color = 2
        self.colorDict = {1: "B", 2: "W"}
        self.timeIndex = 0
        self.reservedTime = 0

    @staticmethod
    def calculateTime(x):
        temp1 = -(1 / 2) * pow((x - 12) / 8, 2)
        temp2 = math.exp(temp1) * (250 / (8 * math.sqrt(2 * math.pi)))
        return temp2 + 4

    def get_move(self, move):
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1

        self.root = self.Node(None, self.color, None, 0.5)
        self.expand(self.root)

        if len(self.root.childs) == 1:
            self.reservedTime += round(self.calculateTime(self.timeIndex))
            self.timeIndex += 1
            self.board.make_move(self.root.childs[0].move, self.color)
            return self.root.childs[0].move

        t_end = round(time.time() + self.calculateTime(self.timeIndex))
        if self.reservedTime > 0:
            if self.reservedTime >= 2:
                t_end += 2
            else:
                t_end += self.reservedTime

        self.timeIndex += 1

        while time.time() < t_end:
            numberOfMoves = len(self.board.saved_move)

            node = self.root
            node.simulation += 1

            while not node.isLeafNode():
                node = node.getMaxChild()
                self.board.make_move(node.move, node.parent.color)

            if node.simulation == 0:
                result = self.runSimulation(node)
                self.backPropogate(node, result)
            elif node.simulation == 1:
                self.expand(node)
                if node.childs == []:
                    result = self.runSimulation(node)
                    self.backPropogate(node, result)
                else:
                    node = node.getMaxChild()
                    self.board.make_move(node.move, node.parent.color)
                    result = self.runSimulation(node)
                    self.backPropogate(node, result)
            else:
                result = self.runSimulation(node)
                self.backPropogate(node, result)

            while len(self.board.saved_move) > numberOfMoves:
                self.board.undo()

        move = self.root.getMaxChild().move
        self.board.make_move(move, self.color)
        return move

    def expand(self, node):
        for piece in self.board.get_all_possible_moves(node.color):
            for move in piece:
                tempNode = self.Node(move, self.opponent[node.color], node, 0.5)
                node.childs.append(tempNode)

    def backPropogate(self, curNode, result):
        node = curNode
        while node.parent:
            if node.parent.color == result:
                node.simulation += 1
                node.wins += 1
            else:
                node.simulation += 1
            node = node.parent

    def runSimulation(self, node):
        curColor = node.color
        while self.isFinished(self.board) == False and self.board.tie_counter < self.board.tie_max:
            moves = self.board.get_all_possible_moves(curColor)
            if moves == []:
                if self.board.black_count > self.board.white_count:
                    return 1
                else:
                    return 2
            index = randint(0, len(moves) - 1)
            inner_index = randint(0, len(moves[index]) - 1)
            move = moves[index][inner_index]
            self.board.make_move(move, curColor)
            curColor = self.opponent[curColor]

        if self.board.tie_counter >= self.board.tie_max:
            return self.color

        if self.board.white_count == 0:
            return 1
        else:
            return 2

    def isFinished(self, board):
        if board.white_count == 0 or board.black_count == 0:
            return True
        return False

if __name__ == "__main__":
    pass