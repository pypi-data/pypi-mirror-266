import os
import glob
import arviz as az
import numpy as np
import pandas as pd
import re
import random

from aipys_analyse.simulation.Simulate import Simulate
from aipys_analyse.func.unPacking import MapSimMOI

from scipy import stats
RANDOM_SEED = 8927
rng = np.random.default_rng(RANDOM_SEED)

RANDOM_SEED = 8927
np.random.seed(RANDOM_SEED)

class runSimulation(Simulate):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dfTall, self.dfWide = self.dataReady()
        #self.dataHandle()
    
    def dataHandle(self):
        """
        dforig: 'sgRNA', 'count'
        dfQ2:'sgID', 'Q2_Reads'
        df_m:'sgID''count_sim'
        """
        count = 1 # make sure we get 3 replicates
        container = {}
        data_list = []
        while count <= 3:
            dforig ,dfQ1,dfQ2,df_m = self.simulation()
            #df = mapSgRNA(df1 = dforig, df2 = dfQ2)
            key_orig = "df"+str(count)+"_orig"
            key_active = "df"+str(count)
            key_M = "df"+str(count)+"_M"
            container[key_orig] = dforig
            container[key_active] = dfQ2
            container[key_M] = df_m
            data_list = data_list + [(key_active,[container[key_active]]),(key_orig,[container[key_orig]]),(key_M,[container[key_M]])]
            count += 1
        return  data_list   
    
    def dataReady(self):
        data_list = self.dataHandle()
        sampleId = MapSimMOI(data_list)
        df = pd.DataFrame(sampleId.df_map)
        df['Gene'] = [re.sub('_._.*','', sg) for sg in df.sgRNA.values]
        df.loc[df.sgRNA.str.contains('non'),'Gene'] = 'non'
        dfWide = df.copy()
        df = pd.melt(df,id_vars = ['Gene','sgRNA'], value_vars=['df1_orig','df2_orig','df3_orig',
                                                     'df1', 'df2', 'df3','df1_M','df2_M','df3_M'])
        df["log"] = np.log(df["value"].values+2)
        df["condition"] = 1
        df.loc[df.variable.str.contains('orig'),"condition"] = 0
        df.loc[df.variable.str.contains('M'),"condition"] = 2
        dftall = df.rename(columns = ({"variable":"class","value":"readCount","log":"logRcount","condition":"tag"}))
        mapping = {0: "Ht0", 1: "Ht1", 2: "M"}
        dftall["class"] = dftall["tag"].replace(mapping)
        return dftall, dfWide
            
