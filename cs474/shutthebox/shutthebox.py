import sys
import itertools
import functools


## READ IN COMMAND LINE ARGS ##

player = sys.argv[1] # Either --one or --two
mode = sys.argv[2] # Either --expect or --move
boxString = sys.argv[3] # a string of unique, increasing digits in the range 1 through 9 indicating which numbers are still open.
boxes = []
for index, box in enumerate(boxString):
	boxes.append(int(box))
roll = 0

if player == "--two":
	playerOneScore = int(sys.argv[4])
	if mode == "--move":
		roll = int(sys.argv[5])

if player == "--one" and mode == "--move":
	roll = int(sys.argv[4])

## CREATE DICTIONARY OF ALL COMBINATIONS OF BOX NUMBERS w SUMS BETWEEN 2 - 12

allNums = [1,2,3,4,5,6,7,8,9]

allcombs = []

for i in allNums:
	allcombs.append(list(itertools.combinations(allNums, i)))

allRolls = {} # now contains all subsets of sums possible from 2 - 12 using numbers 1-9

for a in allcombs:
	for j in a:
		if sum(j) >= 2 and sum(j) <= 12:
			if sum(j) in allRolls:
				allRolls[sum(j)].append(j)
			else:
				allRolls[sum(j)] = [(j)]

allRolls[1] = [[1]]

## CREATE DICTIONARY OF PROBABILITY OF EACH ROLL SUM (for 2 dice only)

allRollsProbs = {}
sides = [1,2,3,4,5,6]

for i in sides:
	for j in sides:
		if i+j in allRollsProbs:
			allRollsProbs[i+j] += (1/36)
		else:
			allRollsProbs[i+j] = (1/36)

## MEMOIZATION

# learned about memozation here: https://medium.com/@nkhaja/memoization-and-decorators-with-python-32f607439f84
def memoize(func):
	store = {}
	def mem_func(*args, **kwargs):
		key = ""
		for a in args:
			key += str(a)
		if key not in store:
			store[key] = func(*args, **kwargs)
		return store[key]
	return mem_func

### PLAYER ONE FUNCTIONS

global playerOneOpt
playerOneOpt = []

def playerOneInitialCall(openTiles):
	setprob = 0
	if(sum(openTiles) > 6):
		for j in range(2,13): # run for each roll 2-12
			state = playerOneState(openTiles,j)
			setprob += allRollsProbs[j] * state
	else:
		for j in range(1,7): # run for each roll 2-12
			state = playerOneState(openTiles,j)
			setprob += (1/6) * state
	return setprob

def playerOneState(openTiles, roll):
	sumset = []
	maxsum = 0
	containSet = False

	if not openTiles: # if empty, return 1
		return 1
	for r in allRolls[roll]: # for every subset of the sum set for this roll, build list of sumsets and check that they're all still open
		containSet = False
		if(all(num in openTiles for num in r)):
			containSet = True
			break
	if not containSet: # if doesn't contain set, pregentage of winning is 1 - player twos expected win
		return 1 - playerTwoInitialCall([1,2,3,4,5,6,7,8,9], sum(openTiles))

	elif sum(openTiles) - roll > 6:
		for r in allRolls[roll]: # for every subset of the sum set for this roll, build list of sumsets and check that they're all still open
			containSet = True
			for num in r: # for every number in each subset
				if not num in openTiles: # check if that number is in Opentiles, if not then move to next subset
					containSet = False
			if containSet:
				sumset.append(r)
			probSumList = {}
		for set in sumset:
			setprob = 0
			for j in range(2,13): # run for each roll 2-12
				openTilesPrime = openTiles.copy()
				for s in set:
					openTilesPrime.remove(s) # remove values of set from open tiles
				state = playerOneState(openTilesPrime,j)
				setprob += allRollsProbs[j] * state
			probSumList[tuple(set)] = setprob # get probability of winning for each subset choice
		maxsum = 0
		optimalMove = 0
		for key in probSumList:
			if probSumList[key] > maxsum:
				maxsum = probSumList[key]
				optimalMove = list(key)
		playerOneOpt.append(optimalMove)
		return maxsum
	elif sum(openTiles) - roll <= 6:
		for r in allRolls[roll]: # for every subset of the sum set for this roll
			containSet = True
			for num in r: # for every number in each subset
				if not num in openTiles: # check if that number is in Opentiles, if not then move to next subset
					containSet = False
			if containSet:
				sumset.append(r)
			probSumList = {}
		for set in sumset:
			setprob = 0
			for j in range(1,7): # run for each roll 2-12
				openTilesPrime = openTiles.copy()
				for s in set:
					openTilesPrime.remove(s) # remove values of set from open tiles
				state = playerOneState(openTilesPrime,j)
				setprob += (1/6) * state
			probSumList[tuple(set)] = setprob # get probability of winning for each subset choice
		optimalMove = 0
		for key in probSumList:
			if probSumList[key] > maxsum:
				maxsum = probSumList[key]
				optimalMove = list(key)
		playerOneOpt.append(optimalMove)
		return maxsum


