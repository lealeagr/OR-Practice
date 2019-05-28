# -*- coding: utf-8 -*-
"""
Created on Sun May  5 12:09:19 2019
@author: Jacky
"""

# http://apmonitor.com/che263/index.php/Main/PythonOptimization

import pandas as pd
import numpy as np
from scipy.optimize import minimize
import Read_Data
import time
#import statistics

#nitems, planningHorizon, MJC, DPP, DAVG, HLC, MNC, CNT_WEIGHT, CNT_VALUE, REQ_WEIGHT, REQ_VALUE, MIN_WEIGHT, MIN_VALUE = \
items, planningHorizon, S, D, DAVG, h, s, w, v, weightREQ, valueREQ, minWeight, minValue = \
    Read_Data.read_Data ('setC-001.txt')

Dm = {}
ss={}
Soc=S[0]
for i in range(items):
    Dm[i]=0
    ss[i]=s[i,0]
    for t in range(planningHorizon):
        Dm[i] = Dm[i] + D[i,t]
    Dm[i]=Dm[i]/planningHorizon
# Modelling optimization function

def objective(x):
    T=x[items]
    Total_holding_cost=0
    Total_setup_cost=0
    for i in range(items):
            Total_holding_cost = Total_holding_cost +x[i] * T *0.5 * Dm[i] * h[i]
            Total_setup_cost = Total_setup_cost + (1 / T) * (ss[i] / x[i])
    Total_setup_cost = Total_setup_cost + (Soc / T)
    return Total_holding_cost + Total_setup_cost
    
#def objective(x):
#    return sum((x[0:items] * x[items] * Dm[0:items] * 0.5 * h[0:items]) \
#              + (1 / x[items]) * (ss[0:items] / x[0:items])) + (1 / x[items]) * Soc

def constraint_value(x):
    c_v=0
    T=x[items]
    if(valueREQ==1):
        for i in range(items):
            c_v=c_v + (x[i] * T * Dm[i] * v[i])
        c_v=c_v - minValue
    return c_v

def constraint_weight(x):
    c_w=0
    T=x[items]
    if(weightREQ==1):
        for i in range(items):
            c_w=c_w + (x[i] * T * Dm[i] * w[i])
        c_w=c_w - minWeight
    return c_w

# Define decision variables and initialize parameters
x0 = np.zeros(items + 1) # the number of integer multipliers of T that a replensishment of item i will last
for i in range(items):
    x0[i] = 1.0
x0[items] = 20 # T

# show initial objective
print('Initial Objective: ' + str(objective(x0)))

# Constraints
# Constraints
bnds = []
for i in range(items + 1):
    bnds.append([1.0,5.0])

con1 = {'type': 'ineq', 'fun': constraint_value} # for instance of the formula, a - b >= 0
con2 = {'type': 'ineq', 'fun': constraint_weight}
cons = ([con1, con2])
##
start = time.time()
# SLSQP only solver can solve nonlinear 
solution = minimize(objective,x0,method='SLSQP',\
                    bounds=bnds, constraints=cons)

x = solution.x

end = time.time()
print('conputational time = {}'.format(end - start))

# show final objective
print('Final Objective: ' + str(objective(x)))

# print solution
print('Solution')
for i in range(items):
#     print(str(x[i]))
    print('x{} = '.format(i) + str(x[i]))
print('T = ' + str(x[items]))
    
#%%
T=int(round(x[items]))
k={}
periods=20
for i in range(items):
    k[i]=int(round(x[i]))
def computeInitialSolution():
     
#Initialize z and y
    z={}
    y={}
    B={}
    for i in range(items):
        for t in range(periods):
            z[t]=0
            y[i,t]=0
            
#Conversion from the static to the dynamic
    for i in range(items):
        for t in range(0,20,T*k[i]):
            B[i,t] = Dm[i]*T*k[i]
            z[t]=1
            y[i,t]=1
            
#    for i in range(items):
#        for t in range(periods):
#            if t!=0:
#                I[i,t]=I[i,t-1]+B[i,t]-D[i]
#            else:
#                I[i,t]=B[i,t]-D[i]
    
    return z,y,B

