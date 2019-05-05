# -*- coding: utf-8 -*-
"""
Created on Sun May  5 12:09:19 2019

@author: Jacky
"""

# http://apmonitor.com/che263/index.php/Main/PythonOptimization

import pandas as pd
import numpy as np
from scipy.optimize import minimize

# reading file by pandas
pd_JRP = pd.read_excel("data//setB-001.xlsx")
print(pd_JRP.columns)
pd_JRP.head()

D = {}
D = list(pd_JRP['MeanDemand(double)'])
print('MeanDemand')
print(D)
h = {}
h = list(pd_JRP['HoldingCostsPerUnit1(double)'])
print('HoldingCostsPerUnit1')
print(h)
s = {}
s = list(pd_JRP['MinorOrderingCosts1'])# determining how to fill out the missing data, one suggestion, give the average value
print('MinorOrderingCosts1')
print(s)
w = {}
w = list(pd_JRP['Weight Contribution(int)'])# determining how to fill out the missing data, one suggestion, give the average value
print('Weight Contribution(int)')
print(w)
v = {}
v = list(pd_JRP['Value Contribution(int)'])# determining how to fill out the missing data, one suggestion, give the average value
print('Value Contribution(int)')
print(v)
# h=[2,1,4]        # holding costs
# D=[10,20,5]      # Demand rate
# s=[2.0,3.0,4.0]  # The minor setup costs
print(len(s))
items = len(s)  # items
S=14020.0       # The major setup cost       
value = 1000    # capacity of value would allow transpotation to deliveer
weight = 150    # capacity of weight would allow transpotation to deliveer

# Modelling optimization function
def objective(x):
     return sum((x[0:items] * x[items] * D[0:items] * 0.5 * h[0:items])
              + (1 / x[items]) * (s[0:items] / x[0:items])) + (1 / x[items]) * S

def constraint_value(x):
    return sum((x[0:items] * x[items] * D[0:items] * v[0:items])) - value

def constraint_weight(x):
    return sum((x[0:items] * x[items] * D[0:items] * w[0:items])) - weight

# Define decision variables and initialize parameters
x0 = np.zeros(items + 1) # the number of integer multipliers of T that a replensishment of item i will last
for i in range(items):
    x0[i] = 1.0
x0[items] = 20 # T

# show initial objective
print('Initial Objective: ' + str(objective(x0)))

# Constraints
bnds = []
for i in range(items + 1):
    bnds.append([1.0,5.0])

con1 = {'type': 'ineq', 'fun': constraint_value} # for instance of the formula, a - b >= 0
con2 = {'type': 'eq', 'fun': constraint_weight}
cons = ([con1, con2])

# SLSQP only solver can solve nonlinear 
solution = minimize(objective,x0,method='SLSQP',\
                    bounds=bnds, constraints=cons)

x = solution.x

# show final objective
print('Final Objective: ' + str(objective(x)))

# print solution
print('Solution')
for i in range(items):
#     print(str(x[i]))
    print('x{} = '.format(i) + str(x[i]))
print('T = ' + str(x[items]))
