#!/usr/bin/env python3
import sys
import itertools
import functools
import scipy.optimize
import numpy as np
import math


## READ IN COMMAND LINE ARGS ##
numUnits = 0
tolerance = 10e-6 #type float
argcount = 1 # to keep track of which arg we're reading in
battleValues = [] # values of each battlefield
verifyList = [] # for verify, the list of mixed strategies to verify
verifyProbsList = []
numBattlefields = 0
obj = "" # objective of game

mode = sys.argv[argcount] # Either either --find or --verify 
#print(mode)
argcount+=1
if sys.argv[argcount] == "--tolerance": # meant to give program some slack bc dealing w some imprecision
	argcount+=1
	tolerance = float(sys.argv[argcount]) #if it gives tolerance, the number is the next argument
	argcount+=1
obj = sys.argv[argcount] # either --win or --score
argcount+=1
if mode == "--find":
	argcount+=1 # will be --units, so skip
	numUnits = int(sys.argv[argcount]) # number of units
	argcount+=1
else: #in verify mode, read values from standard input
	for line in sys.stdin: # each line is a seperate pure strategy
		tempList = line.strip(" \n").replace(" ","").split(",") # each line will include num of battle fields (the number of ints), number of units(the sum of ints), and the probability of playing that strategy (last entry)
		realList = []
		for i in range(len(tempList) - 1):
			realList.append(int(tempList[i]))
		verifyProbsList.append(float(tempList[len(tempList)-1]))
		verifyList.append(realList)
	#print(verifyList)
	for i in verifyList[0]: #
		numUnits+=int(i) # For --verify the number of units is determined by sum of the values read from standard input.
	#argcount+=1

for i in range (argcount, len(sys.argv)): # from argcount to argc, The remaining arguments are positive integers giving the value of each battlefield starting with battlefield 1.
	battleValues.append(int(sys.argv[i]))
numBattlefields = len(battleValues) # The number of battlefields is determined by the number of these arguments

#print("mode is ", mode, " objective is ", obj, " tolerance is ", tolerance, " battlefield values are ", battleValues, " verify list is", verifyList, " num battlefields is ", numBattlefields, " num units is", numUnits)




# GENERATE LIST OF POSSIBLE MOVES -- vals
vals = []
for i in list(itertools.product(list(range(numUnits + 1)), repeat = numBattlefields)):
	if sum(i) == numUnits:
		vals.append(i)


## GENERATE SCORE VALUES MATRICES
playerOneScores = []
colvals = []
playerOneScore = 0
modeArr = []
# GENERATES GRID OF PLAYER ONE SCORES, 
for row, i in enumerate(vals):
	for col, j in enumerate(vals):
		for index, k in enumerate(battleValues):
			if i[index] > j[index]:
				playerOneScore = playerOneScore + battleValues[index] # if wins, give all points
			elif i[index] == j[index]: # if tie, give one half of points
				playerOneScore = playerOneScore + (1/2) * battleValues[index]
		colvals.append(playerOneScore)
		playerOneScore = 0
	playerOneScores.append(colvals)
	colvals = []
#print(playerOneScores)

## GENERATE WIN VALUES MATRIX
playerOneWins = []
colvals = []
playerOneWin = 0

#### FIND ####

if mode == "--find":
	if obj == "--score":
		modeArr = playerOneScores
	else: # obj is --win
		# GENERATES GRID OF PLAYER ONE WINS, (add one) playerOneWins contains the winarray, MAKES IT NEGATIVE FOR SCIPY
		for row, i in enumerate(vals):
			for col, j in enumerate(vals):
				for index, k in enumerate(battleValues):
					if i[index] > j[index]:
						playerOneWin = playerOneWin + battleValues[index] # if wins, give all points
					elif i[index] == j[index]: # if tie, give one half of points
						playerOneWin = playerOneWin + (1/2) * battleValues[index]
				if playerOneWin < (sum(battleValues)/2): # meaning they got less than half points, so they lose... added 1 arbitrarily to each win num
					colvals.append(1)
				elif playerOneWin > (sum(battleValues)/2):
					colvals.append(2)
				else:
					colvals.append(1.5)
				playerOneWin = 0
			playerOneWins.append(colvals)
			colvals = []
		#print(playerOneWins)
		modeArr = playerOneWins

	# find min val for bounds
	minVal = math.inf
	for i in modeArr:
		for j in i:
			if j < minVal:
				minVal = j

	## make everything negative for scipy stuff
	for row in range(len(modeArr)):
		for col in range(len(modeArr[0])):
			modeArr[row][col] = -modeArr[row][col]

	## SCIPY STUFF
	rows = len(vals)
	cols = len(vals)

	a1 = np.transpose(modeArr) #playerOneScores

	b_ub = [-1.0] * cols
	c = [1.0] * rows

	# bounds = 1/minval

	bounds = (0.0, 1.0/(minVal))

	result = scipy.optimize.linprog(c, a1, b_ub, None, None, bounds)
	#print(result.nit, "iterations")

	value = 1.0 / result.fun
	probArr = [pi * value for pi in result.x]


	# BUILDING EQUILIBRIUM ARRAY BY CHECKING INEQUALITIES
	equilibriumArr =[]
	for row, i in enumerate(a1):
		if probArr[row] > tolerance: #containing only pure strategies with probabilities that exceed the tolerance.
			lst = []
			for val in vals[row]:
				lst.append(val)
			lst.append(probArr[row])
			#equilibriumArr.append(list(vals[row], probArr[row]]))
			equilibriumArr.append(lst)

	for i in equilibriumArr:
		print(str(i).strip("[]"))
	#print(equilibriumArr)

