#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 09:14:27 2019
@author: LeaGrahn
"""
from gurobipy import *

#%% Main parameters
# number of items  
nitems= 10

# periods we are going to plan
planningHorizon= 10

# creat periods and items to iterate through
periods = range(planningHorizon)
items = range(nitems)

#%% Import Data
import pandas as pd
#import numpy as np
#from scipy.optimize import minimize

# reading file by pandas
pd_JRP = pd.read_excel("setA-002-withValue.xlsx")
#print(pd_JRP.columns)
pd_JRP.head()

D = {}
for i in items:
    for t in periods:
        D[i,t]= pd_JRP['DPP('+str(t+1)+')'][i]
#print('Demand')
#print(D)
h = {}
h = list(pd_JRP['Holding cost'])
#print('Holding cost')
#print(h)
s = {}
for i in items:
    for t in periods:
        s[i,t] = pd_JRP['Minor ordering cost P'+str(t+1)][i]# determining how to fill out the missing data, one suggestion, give the average value
#print('Minor ordering cost P1')
#print(s)
w = {}
w = list(pd_JRP['Weight Contribution(int)'])# determining how to fill out the missing data, one suggestion, give the average value
##print('Contribution(int)')
##print(w)
v = {}
v = list(pd_JRP['Value Contribution'])# determining how to fill out the missing data, one suggestion, give the average value
#print('Value Contribution(int)')
#print(v)
# h=[2,1,4]        # holding costs
# D=[10,20,5]      # Demand rate
# s=[2.0,3.0,4.0]  # The minor setup costs
#print(len(s))
#items = len(s)  # items
S=1820       # The major setup cost       
#value = 1000    # capacity of value would allow transpotation to deliveer
#weight = 150    # capacity of weight would allow transpotation to deliveer

#%% Creat patterns
import itertools
# Initialization
patterns = []
elements = []
combinations = []



# Fill patterns with one-item-patterns
demand={}
maxweight={}
maxvalue={}

for i in items:
    demand[i]=0
    for t in periods:
        demand[i]=D[i,t]+demand[i]
    maxweight[i]=demand[i]*w[i]
    maxvalue[i]=demand[i]*v[i]

for i in items:
    patterns.append(i)

# Elemens is needed for 
elements = patterns.copy()

# Add all other combinations itertools.combinations
for i in range(nitems+1):
    if i >= 2:
        combinations = list(itertools.combinations(elements,i))
        for combination in combinations:
            patterns.append(combination)


# %% Random parameters
import random
# Freeze rng
random.seed(42)
#
## minor cost per item???
#s = [random.randint(100, 300) for i in items]
## holding cost per item
#h = [random.randint(10, 30) for i in items]
## Demand per item per period
#D = {}
#for i in items:
#    for t in periods:
#        D[i,t]=random.randint(10,30)
## Major cost per order
#S = 1000

#include capacity constraint?
warehouseC=0
#w = [random.randint(1,50) for i in items]
H=100000000

#include budget constraint?
budgetC=0
budget=2000
costs = [random.randint(1,50) for i in items]

#include value constraint?
valueREQ=1
minValue=100

#include weight constraint?
weightREQ=1
minWeight=150


#include minimum order quantity?
minC=0
minOrder=planningHorizon
# Big M-constraint
M={}
for i in items:
    M[i] = 0
    for t in periods:
        M[i] = M[i]+D[i,t]

# Truck
truckC=0
Truck = 20*planningHorizon


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
for j in items:
    for i in items:
        if i==patterns[j]:
            y[patterns.index(j),i]=1
        else:
            y[patterns.index(j),i]=0
j=nitems
o=len(patterns)-1
while j <= o:
    for i in items:
        if i in patterns[j]:
           y[j,i]=1
        else:
            y[j,i]=0
    j=j+1
B={}
l={}
for i in items:
    for t in periods:
        l[i,t] = m.addVar(vtype=GRB.INTEGER, name="l_i"+str(i)+'_t_'+str(t))
        B[i,t] = m.addVar(vtype=GRB.INTEGER, name="B_i"+str(i)+'_t_'+str(t))
        
HC={}
HC = m.addVar( vtype=GRB.CONTINUOUS, name = 'HC')

m.addConstr(HC >= quicksum(0.5*(2*l[i,t]+D[i,t])*h[i] for i in items for t in periods))

OC={}
OC = m.addVar( vtype=GRB.CONTINUOUS, name = 'OC')

m.addConstr(OC >= quicksum(quicksum(x[patterns.index(j),t]*(S+quicksum(s[i,t]*y[patterns.index(j),i] for i in items)) for j in patterns) for t in periods))
#%% Model constraints

# Every item should be at most one time in a pattern per period        

for t in periods:
    m.addConstr(quicksum(x[patterns.index(j),t] for j in patterns) <= 1)

# Every item is orderd ones
for i in items:
    m.addConstr(quicksum(x[patterns.index(j),t]*y[patterns.index(j),i] for j in patterns for t in periods) >= 1)

# Satisfy demand and creat stock
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

# Warehouse capacity is limited
if warehouseC==1:
    for t in periods:
        m.addConstr(quicksum(l[i,t] for i in items) <= H)

# Budget is limited for reordering
if budgetC==1:
    m.addConstr(quicksum(B[i,t] for i in items for t in periods) <= budget)
    
#Minimum value for ordering
if valueREQ==1:
    for t in periods:
            m.addConstr(quicksum(B[i,t]*v[i] for i in items) >= minValue*quicksum(x[patterns.index(j),t] for j in patterns))

#Minimum weight for ordering
if weightREQ==1:
    for t in periods:
            m.addConstr(quicksum(B[i,t]*w[i] for i in items) >= minWeight*quicksum(x[patterns.index(j),t] for j in patterns))



# Miniumum number of one item that have to be orderd
if minC==1:
    for i in items:
        for t in periods:
            m.addConstr(quicksum(minOrder*x[patterns.index(j),t]*y[patterns.index(j),i] for j in patterns) <= B[i,t])
    
if truckC==1:
    for j in patterns:
        for t in periods:
            m.addConstr(x[patterns.index(j),t]*quicksum(B[i,t] for i in items) <= Truck)
            
obj=quicksum((l[i,t]+0.5*D[i,t])*h[i] for i in items for t in periods)+quicksum(quicksum(x[patterns.index(j),t]*(S+quicksum(s[i,t]*y[patterns.index(j),i] for i in items)) for j in patterns) for t in periods)

m.setObjective(obj, GRB.MINIMIZE)
m.update()

#%% Warmstart

def computeInitialSolution(m, x, B, l, D):
        
    for i in items:
        Quantity = 0
        for t in periods:
            Quantity = D[i,t]+Quantity
        B[i,0] = round(Quantity/5)
        B[i,4] = round(Quantity/5)
        B[i,8] = round(Quantity/5)
        B[i,12] = round(Quantity/5)
        B[i,16] = round(Quantity/5)
        
#    x[patterns[-1],0] = 1
#    x[patterns[-1],5] = 1
    
    m.update()
    
    # Check initial solution
    print('\nINITIAL SOLUTION:')
    for i in items:
        print('Ordered amount of item '+str(i)+' is '+str(B[i,0]))
        
    print('Pattern:'+str(patterns[-1]))    
    


    return

#%% Start optimization

# Warmstart
computeInitialSolution(m, x, B, l, D)
m.setParam('TimeLimit',120)
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
