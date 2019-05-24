def read_Data(filename):
    with open(filename,'r') as f:
        txt = f.read()
        txt = txt.split('\n')
        # Es wird eine leere Zeile am Ende erzeugt
        if txt[-1] == '':
            del txt[-1]
        lastRow = txt[-1].split(';')
        nitems = int(lastRow[1][5:])+1
        
        #%% Zeilenweise einlesen
        MJC = {}
        DPP = {}
        DAVG = {}
        HLC = {}
        MNC = {}
        CNT_WEIGHT = {}
        CNT_VALUE = {}
        REQ_WEIGHT = 0
        REQ_VALUE = 0
        MIN_WEIGHT = 10000
        MIN_VALUE = 10000
        for line in txt:
            if line[0] != '#':
                line = line.split(';')
                if line[0] == 'TIME':
                    planningHorizon = int(line [1])
                # Major ordering cost
                elif line[0] == 'MJC':
                    for t in range(planningHorizon):
                        MJC[t] = float(line[t+1])
                # Demand average
                elif line[0] == 'DAVG':
                    i = int(line[1][5:])
                    DAVG[i] = float(line[2])
                # Holding costs
                elif line[0] == 'HLC':
                    i = int(line[1][5:])
                    HLC[i] = float(line[2])
                # Item contribution
                elif line[0] == 'CNT':
                    i = int(line[1][5:])
                    if line [2] == 'Weight':
                        CNT_WEIGHT[i] = float(line[3])
                    elif line [2] == 'Value':
                        CNT_VALUE[i] = float(line[3])
                # Minor ordering cost 
                elif line[0] == 'MNC':
                    i = int(line[1][5:])
                    for t in range(planningHorizon):
                        if len(line) > t+2:
                            MNC[i,t] = float(line[t+2])
                        else:
                            MNC[i,t] = float(line[2])
                # Demand 
                elif line[0] == 'DPP':
                    i = int(line[1][5:])
                    for t in range(planningHorizon):
                        DPP[i,t] = float(line[t+2])
                # Requirements active?
                elif line[0] == 'REQ':
                    if line[1] == 'Weight':
                        REQ_WEIGHT = 1
                        MIN_WEIGHT = float(line [3])
                    elif line[1] == 'Value':
                        REQ_VALUE = 1
                        MIN_VALUE = float(line [3])
                
                        
        # inf ersetzen
        for i in range(nitems):
            for t in range(planningHorizon):
                if MNC[i,t] == float('inf'):
                    MNC[i,t] = 10000.0
        return nitems, planningHorizon, MJC, DPP, DAVG, HLC, MNC, CNT_WEIGHT, CNT_VALUE, REQ_WEIGHT, REQ_VALUE, MIN_WEIGHT, MIN_VALUE
