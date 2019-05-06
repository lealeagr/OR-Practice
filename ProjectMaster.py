#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 09:14:27 2019

@author: LeaGrahn
"""
from gurobipy import *

# number of items  
nitems= 4

planningHorizon= 20
# list of items
items = range(nitems)
print(items)

import itertools
# Initialization
patterns = []
elements = []
combinations = []

# Fill patterns with one-item-patterns
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

import random
import math
#s=random.sample(range(0,30),len(patterns))
#S=7
#r_time=random.sample(range(0,30),len(patterns))
s = [random.randint(10, 30) for x in patterns]
h = [random.randint(100, 300) for i in items]
D = [random.randint(10, 30) for i in items]
S = 10
r_time = [random.randint(3, 5) for x in patterns]

print(s)
print(r_time)

m = Model("JRP_pattern")

#pattern is chosen or not
x={}
for j in patterns:
    x[patterns.index(j)]=m.addVar(vtype=GRB.BINARY, name="x_%s" % str(j))
    print(j)

#item j is part of pattern i (y[j,i] = 1) or not (y[j,i] = 0)
y={}
for j in items:
    for i in items:
        if i==patterns[j]:
            y[patterns.index(j),i]=1
            print (i)
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

#calculate T_j for each pattern
T={}
Divisor={}
for j in patterns:
    Divisor[patterns.index(j)] = 0
    for i in items:
        Divisor[patterns.index(j)]=(h[i]*D[i]*y[patterns.index(j),i]+Divisor[patterns.index(j)])
        print(Divisor[patterns.index(j)])
    
for j in patterns:
    T[patterns.index(j)] = 0
    for i in items:
        if Divisor[patterns.index(j)] != 0:
            T[patterns.index(j)]=((T[patterns.index(j)]+2*planningHorizon*(S+s[i]*y[patterns.index(j),i]))/Divisor[patterns.index(j)])
    T[patterns.index(j)] = math.sqrt(T[patterns.index(j)])

#only choose one pattern for each item      
for i in items:
    m.addConstr(quicksum(y[patterns.index(j),(i)]*x[patterns.index(j)] for j in patterns)<= 1)
    m.addConstr(quicksum(y[patterns.index(j),i]*x[patterns.index(j)] for j in patterns)>= 1)
    
    
obj=quicksum(x[patterns.index(j)]*(planningHorizon/T[patterns.index(j)]*(S+quicksum(s[i]*y[patterns.index(j),i] for i in items))+0.5*T[patterns.index(j)]*quicksum(h[i]*D[i] for i in items))for j in patterns)

m.setObjective(obj, GRB.MINIMIZE)

m.update()
m.optimize()
for v in m.getVars():
    print('%s %g' % (v.varName, v.x))

print('Obj: %g' % obj.getValue())
