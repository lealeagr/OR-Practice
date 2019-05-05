# -*- coding: utf-8 -*-
"""
Created on Sun May  5 12:09:19 2019

@author: Jacky
"""

# http://apmonitor.com/che263/index.php/Main/PythonOptimization

import pandas as pd
import numpy as np
from scipy.optimize import minimize

##
pd_JRP = pd.read_excel("data\\setB-001.xlsx")
print(pd_JRP.columns)
pd_JRP.head()
##

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
print(len(s))
# h=[2,1,4]        # holding costs
# D=[10,20,5]      # Demand rate
# s=[2.0,3.0,4.0]  # The minor setup costs

items = len(s)  # items
S=14020.0       # The major setup cost       


# Modelling optimization function

# def objective(x):
#      return [x[0] * x[3] * D[0] * 0.5 * h[0] + (1 / x[3]) * (s[0] / x[0])
#             +x[1] * x[3] * D[1] * 0.5 * h[1] + (1 / x[3]) * (s[1] / x[1])
#             +x[2] * x[3] * D[2] * 0.5 * h[2] + (1 / x[3]) * (s[2] / x[2]) + (1 / x[3]) * S]
  
def objective(x):
     return sum((x[0:items] * x[items] * D[0:items] * 0.5 * h[0:items])
              + (1 / x[items]) * (s[0:items] / x[0:items])) + (1 / x[items]) * S

# def constraint1(x):
#     return x[0]+x[1]+x[2]+x[3]-4.0

# def constraint2(x):
#     sum_eq = 40.0
#     for i in range(4):
#         sum_eq = sum_eq - x[i]**2
#     return sum_eq


# Define decision variables and initialize parameters
n = items + 1
x0 = np.zeros(n) # the number of integer multipliers of T that a replensishment of item i will last
for i in range(items):
    x0[i] = 1.0
x0[items] = 20 # T

# show initial objective
print('Initial Objective: ' + str(objective(x0)))

# optimize
# b = (1.0,5.0)
# bnds = (b, b, b, b)
bnds = []
for i in range(items + 1):
    bnds.append([1.0,5.0])

# con1 = {'type': 'ineq', 'fun': constraint1} 
# con2 = {'type': 'eq', 'fun': constraint2}
# cons = ([con1])
# cons = ([con1,con2])

# SLSQP only solver can solve nonlinear 
solution = minimize(objective,x0,method='SLSQP',\
                    bounds=bnds)
x = solution.x

# show final objective
print('Final Objective: ' + str(objective(x)))

# print solution
print('Solution')
for i in range(items):
     print('x{} = '.format(i) + str(x[i]))
print('T = ' + str(x[items]))
