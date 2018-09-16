# ----------
# User Instructions:
# 
# Implement the function optimum_policy2D() below.
#
# You are given a car in a grid with initial state
# init = [x-position, y-position, orientation]
# where x/y-position is its position in a given
# grid and orientation is 0-3 corresponding to 'up',
# 'left', 'down' or 'right'.
#
# Your task is to compute and return the car's optimal
# path to the position specified in `goal'; where
# the costs for each motion are as defined in `cost'.

# EXAMPLE INPUT:

# grid format:
#     0 = navigable space
#     1 = occupied space 
grid = [[1, 1, 1, 0, 0, 0],
        [1, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 1, 1],
        [1, 1, 1, 0, 1, 1]]
goal = [2, 0] # final position
init = [4, 3, 0] # first 2 elements are coordinates, third is direction
cost = [2, 1, 12] # the cost field has 3 values: right turn, no turn, left turn

# EXAMPLE OUTPUT:
# calling optimum_policy2D() should return the array
# 
# [[' ', ' ', ' ', 'R', '#', 'R'],
#  [' ', ' ', ' ', '#', ' ', '#'],
#  ['*', '#', '#', '#', '#', 'R'],
#  [' ', ' ', ' ', '#', ' ', ' '],
#  [' ', ' ', ' ', '#', ' ', ' ']]
#
# ----------


# there are four motion directions: up/left/down/right
# increasing the index in this array corresponds to
# a left turn. Decreasing is is a right turn.

forward = [[-1,  0], # go up
           [ 0, -1], # go left
           [ 1,  0], # go down
           [ 0,  1]] # do right
forward_name = ['up', 'left', 'down', 'right']

# the cost field has 3 values: right turn, no turn, left turn
action = [-1, 0, 1]
action_name = ['R', '#', 'L']


# ----------------------------------------
# modify code below
# ----------------------------------------

def optimum_policy2D():
    value = [[[999 for i in range(len(grid[0]))] for j in range(len(grid))] for k in range(len(forward))]
    policy = [[[-2 for i in range(len(grid[0]))] for j in range(len(grid))] for k in range(len(forward))]
    
    change = True
    while change:
        change = False
        for x in range(len(grid)):
            for y in range(len(grid[0])):
                for d in range(len(forward)): 
                    if (x == goal[0] and y == goal[1]):
                        if value[d][x][y] > 0:
                            value[d][x][y] = 0
                            policy[d][x][y] = -2
                            change = True
                    if ( grid[x][y] != 1 ):
                        for k in range(len(action)):
                            forward_ind = (d + action[k])%len(forward)
                            x2 = x+forward[forward_ind][0]
                            y2 = y+forward[forward_ind][1]
                            if (x2 >=0 and x2 <len(grid) and y2 >=0 and y2 < len(grid[0]) and grid[x2][y2]!=1):
                                if value[forward_ind][x2][y2]+cost[k] < value[d][x][y]:
                                    value[d][x][y] = value[forward_ind][x2][y2]+cost[k]
                                    policy[d][x][y] = action[k]
                                    change = True
    
    policy2D = [[' ' for i in range(len(grid[0]))] for j in range(len(grid))]
    pos = [init[0],init[1],init[2]]
    
    while ((pos[0] != goal[0] or pos[1]!= goal[1]) and policy[pos[2]][pos[0]][pos[1]] != -2):
        policy2D[pos[0]][pos[1]] = action_name[policy[pos[2]][pos[0]][pos[1]]+1]
        pos[2] += policy[pos[2]][pos[0]][pos[1]]
        pos[2] %= len(forward)
        pos[0] = pos[0]+forward[pos[2]][0]
        pos[1] = pos[1]+forward[pos[2]][1]
    
    if (pos[0] == goal[0] and pos[1] == goal[1]):
        policy2D[pos[0]][pos[1]]='*'
    return policy2D # Make sure your function returns the expected grid.
