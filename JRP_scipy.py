# -*- coding: utf-8 -*-
"""
Created on Fri May 24 15:58:37 2019

@author: Jacky
"""

import statistics

textfile = 'data//setB-010.txt'
txt = ""
with open(textfile) as fo:
    for rec in fo:
        txt = txt + rec         
#print(txt)
mjc = txt.split('#')


#DAVG

davg = {}
davg_temp = txt.split('#Syntax: DAVG-Keyword;Item-ID(String);MeanDemand(double)')[1].split('#Item holding costs per period')[0].split('DAVG;')
# print(davg_temp)
for item in davg_temp:
    temp = item.split(';')
    if(len(temp) == 1):
        continue;
#     davg[temp[0]]=[];
    davg[temp[0]] = temp[1]
#     print(temp[1])


#DPP

dpp = {}
dpp_temp = txt.split('#Syntax: DPP-Keyword;Item-ID(String);Demand1(int);Demand2;...')[1].split('#Item mean demand')[0].split('DPP;')
# print(dpp)
for item in dpp_temp:
    temp = item.split(';')
    if(len(temp) == 1):
        continue;
    dpp[temp[0]]=[];
    
    for i in range(len(temp)):
#     for time_period in temp:
        if( i == 0):
            continue;
        dpp[temp[0]].append(temp[i])
        
        
        
#Holding Costs

hc = {}
hc_temp = txt.split('#Syntax: HLC-Keyword;Item-ID(String);HoldingCostsPerUnit1(double);HoldingCostsPerUnit2(double);...')[1].split('#Item minor ordering costs per period')[0].split('HLC;')
# print(hc_temp)
for item in hc_temp:
    temp = item.split(';')
    if(len(temp) == 1):
        continue;
#     hc[temp[0]]=[];
    hc[temp[0]] = temp[1]
#     print(temp[1])
        
        
#Minor Ordering costs

#MNC

mnc = {}
mnc_temp = txt.split('#Syntax: MNC-Keyword;Item-ID(String);MinorOrderingCosts1(double);MinorOrderingCosts2(double);...')[1].split('#Item contribution')[0].split('MNC;')
# print(mnc)
for item in mnc_temp:
    temp = item.split(';')
    if(len(temp) == 1):
        continue;
    mnc[temp[0]]=[];
    
    for i in range(len(temp)):
#     for time_period in temp:
        if( i == 0):
            continue;
        mnc[temp[0]].append(temp[i])
        

#Item Contribution


icw = {}
icw_temp = txt.split('#Syntax: CNT-Keyword;Item-ID(String);Requirement-ID;Contribution(int)')[1].split('CNT;')
# print(ic_temp)
for item in icw_temp:
    temp = item.split(';Weight;')
    if(len(temp) == 1):
        continue;
#     ic[temp[0]]=[];
    icw[temp[0]] = temp[1]
#     print(temp[1])   

icv = {}
icv_temp = txt.split('#Syntax: CNT-Keyword;Item-ID(String);Requirement-ID;Contribution(int)')[1].split('CNT;')
# print(ic_temp)
for item in icv_temp:
    temp = item.split(';Value;')
    if(len(temp) == 1):
        continue;
#     ic[temp[0]]=[];
    icv[temp[0]] = temp[1]
#     print(temp[1])   
        
# dpp = list(map(float, dpp))
for i in range(len(dpp)):
    davg['Item.{}'.format(i)] = float(davg['Item.{}'.format(i)])
    hc['Item.{}'.format(i)] = float(hc['Item.{}'.format(i)])
    icw['Item.{}'.format(i)] = float(icw['Item.{}'.format(i)])
    icv['Item.{}'.format(i)] = float(icv['Item.{}'.format(i)])
    mnc['Item.{}'.format(i)][0] = float(mnc['Item.{}'.format(i)][0])
    for j in range(len(dpp['Item.1'])):
        dpp['Item.{}'.format(i)][j] = float(dpp['Item.{}'.format(i)][j])
             
# -*- coding: utf-8 -*-
"""
Created on Sun May  5 12:09:19 2019
@author: Jacky
"""

# http://apmonitor.com/che263/index.php/Main/PythonOptimization

import time
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import statistics

S = float(mjc[4].split('MJC')[2].split(';')[3])       # The major setup cost  
items = len(dpp)  # items
value = float(mjc[6].split('REQ')[3].split(';')[3])   # capacity of value would allow transpotation to deliveer
weight = float(mjc[6].split('REQ')[2].split(';')[3])   # capacity of weight would allow transpotation to deliver
print('textfile = {}'.format(textfile))
print('The number of item = {}'.format(items))
print('The major setup cost = {}'.format(S))
print('The capacity of value = {}'.format(value))
print('The capacity of weight = {}'.format(weight))

D = []
for i in range(items):
    D.append(statistics.mean(dpp['Item.{}'.format(i)]))
print('MeanDemand')
print(D)
h = []
h = [hc['Item.{}'.format(i)] for i in range(items)]
print('HoldingCosts')
print(len(h))
s = {}
s = [mnc['Item.{}'.format(i)][0] for i in range(items)]# determining how to fill out the missing data, one suggestion, give the average value
print('MinorOrderingCosts')
print(len(s))
w = []
w = [icw['Item.{}'.format(i)] for i in range(items)]# determining how to fill out the missing data, one suggestion, give the average value
print('Weight Contribution(int)')
print(len(w))
v = []
v = [icv['Item.{}'.format(i)] for i in range(items)]# determining how to fill out the missing data, one suggestion, give the average value
print('Value Contribution(int)')
print(len(v))
     


# Modelling optimization function
def objective(x):
    T = x[items]
    Total_holding_cost = sum((x[0:items] * T * D[0:items] * 0.5 * h[0:items]))
    Total_setup_cost = sum((1 / T) * (s[0:items] / x[0:items])) + (S / T)
    return Total_holding_cost + Total_setup_cost 

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
        
        
        
        

