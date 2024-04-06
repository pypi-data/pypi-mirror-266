import re
import numpy as np
import pandas as pd
from sklearn import preprocessing
from tqdm import tqdm

class mapSgRNA:
    def __init__(self,df1,df2):
        '''
        :param df1: Q1 sample (original)
        :param df2: Q2 sample (active sort)
        '''
        self.df1 = df1
        self.df2 = df2
        self.mapping()
    
    def mapping(self):
        '''
        :param uniqueSgRNA: list of strings, unique sgRNA
        :return: mapping reads according to unique sgRNA
        '''
        sgRNAdic = {'Gene':[],'sgRNA':[],"reads_ctrl":[],"reads_activate":[]}
        uniqueSgRNA = np.unique(self.df2.sgID.values)
        progress = tqdm()
        print("preparing merging data")   
        for sgRNA in uniqueSgRNA:
            sgRNAdic['sgRNA'].append(sgRNA)
            # check for non targeting:
            if re.match("non-targeting.*", sgRNA) is None:
                sgRNAdic['Gene'].append(re.sub('_._.*','', sgRNA))
            else:
                sgRNAdic['Gene'].append("non")
            # reads ctrl
            if self.df1.loc[self.df1['sgRNA'] == sgRNA, 'count'].any():
                sgRNAdic['reads_ctrl'].append(self.df1.loc[self.df1['sgRNA'] == sgRNA, 'count'].values[0])
            else:
                sgRNAdic['reads_ctrl'].append(2)
            # reads active
            sgRNAdic['reads_activate'].append(self.df2.loc[self.df2['sgID'] == sgRNA, "Q2_Reads"].values[0])
            #print('{}'.format(sgRNA))
            progress.update()
        return sgRNAdic

    @staticmethod
    def dataFrameFinal(sgRNAdic):
        sgRNAdic['log2FoldChange'] = np.log(sgRNAdic['reads_activate']) - np.log(sgRNAdic['reads_ctrl'])
        sgRNAdic['scaleLog2FoldChange'] = preprocessing.scale(sgRNAdic['log2FoldChange'])
        df = pd.DataFrame(sgRNAdic)
        return df
    
    @staticmethod
    def Create_origVSactivDF(df_orig,df_active):
        '''
        Function takes data frame output from saveData module.One data frame is active sample and the other is output of the original (sgRNA and counts columns). Output count list acording to df_active sgRNA. 
        Example:
        df_active (Q1): 'df_0pymc_mu_100_num_4.csv'
        df_orig : 'Orig_2pymc_mu_100_num_4.csv'
        '''
        sgRNA = df_active.sgRNA.values
        count_orig = []
        for sg in sgRNA:
            if df_orig.loc[df_orig['sgRNA'] == sg, df_orig.columns[2]].any():
                count_orig.append(df_orig.loc[df_orig['sgRNA'] == sg,'count'].values[0])
            else:
                count_orig.append(2)
        return count_orig