# Example game HERE: http://oos.moxiecode.com/examples/tipover/
import sys 
import fileinput

sys.setrecursionlimit(2500) # increase recursion for test 11

def tipover(grid, x, y, gridX, gridY): # grid is array of grid, x, y are current location, gridx and gridy are grid coordinates
	if grid[x][y] == "*": # if solved
		return ""
	height = grid[x][y] # height of current stack, assume always on a stack at beginning

	movearr = [[x,y]] # array o
	connected_components = connectedComponent(grid, x, y, gridX, gridY, movearr) # will return a list of total connected possible move spaces
	#print(connected_components)
	for c in connected_components:
		cx = c[0]
		cy = c[1]
		#print(grid)
		if grid[cx][cy] == "*": # check if connected to the goal
			return ""
		if grid[cx][cy] != "." and isinstance(grid[cx][cy], int) and grid[cx][cy] > 1: # check if it's a stack bigger than 1 (tipable)
			possible_moves = possibleMoves(grid, cx, cy, gridX, gridY) # find all directions it can tip
			#print("possible moves for ", cx, ", ", cy, ": ", possible_moves)
			for move in possible_moves:
				copyBoard = grid.copy() # copy board 
				#print("copy board: ", copyBoard)
				height = grid[cx][cy] # reassign new height based on value of connected component
				for j in range(1, height + 1): # for the height of the stack
					copyBoard[cx + (move[0] * j)][cy + (move[1] * j)] = 1 # update copy to reflect move
				foundx = cx # maintain original cc coordinants
				foundy = cy
				copyBoard[cx][cy] = "." # replace tipped box with empyt space
				cx += move[0] * height # change coordinates to reflect tip move
				cy += move[1] * height
				#print(copyBoard)
				#print(cx)
				#print(cy)
				solution = tipover(copyBoard, cx, cy, gridX, gridY) #recursive call
				#print(solution)
				#print(type(solution))
				if solution is not None: # check if recusrive call returned null solution
					return  str(foundx) + " " + str(foundy) + " " + str(move[0]) + " " + str(move[1]) + '\n' + str(solution)
				else:
					#print("didn't find solution for :" , cx, ", ", cy)
					grid[foundx][foundy] = height # undoing board change
					for j in range(1, height+1): # for the height of the stack
						grid[foundx + (move[0] * j)][foundy + (move[1] * j)] = "." # update copy to reflect move
					cx = foundx # reassign back to most recent stack, undo tip
					cy = foundy
					#grid[foundx][foundy] = height
					#print("returning to original grid: ", grid)
					#break
		# else:
		# 	print(cx, ", ", cy, " is not a stack")
	return None

	
		

def possibleMoves(grid, currX, currY, gridX, gridY): # returns array of possible moves for a tippable stack
	dirArray=[[-1,0], [1,0], [0,1], [0,-1]] #array of al possible directions
	height = grid[currX][currY] # height of current stack
	#print("height: ", height)
	possible_moves = [] #currently empty moves list
	for i in dirArray: # finds all new possible directions
		hit = False # have to reassign in case it hit something previously
		newX = currX + (i[0] * height)
		newY = currY + (i[1] * height)
		if newX >= gridX or newX < 0: # first check that it doesn't go off grid
			continue
		elif newY >= gridY or newY < 0: # checking that it doens't go off grid
			continue
		#print("current x =", currX, " current y = ", currY)
		#print("new x =", newX, " new y = ", newY)
		for j in range(1,height+1): # for the height of the stack, check that it doesn't run into anyone
			if grid[currX + (i[0] * j)][currY + (i[1] * j)] != ".": # if hits someone
				#print("hit at", currX + (i[0] * j), currY + (i[1] * j))
				hit = True
				break ## FIGURE OUT WHAT GOES HERE, HOW, IF IT HITS, you can still other possible_moves (not getting to last two)
		if not hit:
			possible_moves.append(i) # if doesn't run into anyone, add to list of possible moves
	return possible_moves

# connected component = list of length two arrays, each = an x, y coordinant of reachable spots
def connectedComponent(grid, x, y, gridX, gridY, cc):
	for component in cc: # keep looping and adding spaces to list of connected components
		i = component[0]
		j = component[1]

		if i + 1 < gridX and not [i+1, j] in cc and grid[i+1][j] != ".": # for each, also check that the spot isn't already in the set, no need for redundancy
			cc.append([i+1, j])
		if i - 1 >= 0 and not [i-1, j] in cc and grid[i-1][j] != ".":
			cc.append([i-1, j])
		if j + 1 < gridY and not [i, j + 1] in cc and grid[i][j+1] != ".":
			cc.append([i, j+1])
		if j - 1 >= 0 and not [i, j-1] in cc and grid[i][j-1] != ".":
			cc.append([i, j-1])
	#print("cc for: ", x, " ", y ,": ", cc)
	return cc


### Read in Input ###

lines = sys.stdin.readlines()
first = lines[0].split()
height = int(first[0])
width = int(first[1])
#print(height, '\n')
#print(width, '\n')

# where the first is the row index (counting from 0 at the top) and the second is the column index (counting from 0 at the left);
second = lines[1].split()
x = int(second[0])
y = int(second[1])
#print(x, '\n')
#print(y, '\n')


grid = lines[2:]
newgrid = []

for line in grid: # input as ints
	line = line.strip()
	newrow = []
	for c in line:
		if c != "." and c != "*":
			c = int(c)
		newrow.append(c)
	newgrid.append(newrow)

#print(newgrid)
ans = tipover(newgrid, x, y, height, width)
if type(ans) == str:
	print(ans.rstrip()) # to send to stdout
