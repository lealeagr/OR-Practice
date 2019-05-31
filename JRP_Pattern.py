from gurobipy import *
import Read_Data
import Static_Model

#nitems, planningHorizon, MJC, DPP, DAVG, HLC, MNC, CNT_WEIGHT, CNT_VALUE, REQ_WEIGHT, REQ_VALUE, MIN_WEIGHT, MIN_VALUE = \
nitems, planningHorizon, S, D, DAVG, h, s, w, v, weightREQ, valueREQ, minWeight, minValue = \
    Read_Data.read_Data ('setA-002.txt')
zs,ys,Bs= Static_Model.computeInitialSolution()

# creat periods and items to iterate through
periods = range(planningHorizon)
items = range(nitems)
M={}
for i in items:
    M[i]= 50000
    
warehouseC = 0
budgetC = 0
minC = 0
truckC = 0
#%% Creat patterns
import itertools
# Initialization
patterns = []
combinations = []
elements = [0]*nitems
patterns.append(tuple(elements))

#fill patterns with only initial solution pattern
for t in periods:
    if zs[t]==1:
        for i in items:
            if ys[i,t]==1:
                elements[i]=1
            else:
                elements[i]=0
#        if elements!=patterns[len(patterns)-1]:
        patterns.append(tuple(elements))
patterns=list(set(patterns))
        

## Fill patterns with one-item-pattern
#for i in items:
#    elements[i] = 1
#    combinations = set(itertools.permutations(tuple(elements), nitems))
#    for combination in combinations:
#        patterns.append(combination)

#%% Model variables
#import math
m = Model("JRP_pattern")

#pattern is chosen or not
x={}
for j in patterns:
    for t in periods:
        x[patterns.index(j),t]=m.addVar(vtype=GRB.BINARY)
#          , name="x_p"+str(j)+'_t'+ str(t))

#item i is part of pattern j (y[j,i] = 1) or not (y[j,i] = 0)
y={}
for j in patterns:
    for i in items:
        if j[i] == 1:
            y[patterns.index(j),i]=1
        else:
            y[patterns.index(j),i]=0            
B={}
l={}
for i in items:
    for t in periods:
        l[i,t] = m.addVar(vtype=GRB.INTEGER, name="l_i"+str(i)+'_t_'+str(t))
        B[i,t] = m.addVar(vtype=GRB.INTEGER, name="B_i"+str(i)+'_t_'+str(t))
        
#HC={}
#HC = m.addVar( vtype=GRB.CONTINUOUS, name = 'HC')
#
#m.addConstr(HC >= quicksum(0.5*(2*l[i,t]+D[i,t])*h[i] for i in items for t in periods))
#
#OC={}
#OC = m.addVar( vtype=GRB.CONTINUOUS, name = 'OC')
#
#m.addConstr(OC >= quicksum(quicksum(x[patterns.index(j),t]*(S+quicksum(s[i]*y[patterns.index(j),i] for i in items)) for j in patterns) for t in periods))
#%% Model constraints

## Every item should be at most one time in a pattern per period        
#for i in items:
#    for t in periods:
#        m.addConstr(quicksum(x[patterns.index(j),t]*y[patterns.index(j),i] for j in patterns) <= 1)
##        
##Only one pattern is ordered per period
#for t in periods:
#    m.addConstr(quicksum(x[patterns.index(j),t] for j in patterns)<=1)

## Every item is orderd ones
#for i in items:
#    m.addConstr(quicksum(x[patterns.index(j),t]*y[patterns.index(j),i] for j in patterns for t in periods) >= 1)

obj=quicksum(l[i,t]*h[i] for i in items for t in periods)+quicksum(quicksum(x[patterns.index(j),t]*(S[t]+quicksum(s[i,t]*y[patterns.index(j),i] for i in items)) for j in patterns) for t in periods)

m.setObjective(obj, GRB.MINIMIZE)


m.update()

# Satisfy demand and create stock
for i in items:
    for t in periods:
        if t != 0:
            m.addConstr(B[i,t]-D[i,t]+l[i,t-1] == l[i,t])
        else:
            m.addConstr(B[i,t]-D[i,t] == l[i,t])

# Linking of B and x
for i in items:
    for t in periods:
        m.addConstr(quicksum(M[i]*x[patterns.index(j),t]*y[patterns.index(j),i] for j in patterns) >= B[i,t])

