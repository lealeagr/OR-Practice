# -*- coding: utf-8 -*-
"""
Created on Sun May  5 12:09:19 2019
@author: Jacky
"""
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import Read_Data
import time



def computeInitialSolution():
# http://apmonitor.com/che263/index.php/Main/PythonOptimization


#import statistics

#nitems, planningHorizon, MJC, DPP, DAVG, HLC, MNC, CNT_WEIGHT, CNT_VALUE, REQ_WEIGHT, REQ_VALUE, MIN_WEIGHT, MIN_VALUE = \
    nitems, planningHorizon, S, D, DAVG, h, s, w, v, weightREQ, valueREQ, minWeight, minValue = \
        Read_Data.read_Data ('setA-002.txt')
    
    items=range(nitems)
    periods=range(planningHorizon)
    
    Dm = {}
    ss={}
    Soc=S[0]
    for i in items:
        Dm[i]=0
        ss[i]=s[i,0]
        for t in periods:
            Dm[i] = Dm[i] + D[i,t]
        Dm[i]=Dm[i]/planningHorizon
    # Modelling optimization function
    
    def objective(x):
        T=x[nitems]
        Total_holding_cost=0
        Total_setup_cost=0
        for i in items:
                Total_holding_cost = Total_holding_cost +x[i] * T *0.5 * Dm[i] * h[i]
                Total_setup_cost = Total_setup_cost + (1 / T) * (ss[i] / x[i])
        Total_setup_cost = Total_setup_cost + (Soc / T)
        return Total_holding_cost + Total_setup_cost
        
    #def objective(x):
    #    return sum((x[0:items] * x[items] * Dm[0:items] * 0.5 * h[0:items]) \
    #              + (1 / x[items]) * (ss[0:items] / x[0:items])) + (1 / x[items]) * Soc
    
    def constraint_value(x):
        c_v=0
        T=x[nitems]
        if(valueREQ==1):
            for i in items:
                c_v=c_v + (x[i] * T * Dm[i] * v[i])
            c_v=c_v - minValue
        return c_v
    
    def constraint_weight(x):
        c_w=0
        T=x[nitems]
        if(weightREQ==1):
            for i in items:
                c_w=c_w + (x[i] * T * Dm[i] * w[i])
            c_w=c_w - minWeight
        return c_w
    
    # Define decision variables and initialize parameters
    x0 = np.zeros(nitems + 1) # the number of integer multipliers of T that a replensishment of item i will last
    for i in items:
        x0[i] = 1.0
    x0[items] = planningHorizon # T
    
    # show initial objective
    print('Initial Objective: ' + str(objective(x0)))
    
    # Constraints
    # Constraints
    bnds = []
    for i in range(nitems + 1):
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
    for i in items:
    #     print(str(x[i]))
        print('x{} = '.format(i) + str(x[i]))
    print('T = ' + str(x[nitems]))
    
    #Round values from the static solution    

    Ts=int(round(x[nitems]))
    k={}
    for i in items:
        k[i]=int(round(x[i]))
    TC_rounded=0    
    for i in items:
        TC_rounded=TC_rounded + k[i] * Ts * Dm[i] * 0.5 * h[i] + (1 / Ts) * (ss[i] / k[i])
    TC_rounded=(TC_rounded + Soc/Ts)*planningHorizon
             
    #Initialize z and y
    
    z={}
    y={}
    B={}
    I={}
    for i in items:
        for t in range(planningHorizon):
            z[t]=0
            y[i,t]=0
            B[i,t]=0
            
    #Conversion from the static to the dynamic
    
    for i in items:
        Dm[i]=round(Dm[i])
        for t in range(0,planningHorizon,Ts*k[i]):
            B[i,t] = Dm[i]*Ts*k[i]
            z[t]=1
            y[i,t]=1
            
    for i in items:
        for t in range(planningHorizon):
            if t!=0:
                I[i,t]=I[i,t-1]+B[i,t]-D[i,t]
            else:
                I[i,t]=B[i,t]-D[i,t]
                
    #Total cost with the dynamic objective function with the static solution. 
    newTC=0
            
    for t in range(planningHorizon):
        for i in items:
            newTC=newTC+s[i,t]*y[i,t]+h[i]*I[i,t]
        newTC=newTC+S[t]*z[t]


    print(TC_rounded)
    print(newTC)    
        
    return z,y,B
#    
z,y,B=computeInitialSolution()