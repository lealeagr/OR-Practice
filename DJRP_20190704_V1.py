from gurobipy import *
import Read_Data
#import Static_Model
#import matplotlib.pyplot as plt
#import numpy as np
#import time
def DJRP_run (nitems, planningHorizon, S, D, DAVG, h, s, w, v, weightREQ, valueREQ, minWeight, minValue):
    #nitems, planningHorizon, MJC, DPP, DAVG, HLC, MNC, CNT_WEIGHT, CNT_VALUE, REQ_WEIGHT, REQ_VALUE, MIN_WEIGHT, MIN_VALUE = \
#    folder="_Daten_und_Loesungen\\A\\"
#    inst_set='setA-002'
#    instance=inst_set + '.txt'
#    nitems, planningHorizon, S, D, DAVG, h, s, w, v, weightREQ, valueREQ, minWeight, minValue = \
#        Read_Data.read_Data (folder+instance)
    
    # Periods and items to iterate through
    periods = range(planningHorizon)
    items = range(nitems)
    
    # Big M with sum over Demand
    M={}
    for i in items:
        M[i]= 0
        for t in periods:
            M[i]= M[i]+D[i,t]
            
    #Start modeling 
    m=Model("DJRP_model")
    m.Params.TIME_LIMIT = 500
    #Introduction of variables 
    z={}                                                                            #An order is placed at period t
    y={}                                                                            #An order is placed at period t for item i
    B={}                                                                            #Order quantity of item i arriving at the beginning of period t 
    I={}                                                                            #Level of inventory of item i at the end of period t 
    for t in periods:
        z[t]=m.addVar(vtype=GRB.BINARY, name= "Z_%s" % str(t))
        for i in items:
            y[i,t]= m.addVar(vtype=GRB.BINARY, name="Y_%s%s" % (str(i), str(t)))
            B[i,t]=m.addVar(vtype=GRB.INTEGER, name="B_%s%s" %(str(i), str(t)), lb=0)
            I[i,t]=m.addVar(vtype=GRB.INTEGER, name="I_%s%s" % (str(i), str(t)), lb=0)
    
    #Introduction of objective function 
    obj=quicksum(S[t]*z[t] for t in periods)+quicksum(s[i,t]*y[i,t]+h[i]*I[i,t] for i 
                in items for t in periods)
    m.setObjective(obj, GRB.MINIMIZE)
    m.update()  
    
    # Introduction of constraints
        #Constraint: inventory control 
    for i in items:
        for t in periods:
            if t != 0:
                m.addConstr(I[i,t-1]+B[i,t]-I[i,t]== D[i,t])
            else:
                m.addConstr(B[i,t]-I[i,t] == D[i,t])
                
       #Constraint: proof that item i has been ordered in the period t      
    for i in items:
        for t in periods:
            m.addConstr(B[i,t]<=M[i]*y[i,t])    
         
        #Constraint: proof that the number of orders in a period t is not bigger than the number of items    
    for t in periods:
        m.addConstr(quicksum(y[i,t] for i in items)<=nitems*z[t])
    
        #Constraint: minimum value for ordering
    if valueREQ==1:
        for t in periods:
                m.addConstr(quicksum(B[i,t]*v[i] for i in items) >= minValue*z[t])
    
        #Constraint: minimum weight for ordering
    if weightREQ==1:
        for t in periods:
                m.addConstr(quicksum(B[i,t]*w[i] for i in items) >= minWeight*z[t])
    
    
#    start = time.time()
    
    ##Initialization of DJRP with Static solution  
    #zs,ys,Bs= Static_Model.computeInitialSolution(instance)
    #for t in periods:
    #    z[t].start= zs[t]
    #for i in items:
    #    for t in periods:
    #        y[i,t].start = ys[i,t]
    
    #Show the moment our solution is better than INFORM        
    #m.params.BestObjStop=
    
    #Run optimization
    m.optimize()
    
    #Computational time 
#    run_time=m.runtime                                                              #Time for only DJRP
    m.update()
#    end = time.time()
#    comp_time=end-start                                                             #Time for static+DJRP

    #Write down solution 
    obj_Value=obj.getValue()
