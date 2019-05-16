# -*- coding: utf-8 -*-
"""
Created on Tue May  7 17:05:23 2019

@author: ngomb
"""

from gurobipy import *
import pandas as pd
# number of items  
nitems= 1000

# periods we are going to plan
planningHorizon= 20

# creat periods and items to iterate through
periods = range(planningHorizon)
items = range(nitems)
#h=[2,1,4]                                      # holding costs
#D={(0,0):10, (1,0):23, (2,0):4, (0,1):20, (1,1):4, (2,1):9}                     # Demand rate
#s={(0,0):2, (1,0):1, (2,0):4, (0,1):3, (1,1):2, (2,1):3.5}           # The minor setup costs
#S=14020
# reading file by pandas
valueREQ=0
weightREQ=0
minWeight=150
minValue=1000

pd_JRP = pd.read_excel("setC-001_mod.xlsx")
#print(pd_JRP.columns)
pd_JRP.head()

D = {}
for i in items:
    for t in periods:
        D[i,t]= pd_JRP['Demand'+str(t+1)][i]
#print('Demand')
#print(D)
h = {}
h = list(pd_JRP['HoldingCostsPerUnit1(double)'])
#print('Holding cost')
#print(h)
s = {}
for i in items:
    for t in periods:
        s[i,t]= pd_JRP['MinorOrderingCosts'+str(t+1)][i]
#s = list(pd_JRP['Minor ordering cost P1'])# determining how to fill out the missing data, one suggestion, give the average value
#print('Minor ordering cost P1')
#print(s)
w = {}
w = list(pd_JRP['Weight Contribution(int)'])# determining how to fill out the missing data, one suggestion, give the average value
#print('Weight Contribution(int)')
#print(w)
v = {}
v = list(pd_JRP['Value Contribution(int)'])# determining how to fill out the missing data, one suggestion, give the average value
#print('Value Contribution(int)')
#print(v)
# h=[2,1,4]        # holding costs
# D=[10,20,5]      # Demand rate
# s=[2.0,3.0,4.0]  # The minor setup costs
#print(len(s))
#items = len(s)  # items
S=80980      # The major setup cost       
#value = 1000    # capacity of value would allow transpotation to deliveer
#weight = 150    # capacity of weight would allow transpotation to deliveer

# h=[2,1,4]        # holding costs
# D=[10,20,5]      # Demand rate
# s=[2.0,3.0,4.0]  # The minor setup costs
# define constant parameters
#items = len(s)  # items
#S=14020.0*0.01       # The major setup cost 
B=2000.0

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

obj=quicksum(S*z[t] for t in periods)+quicksum(s[i,t]*y[i,t]+h[i]*I[i,t] for i in items for t in periods)
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
        m.addConstr(x[i,t]<=1000000*y[i,t])       
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



m.optimize()
m.printAttr('X')
