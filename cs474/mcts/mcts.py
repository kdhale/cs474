"""

Create a Python 3 module called mcts (so this must be in a file called mcts.py) that implements a 
function called mcts_strategy that takes a number of iterations and returns a function that takes 
a position and returns the move suggested by running MCTS for that number of iterations starting 
with that position.

"""
import pprint
from kalah import Kalah
import minimax
import random
import math

def mcts_strategy(numIters): #takes a number of iterations, 
	def retFunc(rootPosition): # takes a position (instances of Kalah.Position) and returns the move suggested by running MCTS for that number of iterations starting with that position.
		def maxUCB(p): # returns position w max UCB
			ucb = 0
			maxUCB = -math.inf
			maxArmMove = 0
			for move in p.legal_moves(): # key needs to be moves, not positions
				child = p.result(move) # position of that move
				rj = treeDict[child][0] / treeDict[child][1] # first thing in the list of  
				t = treeDict[p][1] # number of times we've accessed child's parent
				nj = treeDict[child][1]
				currUCB = rj + math.sqrt( (2 * math.log(t)) / nj )
				if currUCB > maxUCB:
					maxUCB = currUCB
					maxArmMove = move
			return maxArmMove
		def minUCB(p):
			ucb = 0
			minUCB = math.inf
			minArmMove = 0
			for move in p.legal_moves(): # key needs to be moves, not positions
				child = p.result(move) # position of that move
				rj = treeDict[child][0] / treeDict[child][1] # first thing in the list of  
				t = treeDict[p][1]
				nj = treeDict[child][1]
				currUCB = rj - math.sqrt( (2 * math.log(t)) / nj )
				if currUCB < minUCB:
					minUCB = currUCB
					minArmMove = move
			return minArmMove

		#print("starting a new game")
		treeDict = {} # keys = positions, values = lists(node wins, node total plays)
		iter = 0
		treeDict[rootPosition] = (0,0)
		curr = rootPosition
		
		while iter < numIters:
			path = []
			curr = rootPosition
			currMoves = curr.legal_moves()
			currExpandable = False
			child = 0
			while not currExpandable and not curr.game_over(): # traverse
				currMoves = curr.legal_moves()
				for move in currMoves: # keep running until run into a child that isn't in the tree yet
					if not curr.result(move) in treeDict: # if that child is not in the tree yet
						path.append(curr) # add curr to path of parents to be updated
						currExpandable = True
						missingChild = curr.result(move)
						break
				if not currExpandable:
					path.append(curr) # add curr to path of parents to be updated
					if curr.next_player() == 0:
						newCurr = curr.result(maxUCB(curr))
					else:
						newCurr = curr.result(minUCB(curr))
					curr = newCurr
			if curr.game_over():
					treeDict[curr] = (curr.winner(), 1) 
					for ancestor in path: # UPDATE every ancestor in path
						treeDict[ancestor] = (treeDict[ancestor][0] + treeDict[curr][0], treeDict[ancestor][1] + treeDict[curr][1])
			else: # else, so we're expandable, now find the move that doesn't have a node yet
				currPosition = missingChild # either do this or commented out stuff above
				newPosition = 0

				#found the child that isn't in the tree, now simulate random play
				while not currPosition.game_over(): 
					randMovesList = currPosition.legal_moves()
					randMove = random.choice(randMovesList)
					newPosition = currPosition.result(randMove)
					currPosition = newPosition

				# now random play is over, put child in tree, and time to sent stats back up to parent
				treeDict[missingChild] = (currPosition.winner(), 1) 
				for ancestor in path: # UPDATE every ancestor in path, path is CORRECT
					treeDict[ancestor] = (treeDict[ancestor][0] + treeDict[missingChild][0], treeDict[ancestor][1] + treeDict[missingChild][1])
			iter = iter + 1

		#chose the arm that either maximizes or minimizes the proportion of wins/visits (NOT UCB!!!)
		if rootPosition.next_player() == 0:
			max = -math.inf
			maxMove = 0
			for move in rootPosition.legal_moves():
				child = rootPosition.result(move)
				if (treeDict[child][0]/treeDict[child][1]) > max:
					maxMove = move
					max = treeDict[child][0]/treeDict[child][1]
			return maxMove
		else:
			min = math.inf
			minMove = 0
			for move in rootPosition.legal_moves():
				child = rootPosition.result(move)
				if (treeDict[child][0]/treeDict[child][1]) < min:
					minMove = move
					min = treeDict[child][0]/treeDict[child][1]
			return minMove
		
	treeDict = {}
	return retFunc