#### PLAYER TWO FUNCITONS ####


global playerTwoOpt
playerTwoOpt = []


def playerTwoInitialCall(openTiles,target):
	setprob = 0
	if(sum(openTiles) > 6):
		for j in range(2,13): # run for each roll 2-12
			state = playerTwoState(openTiles,j,target)
			setprob += allRollsProbs[j] * state
	else:
		for j in range(1,7): # run for each roll 2-12
			state = playerTwoState(openTiles,j,target)
			setprob += (1/6) * state
	return setprob

def playerTwoState(openTiles, roll, target):
	sumset = []
	maxsum = 0
	containSet = False
	for r in allRolls[roll]: # for every subset of the sum set for this roll, build list of sumsets and check that they're all still open
		containSet = False
		if(all(num in openTiles for num in r)):
			containSet = True
			break

	if not containSet: 
		if sum(openTiles) > target:
			return 0
		elif sum(openTiles) == target:
			return 1/2
		else:
			return 1
	elif sum(openTiles) - roll > 6:
		for r in allRolls[roll]: # for every subset of the sum set for this roll, build list of sumsets and check that they're all still open
			containSet = True
			for num in r: # for every number in each subset
				if not num in openTiles: # check if that number is in Opentiles, if not then move to next subset
					containSet = False
			if containSet:
				sumset.append(r)
			probSumList = {}
		for set in sumset:
			setprob = 0
			for j in range(2,13): # run for each roll 2-12
				openTilesPrime = openTiles.copy()
				for s in set:
					openTilesPrime.remove(s) # remove values of set from open tiles
				state = playerTwoState(openTilesPrime,j,target)
				setprob += allRollsProbs[j] * state
			probSumList[tuple(set)] = setprob # get probability of winning for each subset choice
		maxsum = 0
		optimalMove = 0
		for key in probSumList:
			if probSumList[key] > maxsum:
				maxsum = probSumList[key]
				optimalMove = list(key)
		playerTwoOpt.append(optimalMove) #print("optimal move when roll is ", roll, " and list is ", openTiles, " is ", optimalMove)
		return maxsum
	elif sum(openTiles) - roll <= 6:
		for r in allRolls[roll]: # for every subset of the sum set for this roll
			containSet = True
			for num in r: # for every number in each subset
				if not num in openTiles: # check if that number is in Opentiles, if not then move to next subset
					containSet = False
			if containSet:
				sumset.append(r)
			probSumList = {}
		for set in sumset:
			setprob = 0
			for j in range(1,7): # run for each roll 2-12
				openTilesPrime = openTiles.copy()
				for s in set:
					openTilesPrime.remove(s) # remove values of set from open tiles
				setprob += (1/6) * playerTwoState(openTilesPrime,j,target)
			probSumList[tuple(set)] = setprob # get probability of winning for each subset choice
		optimalMove = 0
		for key in probSumList:
			if probSumList[key] > maxsum:
				maxsum = probSumList[key]
				optimalMove = list(key)
		playerTwoOpt.append(optimalMove)
		return maxsum
		


playerOneState = memoize(playerOneState)
playerTwoState = memoize(playerTwoState)

#print(playerOneInitialCall([1,2,3,4,5,6,7,8,9]))
if player == "--one" and mode == "--move":
	a = playerOneState(boxes, roll)
	print(playerOneOpt.pop())
elif player == "--one" and mode == "--expect":
	print("%.6f" % playerOneInitialCall(boxes))



## HOW do I get it to return optimal move without remaking whole function
if player == "--two" and mode == "--move":
	a = playerTwoState(boxes, roll, playerOneScore)
	print(playerTwoOpt.pop())
elif player == "--two" and mode == "--expect":
	print("%.6f" % (playerTwoInitialCall(boxes, playerOneScore)))