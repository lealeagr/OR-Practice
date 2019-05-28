from gurobipy import *
import Read_Data
import Static_Model

#nitems, planningHorizon, MJC, DPP, DAVG, HLC, MNC, CNT_WEIGHT, CNT_VALUE, REQ_WEIGHT, REQ_VALUE, MIN_WEIGHT, MIN_VALUE = \
nitems, planningHorizon, S, D, DAVG, h, s, w, v, weightREQ, valueREQ, minWeight, minValue = \
    Read_Data.read_Data ('setC-001.txt')

# creat periods and items to iterate through
periods = range(planningHorizon)
items = range(nitems)

m=Model("DJRP_model")
z={}
y={}
x={}
I={}
for t in periods:
    z[t]=m.addVar(vtype=GRB.BINARY, name= "Z_%s" % str(t))
    for i in items:
        y[i,t]= m.addVar(vtype=GRB.BINARY, name="Y_%s%s" % (str(i), str(t)))
        x[i,t]=m.addVar(vtype=GRB.CONTINUOUS, name="X_%s%s" %(str(i), str(t)), lb=0)
        I[i,t]=m.addVar(vtype=GRB.CONTINUOUS, name="I_%s%s" % (str(i), str(t)), lb=0)

obj=quicksum(S[t]*z[t] for t in periods)+quicksum(s[i,t]*y[i,t]+h[i]*I[i,t] for i in items for t in periods)
m.setObjective(obj, GRB.MINIMIZE)
m.update()  
for i in items:
    for t in periods:
        if t != 0:
            m.addConstr(I[i,t-1]+x[i,t]-I[i,t]== D[i,t])
        else:
            m.addConstr(x[i,t]-I[i,t] == D[i,t])
        
for i in items:
    for t in periods:
        m.addConstr(x[i,t]<=500000*y[i,t])    
        
for t in periods:
    m.addConstr(quicksum(y[i,t] for i in items)<=nitems*z[t])

#Minimum value for ordering
if valueREQ==1:
    for t in periods:
            m.addConstr(quicksum(x[i,t]*v[i] for i in items) >= minValue*z[t])

#Minimum weight for ordering
if weightREQ==1:
    for t in periods:
            m.addConstr(quicksum(x[i,t]*w[i] for i in items) >= minWeight*z[t])

#m.Params.TIME_LIMIT = 600
z,y,B= Static_Model.computeInitialSolution()
m.update()
m.optimize()
m.printAttr('X')