# ## VERIFY
if mode == "--verify":
	if obj == "--score":
		modeArr = playerOneScores
	else: # obj is --win
		# GENERATES GRID OF PLAYER ONE WINS, (add one) playerOneWins contains the winarray, MAKES IT NEGATIVE FOR SCIPY
		for row, i in enumerate(vals):
			for col, j in enumerate(vals):
				for index, k in enumerate(battleValues):
					if i[index] > j[index]:
						playerOneWin = playerOneWin + battleValues[index] # if wins, give all points
					elif i[index] == j[index]: # if tie, give one half of points
						playerOneWin = playerOneWin + (1/2) * battleValues[index]
				if playerOneWin < (sum(battleValues)/2): # meaning they got less than half points, so they lose... added 1 arbitrarily to each win num
					colvals.append(0)
				elif playerOneWin > (sum(battleValues)/2):
					colvals.append(1)
				else:
					colvals.append(.5)
				playerOneWin = 0
			playerOneWins.append(colvals)
			colvals = []
		modeArr = playerOneWins
	#print("mode is ", mode, " objective is ", obj, " tolerance is ", tolerance, " battlefield values are ", battleValues, " verify list is", verifyList, " num battlefields is ", numBattlefields, " num units is", numUnits)
	#print(tolerance)

	expectValue = 0
	exy = 0
	for strat1 in verifyList: # create the expected value
		stratProb1 = verifyProbsList[verifyList.index(strat1)] # gives probability aka the last element of the list
		#strat1.pop() # removes probability, so now it's just the list of battlefield units
		for strat2 in verifyList:
			stratProb2 = verifyProbsList[verifyList.index(strat2)] # gives probability aka the last element of the list
			#print(modeArr[vals.index(tuple(strat1))][vals.index(tuple(strat2))])
			expectValue += stratProb1 * stratProb2 * modeArr[vals.index(tuple(strat1))][vals.index(tuple(strat2))] # gives the expected value @ that index
	#print("expected value = ", expectValue)

	for strat1 in verifyList: # first set of inequalities
		exy = 0
		stratProb1 = verifyProbsList[verifyList.index(strat1)] # gives probability aka the last element of the list	
		for strat2 in verifyList: # this whole loop represents an entire inequality
			stratProb2 = verifyProbsList[verifyList.index(strat2)]
			exy += stratProb2 * modeArr[vals.index(tuple(strat1))][vals.index(tuple(strat2))] # first variable stratprob1 or 1?
		if  exy - expectValue > tolerance: # ie. if ! exy <= expectValue
			print("EX[", strat1, ", ", strat2 ,"] = ",  exy ," > ", expectValue)
			sys.exit()
	# for strat2 in verifyList: # flip the inequalities?
	# 	exy = 0
	# 	stratProb2 = verifyProbsList[verifyList.index(strat2)] # gives probability aka the last element of the list	
	# 	for strat1 in verifyList:
	# 		stratProb1 = verifyProbsList[verifyList.index(strat1)]
	# 		exy += stratProb1 *  modeArr[vals.index(tuple(strat2))][vals.index(tuple(strat1))]
	# 	if exy + expectValue < tolerance:
	# 		print("EY[", strat1 ,", ", strat2, "] = ",  expectValue, " < ", exy)
	# 		sys.exit()
	print("PASSED")

#print(battleValues)