solveIP = False
iter = 0
while True:
    iter += 1
    
    m.update()
    
    # Zur Kontrolle das Problem in Datei ausgeben.
    m.write("model_Basic.lp")
    
    # Gurobi loesen lassen.
    m.optimize()
    
    for v in m.getVars():
        if v.x == 1:
            print('%s %g' % (v.varName, v.x))
    


## Loesung ausgeben.
#if m.status == GRB.status.OPTIMAL:
#  for j in patterns:
#    for t in periods:
#        xfinal[patterns.index(j),t]=x[patterns.index(j),t].getValue()
#        if xfinal[patterns.index(j),t]==1.0:
#            print("Combination %d is ordered in Periode:%d" % (patterns.index(j),t))
#        else:
#            print("xxxx")
#else:
#  print('No solution')

    if solveIP:
        break


# Warehouse capacity is limited
if warehouseC==1:
    for t in periods:
        m.addConstr(quicksum(l[i,t] for i in items) <= H)

# Budget is limited for reordering
if budgetC==1:
    m.addConstr(quicksum(B[i,t] for i in items for t in periods) <= budget)

#Minimum weight for ordering
if weightREQ==1:
    for t in periods:
        for j in patterns:
            m.addConstr(quicksum(B[i,t]*w[i]*y[patterns.index(j),i] for i in items) >= minWeight*x[patterns.index(j),t])

#Minimum weight for ordering
if valueREQ==1:
    for t in periods:
        for j in patterns:
            m.addConstr(quicksum(B[i,t]*w[i]*y[patterns.index(j),i] for i in items) >= minValue*x[patterns.index(j),t])

# Miniumum number of one item that have to be orderd
if minC==1:
    for i in items:
        for t in periods:
            m.addConstr(quicksum(minOrder*x[patterns.index(j),t]*y[patterns.index(j),i] for j in patterns) <= B[i,t])
    
if truckC==1:
    for j in patterns:
        for t in periods:
            m.addConstr(x[patterns.index(j),t]*quicksum(B[i,t] for i in items) <= Truck)
            
obj=quicksum(l[i,t]*h[i] for i in items for t in periods)+quicksum(quicksum(x[patterns.index(j),t]*(S[t]+quicksum(s[i,t]*y[patterns.index(j),i] for i in items)) for j in patterns) for t in periods)

m.setObjective(obj, GRB.MINIMIZE)
m.update()

#%% Warmstart
#
#def computeInitialSolution(m, x, B, l, D):
#        
#    for i in items:
#        Quantity = 0
#        for t in periods:
#            Quantity = D[i,t]+Quantity
#        B[i,0] = round(Quantity/5)
#        B[i,4] = round(Quantity/5)
#        B[i,8] = round(Quantity/5)
#        B[i,12] = round(Quantity/5)
#        B[i,16] = round(Quantity/5)
#        
##    x[patterns[-1],0] = 1
##    x[patterns[-1],5] = 1
#    
#    m.update()
#    
#    # Check initial solution
#    print('\nINITIAL SOLUTION:')
#    for i in items:
#        print('Ordered amount of item '+str(i)+' is '+str(B[i,0]))
#        
#    print('Pattern:'+str(patterns[-1]))    
#    
#
#
#    return

#%% Start optimization

# Warmstart
#computeInitialSolution(m, x, B, l, D)
#for t in periods:
#    z[t].start= zs[t]
#for i in items:
#    for t in periods:
#        #B[i,t].start = Bs[i,t]
#        y[i,t].start = ys[i,t]

m.setParam('TimeLimit',600)
m.optimize()
m.write("model.lp")


#%% Lösung ausgeben

# Hier gibt er alle Variablen mit Wert 1 aus. Kann man noch schöner machen, wenn man das nur auf x bezieht
for v in m.getVars():
    if v.x == 1:
        print('%s %g' % (v.varName, v.x))

print('Obj: %g' % obj.getValue())


#printSolution (m,x,y,B,l)

#def printSolution (x,y,B,l):
#    
#    print('\nSOLUTION:')
#    print('TOTAL COSTS: %g' % m.objVal)
    
#    SolutionPatterns = range(len(x))
#    for p in SolutionPatterns:
#        if x[p] > 0.5:
#            print('Pattern'+str(x[p].x+'is used in period ))