"""

Write a function called q_learn in a module called qfl that takes an object that models the Two-Minute Drill 
version of NFL strategy and a time limit in seconds and returns a function that takes a non-terminal position 
in the game and returns the index of the selected offensive play. The function that it returns should execute in 
less than 10 microseconds for any position. Because there are too many positions to compute a Q-value for each 
individually within the time bound, you should use a function approximator such as a linear approximator.


Your q_learn function can observe outcomes from a particular position given a choice of action (offensive play)
by calling the result method on the model object passed to q_learn module. The result method takes a position 
and action and returns a pair whose first component is the resulting position. Positions are given as 4-tuples 
with components for the remaining yards needed to score, the downs left, the yards needed to reset the number of 
downs left, and the time remaining in 5-second ticks. The second component of the pair returned from result is a 
triple specifying the number of yards gained by that action, the time elapsed after that action (in 5-second ticks), 
and a Boolean flag indicating whether the action resulted in a turnover (in which case the game is over and the offense 
loses). That second component can be useful if you want to shape rewards.

Model object methods:

the result method;
the initial_position method, which returns the initial position of the game;
the offensive_playbook_size method, which returns the number of offensive plays to choose from and the plays are 
	then numbered 0, 1, ..., model.offensive_playbook_size() - 1 (there is also a defensive_playbook_size method, 
	but you should not need to use that method);
the game_over method, which takes a position and determines if it is a terminal position;
the win method, which takes a terminal position and determines whether the offense won; and
the simulate method, which takes two arguments: 1) an offensive policy function – -- 
	a function that takes a position and returns the index of the offensive play to choose in that position; and 2)
	a positive integer for the number of games to simulate using that policy. The method returns the winning percentage 
	achieved over those games by the policy.

"""

import time
import random
import math


def q_learn(model, timeLimit): # object that models the Two-Minute Drill version of NFL strategy and a time limit in seconds
	
	# function that takes a position s and returns the key of the bucket it will be in
	def superstateConvert(s,a):
		coord1 = 0
		coord2 = 0
		
		# if model.game_over(s): ## if state is terminal, put in terrminal bucket
		# 	r = model.win(s)
		# 	coord1 = 3
		# 	coord2 = r
		# check how many times each bucket is changed
		if s[1] == 0:
			r1 = r1 = s[2]/(s[1] + .00001) # yards-to-first/downs left max = 10, partitions = 3
		else:
			r1 = s[2]/s[1] # yards-to-first/downs left max = 10, partitions = 3
		if s[3] == 0:
			r2 = s[0]/(s[3] + .00001) # not ideal, but works?? 
		else:
			r2 = s[0]/s[3] # yards-to-score/time left max = 80 partitions = 27

		# can choose to see more features beside just r1 and r2
		if r1 > 4: # 8
			coord1 = 2
		elif r1 > 2: # 2.5
			coord1 = 1
		else:
			coord1 = 0
		
		if r2 > 4.8: # # yards-to-score/time left max 4
			coord2 = 2
		elif r2 > 2.4: #2.4
			coord2 = 1
		else:
			coord2 = 0

		return (a, coord1, coord2)
	
	## trying to do buckets
	qsa = {} # key = (0,0), (0,1), etc ... value = tuple (q values and num times visited) ... will only have 9 key-value pairs
	for a in range(model.offensive_playbook_size()): # populate qsa
		qsa[a, 0,0] = [0, 0]
		qsa[a, 0,1] = [0, 0]
		qsa[a, 0,2] = [0, 0] 
		qsa[a, 1,0] = [0, 0]
		qsa[a, 1,1] = [0, 0]
		qsa[a, 1,2] = [0, 0]
		qsa[a, 2,0] = [0, 0]
		qsa[a, 2,1] = [0, 0]
		qsa[a, 2,2] = [0, 0]
		# qsa[a, 3,1] = [0, 0] # terminal winning states
		# qsa[a, 3,0] = [0, 0] # terminal losing states
	r1 = 0 # yards-to-first/downs left
	r2 = 0 # yards-to-score/time left
	episodeCounter = 0
	epsilon = .25
	learningRate = .1 # alpha, if alpha decreases too quick, will converge to a bad decision too quickly, will be good once it's giving consistent results !!! giving consistent, don't change!
	discountFactor = .995 # gamma, reward shaping (early on, not necessary)
	decay_rate = .99999 # figure out the final value and set decay rate so that final value is 1% of initial value
	#State 

	# LEARNNG TIME
	start = time.time()
	while  time.time() - start < (timeLimit * .999):
		s = model.initial_position() # s <- s0
		r = 0
		while not model.game_over(s): # make sure ticks < 25, and get 10 yards 
			## CHOOSE AN ACTION: use Epsilon Greedy to choose action A
			testNum = random.random() # gives value between 0 and 1
			if(testNum < epsilon):
				a = random.randint(0,model.offensive_playbook_size()-1) # choose action a (using epsilon greedy) from model.offensive_playbook_size()
			else: # find action that maximizes current Q
				maxQ = -math.inf
				maxAction = 0
				for a in range(model.offensive_playbook_size()):
					sPrime = model.result(s,a)[0]
					result = superstateConvert(s, a)
					if qsa[result][0] > maxQ:
						maxQ = qsa[result][0]
						maxAction = a
				a = maxAction
			
			# observe transition --> result result returns (resulting position tuple, some random other thing)
			sPrime = model.result(s,a)[0]
			learningRate = learningRate * decay_rate
			epsilon = epsilon * decay_rate
			#Compute Superstate:
			superS = superstateConvert(s,a)
			
			maxQ = -math.inf
			maxAction = 0
			for aPrime in range(model.offensive_playbook_size()):
				sPrimePrime = model.result(s,a)[0]
				result = superstateConvert(sPrime,aPrime)
				if qsa[result][0] > maxQ:
					maxQ = qsa[result][0]
					maxAction = aPrime
			aPrime = maxAction
			superSPrime = superstateConvert(sPrime,aPrime)

			#Update
			if model.game_over(sPrime):
				if model.win(sPrime):
					r = 1
				else:
					r = -1
			else:
				r = 0
			# else: # tiny bit of reward shaping -- add .1 if get a first down
			# 	if sPrime[1] == 4 and sPrime[2] != 80:
			# 		r = r + 0.1
			if model.game_over(sPrime):
				qsa[superS][0] = qsa[superS][0] + learningRate * (r  - qsa[superS][0]) 
			else:
				qsa[superS][0] = qsa[superS][0] + learningRate * (r + discountFactor * qsa[superSPrime][0] - qsa[superS][0])
			qsa[superS][1] = qsa[superS][1] + 1
			s = sPrime

		episodeCounter = episodeCounter + 1
	#print(episodeCounter)
	
	def retFunc(pos): # takes a non-terminal position in the game and returns the index of the selected offensive play
		s = pos
		maxQ = -math.inf
		maxAction = 0
		superS = 0
		for a in range(model.offensive_playbook_size()):
			sPrime = model.result(s,a)[0]
			result = superstateConvert(s, a)
			if qsa[result][0] > maxQ:
				maxQ = qsa[result][0]
				maxAction = a
		return maxAction
	# for i in qsa:
	# 	print(i, " : ", qsa[i])
	return retFunc