#    m.write("Model_%s.lp" %str(inst_set))
#    m.write("Solution_%s.sol" %str(inst_set))
    #m.printAttr('X')
    return m, z, y, B, I

#%% PLOT SOLUTIONS
#
##Selection of the item to plot
#item=3
#
##GRAPH 1
##Parameters of the graph
#x_axys = np.arange(planningHorizon)                                             
#width =  1                                                                      # the width of the bars
#fig, ax = plt.subplots(figsize=(10, 5))
##Inventory level of item at the end of period 
#I_item=np.zeros(planningHorizon)
#for a in periods:
#    I_item[a]=I[item,a].X  
#rects1 = ax.bar(x_axys + width/2, I_item, width, color = 'C2',
#                label='Inventory Level item %s' %str(item))
#
##Demand of item 
#D_item=np.zeros(planningHorizon)
#for a in periods:
#    D_item[a]=-D[item,a]
#rects2 = ax.bar(x_axys+width/2, D_item, width, 
#                label='Demand item %s' %str(item))
#                                                                       
##Order Quantity 
#Z_p=np.zeros(planningHorizon)
#for a in periods:
#    Z_p[a]=z[a].X
#    if Z_p[a]==1:
#        Z_p[a]=B[item,a].X        
#
#plt.step(x_axys,Z_p[x_axys], where='post',color='C1', linewidth=3, label='Quantity ordered item %s' %str(item))
#
## Text for title, label and axys
#ax.set_ylabel('Number of items')
#ax.set_xlabel('Periods')
#ax.set_title('Inventory control level of instance "%s"' %str(inst_set))
#x_legend = np.arange(planningHorizon+1)
#ax.set_xticks(x_legend)
#ax.set_xticklabels(x_legend)
#ax.legend()
#
##Text for bars 
#plt.margins(y=0.5)
#fig.tight_layout()
#for a in periods:
#    plt.text(x_axys[a] + 0.5, 1.1* I_item[a], '%i' % abs(I_item[a]), ha='center', va= 'bottom')
#    plt.text(x_axys[a] + 0.5, 1.1* D_item[a] , '%i' % -D_item[a], ha='center', va= 'top')
#plt.savefig('Inventory_control_%s_item %s.png' %(str(inst_set), str(item)))
#plt.show()
#
#
##GRAPH 2: Weight
#if weightREQ==1:
#    fig, ax = plt.subplots()
#    #Total order weight  
#    W_order=np.zeros(planningHorizon)
#    for a in periods: 
#        W_order[a]=sum(B[n,a].X*w[n] for n in items)
#    rects3 = ax.bar(x_axys + width/2, W_order, width, color = 'C0',
#                    label='Weight ordered')
#    
#    #Minimum order weight  
#    Min_w=np.zeros(planningHorizon)
#    for a in periods:
#        Min_w[a]=minWeight        
#    
#    plt.step(x_axys,Min_w[x_axys], where='post',color='C9', linewidth=3, label='Minimum weight')
#    
#    # Text for title, label and axys
#    ax.set_ylabel('Weight')
#    ax.set_xlabel('Periods')
#    ax.set_title('Total weight ordered in each period "%s"' %str(inst_set))
#    x_legend = np.arange(planningHorizon+1)
#    ax.set_xticks(x_legend)
#    ax.set_xticklabels(x_legend)
#    ax.legend()
#    
#    #Text for bars 
#    plt.margins(y=0.5)
#    fig.tight_layout()
#    for a in periods:
#        if W_order[a]>0:
#            plt.text(x_axys[a] + 0.5, 1.1* W_order[a], '%i' % abs(W_order[a]), ha='center', va= 'bottom')
#    plt.savefig('Weight_%s.png' %str(inst_set))
#    plt.show()
#    
#
##GRAPH 3: Value
#if valueREQ==1:
#    fig, ax = plt.subplots()
#    #Total order value 
#    V_order=np.zeros(planningHorizon)
#    for a in periods: 
#        V_order[a]=sum(B[n,a].X*v[n] for n in items)
#    rects3 = ax.bar(x_axys + width/2, V_order, width, color = 'C2',
#                    label='Value ordered')
#    
#    #Minimum order weight  
#    
#    Min_v=np.zeros(planningHorizon)
#    for a in periods:
#        Min_v[a]=minValue      
#    
#    plt.step(x_axys,Min_v[x_axys], where='post',color='C0', linewidth=3, label='Minimum Value')
#    
#    # Text for title, label and axys
#    ax.set_ylabel('Value')
#    ax.set_xlabel('Periods')
#    ax.set_title('Total value ordered in each period "%s"' %str(inst_set))
#    x_legend = np.arange(planningHorizon+1)
#    ax.set_xticks(x_legend)
#    ax.set_xticklabels(x_legend)
#    ax.legend()
#    
#    #Text for bars 
#    plt.margins(y=0.5)
#    fig.tight_layout()
#    for a in periods:
#        if V_order[a]>0:
#            plt.text(x_axys[a] + 0.5, 1.1* V_order[a], '%i' % abs(V_order[a]), ha='center', va= 'bottom')
#    plt.savefig('Value_%s.png' %str(inst_set))
#    plt.show()
#    
##GRAPH 4: Major cost, minor cost and holdings cost
#fig, ax = plt.subplots(figsize=(8, 4))
#
##Major ordering cost 
#MJC_order=np.zeros(planningHorizon)
#for a in periods:
#    if(z[a].X==1):
#        MJC_order[a]=S[a] 
#rects1 = ax.bar(x_axys + width/6, MJC_order, width/3, 
#                label='Major ordering cost')
#
##Minor ordering cost 
#MNC_order=np.zeros(planningHorizon)
#for a in periods:
#    if(z[a].X==1):
#        MNC_order[a]=sum(s[n,a]*y[n,a].X for n in items) 
#rects2 = ax.bar(x_axys + width/2, MNC_order, width/3, 
#                label='Minor ordering cost')
##Holding cost 
#HC_order=np.zeros(planningHorizon)
#for a in periods:
#    HC_order[a]= sum(h[n]*I[n,a].X for n in items)        
#rects3 = ax.bar(x_axys+ 5*width/6, HC_order, width/3, 
#                label='Holding cost')
#
## Add some text for labels, title and custom x-axis tick labels, etc.
#ax.set_ylabel('Cost')
#ax.set_xlabel('Periods')
#ax.set_title('MJC, MNC and HC %s' %str(inst_set))
#x_legend = np.arange(planningHorizon+1)
#ax.set_xticks(x_legend)
#ax.set_xticklabels(x_legend)
#ax.legend()
#fig.tight_layout()
#plt.savefig('Costs_%s.png' %str(inst_set))
#plt.show()
#
##GRAPH 5: Weight items
#if weightREQ==1:
#    fig, ax = plt.subplots(figsize=(20, 2))
#    x_2 = np.arange(nitems) 
#    weight=np.zeros(nitems)
#    for n in items:
#        weight[n]=w[n]
#    rects3 = ax.bar(x_2, weight, width/3, color='C9',
#                label='Weight')
#    
#    # Add some text for labels, title and custom x-axis tick labels, etc.
#    ax.set_ylabel('Weight')
#    ax.set_xlabel('Items')
#    ax.set_title('Weight each items "%s"' %str(inst_set))
#    x_legend = np.arange(nitems)
#    ax.set_xticks(x_legend)
#    ax.set_xticklabels(x_legend)
#    ax.legend() 
#    fig.tight_layout()
#    plt.savefig('Weight each items_%s.png' %str(inst_set))
#    plt.show()
#
##GRAPH 6: Value items
#if valueREQ==1:
#    fig, ax = plt.subplots(figsize=(20, 2))
#    x_2 = np.arange(nitems) 
#    value=np.zeros(nitems)
#    for n in items:
#        value[n]=v[n]
#    rects3 = ax.bar(x_2, value, width/3, color='C5',
#                label='Value')
#    
#    # Add some text for labels, title and custom x-axis tick labels, etc.
#    ax.set_ylabel('Value')
#    ax.set_xlabel('Items')
#    ax.set_title('Value each items "%s"' %str(inst_set))
#    x_legend = np.arange(nitems)
#    ax.set_xticks(x_legend)
#    ax.set_xticklabels(x_legend)
#    ax.legend() 
#    fig.tight_layout()
#    plt.savefig('Value each items_%s.png' %str(inst_set))
#plt.show()