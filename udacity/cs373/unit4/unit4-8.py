# ----------
# User Instructions:
# 
# Define a function, search() that takes no input
# and returns a list
# in the form of [optimal path length, x, y]. For
# the grid shown below, your function should output
# [11, 4, 5].
#
# If there is no valid path from the start point
# to the goal, your function should return the string
# 'fail'
# ----------

# Grid format:
#   0 = Navigable space
#   1 = Occupied space

grid = [[0, 0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0],
        [0, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 1, 0]]

init = [0, 0]
goal = [len(grid)-1, len(grid[0])-1] # Make sure that the goal definition stays in the function.

delta = [[-1, 0 ], # go up
        [ 0, -1], # go left
        [ 1, 0 ], # go down
        [ 0, 1 ]] # go right

delta_name = ['^', '<', 'v', '>']

cost = 1

grid = [[0, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0],
    [0, 0, 1, 1, 1, 0],
    [0, 0, 0, 0, 1, 0]]

init = [0,0] # odakle se krece

goal = [len(grid)-1, len(grid[0])-1] # Make sure that the goal definition stays in the function.

delta = [[-1, 0 ], # go up
         [ 0, -1], # go left
         [ 1, 0 ], # go down
         [ 0, 1 ]] # go right

delta_name = ['^', '<', 'v', '>']
cost = 1

def search():
    # ----------------------------------------
    # insert code here and make sure it returns the appropriate result
    # ----------------------------------------
    checkmark = [[0 for i in range(len(grid[0]))] for j in range(len(grid))]
    start = [0, init[0], init[1]]
    checkmark[start[1]][start[2]] = 1
    openlist=[]
    openlist.append(start)
    reached = False
    while (openlist):
        cur_item = openlist.pop(0)
        cur_pos = [cur_item[1],cur_item[2]]
        for i in range(len(delta)):
            cur_pos2 = [cur_pos[0]+delta[i][0],cur_pos[1]+delta[i][1]]
            if (cur_pos2[0] >= 0 and cur_pos2[0] < len(grid) and cur_pos2[1] >=0 and cur_pos2[1] < len(grid[0]) and not checkmark[cur_pos2[0]][cur_pos2[1]] and not grid[cur_pos2[0]][cur_pos2[1]]):
                checkmark[cur_pos2[0]][cur_pos2[1]]=1
                if (cur_pos2[0] == goal[0] and cur_pos2[1] == goal[1]):
                    reached = True
                    path = [cur_item[0]+cost,cur_pos2[0],cur_pos2[1]]
                    #path = cur_item[0]+cost
                    break
                openlist.append([cur_item[0]+cost,cur_pos2[0],cur_pos2[1]])
        openlist.sort()
        
    if not reached:
        path = 'fail'

    return path # you should RETURN your result

print( search() )
