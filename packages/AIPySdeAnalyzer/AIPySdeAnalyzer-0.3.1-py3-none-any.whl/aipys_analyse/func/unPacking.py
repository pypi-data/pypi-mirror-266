import numpy as np
import tqdm

class UploadData:
    def __init__(self, data):
        self.data = data
    
    def defineData(self, name):
        return {name: self.data}

class MapSimMOI:
    def __init__(self, data_list):
        self.data_dict = self.upload_data(data_list)
        self.df_map = self.mapsgRNA()
    
    def upload_data(self, data_list):
        data_dict = {}
        for name, data in data_list:
            uploader = UploadData(data)
            data_dict.update(uploader.defineData(name))
        return data_dict
    
    @staticmethod
    def unpack_sgRNA(df,colCount=1,colsgRNA=0):
        sgRNA = []
        for i in tqdm.tqdm(range(len(df))):
            count = df.loc[i,colCount]
            sgComb = df.loc[i,colsgRNA]
            for sg in sgComb.split("#"):
                sgRNA = sgRNA + [sg]*count
        return sgRNA
    
    def mapsgRNA(self):
        """_summary_
        dforig: 'sgRNA', 'count'
        dfQ2:'sgID', 'Q2_Reads'
        df_m:'sgID''count_sim'
        """
        df_map_dict_origSgRNA = {}
        sgRNA_uniqe = []
        sampleId = []
        # Unpack sgRNA from etch table
        for name, data in self.data_dict.items():
            if 'orig' in name:
                colCount='count'
                colsgRNA='sgRNA'
            elif 'M' in name:
                colCount='count_sim'
                colsgRNA='sgID'
            else:
                colCount='Q2_Reads'
                colsgRNA='sgID'
            sgRNA = self.unpack_sgRNA(data[0],colCount=colCount,colsgRNA=colsgRNA)
            df_map_dict_origSgRNA[name] = sgRNA # dictonery of list by table name
            sgRNA_uniqe = sgRNA_uniqe + sgRNA
            sampleId.append(name)
        sgRNA_uniqe = np.unique(np.array(sgRNA_uniqe))
        # Travers through the unique map and count sgRNA observed per table.
        df_map_dict = {"sgRNA":[]}
        for samp in sampleId:
            df_map_dict[samp] = [] 
        print("unpacking")
        for sg in tqdm.tqdm(sgRNA_uniqe):
            df_map_dict["sgRNA"].append(sg)
            for samp in sampleId:
                count = df_map_dict_origSgRNA[samp].count(sg)
                if count == 0:
                    count = 1
                df_map_dict[samp].append(count)
        return df_map_dict 