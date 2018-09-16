colors = [['red', 'green', 'green', 'red' , 'red'],
          ['red', 'red', 'green', 'red', 'red'],
          ['red', 'red', 'green', 'green', 'red'],
          ['red', 'red', 'red', 'red', 'red']]

measurements = ['green', 'green', 'green' ,'green', 'green']


motions = [[0,0],[0,1],[1,0],[1,0],[0,1]]

sensor_right = 0.7

p_move = 0.8

def show(p):
    for i in range(len(p)):
        print p[i]
        
#DO NOT USE IMPORT
#ENTER CODE BELOW HERE
#ANY CODE ABOVE WILL CAUSE
#HOMEWORK TO BE GRADED
#INCORRECT

def sense(p, Z):
    q=[]
    for i in range(len(p)):
        q.append([])
        for j in range(len(p[i])):
            b = (colors[i][j]==Z)
            q[i].append(p[i][j]*(b*sensor_right+(1-b)*(1-sensor_right)))
    sq = 0
    for i in range(len(q)):
        sq += sum(q[i])
    for i in range(len(q)):
        for j in range(len(q[i])):
            q[i][j]/=sq
    return q

def move(p, U):
    q=[]
    for i in range(len(p)):
        q.append([])
        for j in range(len(p[i])):
            q[i].append((1-p_move)*p[i][j]+p_move*p[(i-U[0])%len(p)][(j-U[1])%len(p[i])])
    sq = 0
    for i in range(len(q)):
        sq += sum(q[i])
    for i in range(len(q)):
        for j in range(len(q[i])):
            q[i][j]/=sq
    return q

p = []
s = 1./20
for i in range(len(colors)):
    p.append([])
    for j in range(len(colors[i])):
        p[i].append(s)

#p = sense(p,measurements[0])
#p = move(p,motions[0])
#p = sense(p, measurements[1])
#print p
for k in range(len(motions)):
    p = move(p,motions[k])
    p = sense(p,measurements[k])


#Your probability array must be printed 
#with the following code.


show(p)




