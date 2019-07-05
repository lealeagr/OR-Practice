from gurobipy import *
import Read_Data
import numpy as np
import time
import DJRP_20190704_V1
#filenumbers = ['01','02','03','04','05','06','07','08','09','10']
filenumbers = ['01','02','03','04','05']
for number in filenumbers:
    folder= "_Daten_und_Loesungen\\E\\"
    filename = "setE-0"+number+".txt"
    #nitems, planningHorizon, MJC, DPP, DAVG, HLC, MNC, CNT_WEIGHT, CNT_VALUE, REQ_WEIGHT, REQ_VALUE, MIN_WEIGHT, MIN_VALUE = \
    nitems, planningHorizon, S, D, DAVG, h, s_minor, w, v, weightREQ, valueREQ, minWeight, minValue = \
        Read_Data.read_Data (folder+filename)
    
    # creat periods and items to iterate through
    periods = range(planningHorizon)
    items = range(nitems)
    maxIter = 100
    minAmountItems = np.linspace(0.85,0.99, num = maxIter)
    # Big M with sum over Demand
    M={}
    for i in items:
        M[i]= 0
        for t in periods:
            M[i]= M[i]+D[i,t]
            
    start = time.time()
    DJRP_Model, DJRP_z, DJRP_y, DJRP_B, DJRP_I = \
    DJRP_20190704_V1.DJRP_run (nitems, planningHorizon, S, D, DAVG, h, s_minor, w, v, weightREQ, valueREQ, minWeight, minValue)
    #%% Creat patterns
    # Creat subpatterns and initialize for every period a pattern that can order everything
    
    subpatterns = []
    for t in periods:
        djrppatterns = []
        subpatterns.append([])
        subpatterns[t].append([1]*nitems)
        for i in items:
            djrppatterns.append(int(DJRP_y[i,t].x))
        if djrppatterns not in subpatterns[t] and sum(djrppatterns)>0:
            subpatterns[t].append(djrppatterns)
            
    #%%
    c = {}   
    # Creat costs per pattern
    for t in periods:
        for s in range(len(subpatterns[t])):
            c[s,t] = S[t]
            for i in items:
                c[s,t] = c[s,t]+s_minor[i,t]*subpatterns[t][s][i]
            
        
    #%% Model variables
    m = Model("JRP Master Problem")
    m.setParam('TimeLimit',180000)
    m.params.outputFlag = 0
    
    #pattern is chosen or not
    x=[]
    for t in periods:
        x.append([])
        for s in subpatterns[t]:
            x[t].append(m.addVar(vtype = GRB.CONTINUOUS, lb = 0, ub = 1, name = "x_t"+str(t)+"_s_"+str(subpatterns[t].index(s))))
    
    #item i is part of pattern j (y[j,i] = 1) or not (y[j,i] = 0)
    a={}
    for t in periods:
        for s in range(len(subpatterns[t])):
            for i in items:
                if subpatterns[t][s][i] == 1:
                    a[i,s,t]=1
                else:
                    a[i,s,t]=0            
    B={}
    L={}
    for i in items:
        for t in periods:
            L[i,t] = m.addVar(vtype=GRB.CONTINUOUS, name="l_i"+str(i)+'_t_'+str(t))
            B[i,t] = m.addVar(vtype=GRB.CONTINUOUS, name="B_i"+str(i)+'_t_'+str(t))
            
    m.update()
    #%% Master model
    
    # Satisfy demand and creat stock
    for i in items:
        for t in periods:
            if t != 0:
                m.addConstr(B[i,t]-D[i,t]+L[i,t-1] == L[i,t])
            else:
                m.addConstr(B[i,t]-D[i,t] == L[i,t])
    
    # Just order one pattern
    cons_one_pattern = []
    for t in periods:
       cons_one_pattern.append( m.addConstr(quicksum(x[t][subpatterns[t].index(s)] for s in subpatterns[t]) <= 1 , name ="cons_one_pattern"+str(t)))
       
    # If you order something the pattern has to be chosen
    cons_pattern_chosen = []
    for i in items:
        for t in periods:
            cons_pattern_chosen.append([])
            cons_pattern_chosen[t].append(m.addConstr(B[i,t] <= quicksum(M[i]*x[t][subpatterns[t].index(s)]*a[i,subpatterns[t].index(s),t] for s in subpatterns[t]),name ="cons_pattern_chosen"+str(t)+str(i)))
    
    # Weight constraint
    cons_weight_REQ = []
    if weightREQ==1:
        for t in periods:
            cons_weight_REQ.append(m.addConstr(quicksum(B[i,t]*w[i] for i in items) >= minWeight*quicksum(x[t][subpatterns[t].index(s)] for s in subpatterns[t]), name = "cons_weight_REQ"+str(t)))
    
    cons_value_REQ = []
    # Value constraint
    if valueREQ==1:
        for t in periods:
            cons_value_REQ.append(m.addConstr(quicksum(B[i,t]*v[i] for i in items) >= minValue*quicksum(x[t][subpatterns[t].index(s)] for s in subpatterns[t]), name = "cons_value_REQ"+str(t)))
    m.update()
    #%% Get ready for loop
    #solveIP = False
    solveIP = [0]*planningHorizon
    iter = 0
    pricingModel = Model("JRP Pricing Problem")    
    pricingModel.setParam('TimeLimit',15)
    pricingModel.params.outputFlag = 0
    
    while True:
        iter += 1
        print("Iteration "+str(iter)+" wird gestartet!")
        
        # Creat costs per pattern
        c={}
        for t in periods:
            for s in range(len(subpatterns[t])):
                c[s,t] = S[t]
                for i in items:
                    c[s,t] = c[s,t]+s_minor[i,t]*subpatterns[t][s][i]
        a={}
        for t in periods:
            for s in range(len(subpatterns[t])):
                for i in items:
                    if subpatterns[t][s][i] == 1:
                        a[i,s,t]=1
                    else:
                        a[i,s,t]=0
                        
        obj = quicksum(h[i]*L[i,t] for i in items for t in periods)+quicksum(x[t][subpatterns[t].index(s)]*c[subpatterns[t].index(s),t] for t in periods for s in subpatterns[t])
        m.setObjective(obj, GRB.MINIMIZE)
        m.update()
        m.optimize()
    #    # Laufend Modelle rausschreiben
    #    m.write("model"+str(iter)+".lp")
        
        #Loesung ausgeben.
    #    if m.status == GRB.status.OPTIMAL:
    #        print('Loesung gefunden.')
    #    else:
    #      print('Keine Loesung gefunden.')
    
        # Stop if all are true
        if sum(solveIP) == planningHorizon:
          break
    
        #%% Pricing model
        # Solve for every period the pricing problem
        for t in periods:
            if solveIP[t] == True:
                continue
            # Das Modell ist leeren
            pricingModel.remove(pricingModel.getVars())
            pricingModel.remove(pricingModel.getConstrs())
            pricingModel.reset(0)
    
            # Pricing-Problem aufstellen.
            # Welches Item ist im Pattern enthalten in t
            P = {}
            for i in items:
                P[i] = pricingModel.addVar(vtype = GRB.BINARY, name = "P_i"+str(i)+"_t_"+str(t))
                    
            P_used = {}
            P_used = pricingModel.addVar(vtype = GRB.BINARY, name = "P_used_t"+str(t))
            
            pricingModel.update()
            
            # Constraints: Pattern must be bigger than minValue/minWeight
            if valueREQ==1:
                pricingModel.addConstr(quicksum(D[i,h]*v[i]*P[i] for i in items for h in periods) >= minValue, name="valueREQ"+str(t))
            if weightREQ==1:
                pricingModel.addConstr(quicksum(D[i,h]*w[i]*P[i] for i in items for h in periods) >= minWeight, name="weightREQ"+str(t))
            
            # Constraint: Linking P and p_used
            pricingModel.addConstr(quicksum(P[i] for i in items) <= nitems*P_used)
            
            # Focus on bigger patterns
            pricingModel.addConstr(quicksum(P[i] for i in items) >= minAmountItems[iter-1]*nitems)
            
            # modCost for Obj Function
            if valueREQ == 1:
                modCost = quicksum(M[i]*P[i]*cons_pattern_chosen[t][i].pi for i in items) \
                + cons_one_pattern[t].pi \
                + minValue*cons_value_REQ[t].pi \
                + minWeight*cons_weight_REQ[t].pi \
                + quicksum(s_minor[i,t]*P[i] for i in items)
                + S[t]*P_used
            else:
                modCost = quicksum(M[i]*P[i]*cons_pattern_chosen[t][i].pi for i in items) \
                + cons_one_pattern[t].pi \
                + minWeight*cons_weight_REQ[t].pi \
                + quicksum(s_minor[i,t]*P[i] for i in items) \
                + S[t]*P_used    
                
            # Pricing-IP loesen.
            pricingModel.setObjective(modCost, GRB.MINIMIZE)       
            pricingModel.update()
            pricingModel.optimize()
    
            
            #%% kleinste reduzierte Kosten prüfen und neue Pattern erstell+hinzufügen
            
            # Kleinste reduzierte Kosten sind negativ?
            if pricingModel.objval <- 0.001:
              pat = [ int(P[i].x) for i in items]
              if pat not in subpatterns[t]:
                  subpatterns[t].append(pat)
                  coeff_temp = []
                  for i in items:
                      coeff_temp.append(-M[i]*pat[i])
                  # Minus weil es auf die andere Seite kommt im Modell
                  columnPricing = Column (coeff_temp, cons_pattern_chosen[t])
                  columnPricing.addTerms(1, cons_one_pattern[t])
                  columnPricing.addTerms(-minWeight, cons_weight_REQ[t])
                  if valueREQ == 1:
                      columnPricing.addTerms(-minValue, cons_value_REQ[t])
                  x[t].append(m.addVar(vtype = GRB.CONTINUOUS, column=columnPricing, lb= 0.0, ub=1.0, name = "x_t"+str(t)+"_s_"+str(subpatterns[t].index(pat))))
            else:
              print("\nIn Periode "+str(t)+" kein neues Schnittmuster gefunden.")
              solveIP[t] = True
                   
        if sum(solveIP) == planningHorizon or iter >= maxIter:
            print("\n\nLoese ganzzahlig!")
            solveIP = [True]*planningHorizon
            m.params.outputFlag = 1
    #        x.__delitem__
            B.__delitem__
            L.__delitem__
            for t in periods:
                for s in range(len(subpatterns[t])):
                    x[t][s].vtype = GRB.BINARY
    #                x[t][s].start = 0
                for i in items:
                    B[i,t].vtype = GRB.INTEGER
                    L[i,t].vtype = GRB.INTEGER
                    B[i,t].start = int(DJRP_B[i,t].x)
    #                L[i,t].start = int(DJRP_I[i,t].x)
                    # TODO schöner machen
    #                if DJRP_B[i,t].x > 0:
    #                    x[t][1].start = 1
    
                    
            m.update()
        
    print('Zielfunktionswert: %f' % (m.getObjective().getValue()))
    #m.write(str(filename)+"_model.sol")
    end = time.time()
    result = end-start
    print(result)
    #%%
    f = open('_Daten_und_Loesungen\Ergebnisse_SetC\\5_Sekunden.txt', "a")
    f.write("\n"+filename+"\tObj:%f\tRunning time:%i\tDJRP_time:500\tmaxIter:100\tPattern_time:inf" % (m.getObjective().getValue(),result) )
    f.close()
    
    m.write("model_"+filename+".lp")