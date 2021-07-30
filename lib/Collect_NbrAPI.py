#!/usr/bin/python

from lib.Process_Data import Process_Data
from lib.Collect_Research_Data import Collect_Research_Data
from lib.Repository_Stats import Repository_Stats
from lib.Collect_Nbr import PreNbrData

from lib.System import System
from lib.TextModel import TextModel
from datetime import datetime, timedelta
import time
import ast


import pandas as pd
from patsy import dmatrices
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt



class NbrData():
    def __init__(self, repo_id, apity, apity_num, pj_size, lg_num, age, commits_num, developer_num, se_num, se_rem_num, se_iibc_num, se_pd_num, se_other):
        self.repo_id   = repo_id
        self.apity     = apity
        self.apity_num = apity_num
        self.pj_size   = pj_size    
        self.lg_num    = lg_num
        self.age       = age
        self.cmmt_num  = commits_num
        self.dev_num   = developer_num
        self.se_num    = se_num
        self.se_rem_num  = se_rem_num
        self.se_iibc_num = se_iibc_num
        self.se_pd_num   = se_pd_num
        self.se_other    = se_other


class Collect_NbrAPI(Collect_Research_Data):

    stat_dir = "Data/StatData/"
    prenbr_stats   = stat_dir + "PreNbr_Stats.csv"
    apitype_stats  = stat_dir + "ApiSniffer.csv"
    
    def __init__(self, repo_no, file_name='NbrAPI_Stats'):
        super(Collect_NbrAPI, self).__init__(file_name=file_name)
        self.pre_nbr_stats = {}
        self.apitypes = {}
  
    def _update_statistics(self, repo_item):
        pass

    def load_apitypes (self):
        cdf = pd.read_csv(Collect_NbrAPI.apitype_stats)
        for index, row in cdf.iterrows():
            clfType = row['clfType']
            if clfType == None:
                continue
            self.apitypes[row['id']] = clfType
            apitypes = set (self.apitypes.values())
        return apitypes

    def load_prenbr (self):
        cdf = pd.read_csv(Collect_NbrAPI.prenbr_stats)
        for index, row in cdf.iterrows():
            repo_id = row['repo_id']
            combo = row['combo']
            combo = combo.replace ("c++", "cpp")
            combo = combo.replace ("objective-c", "objectivec")
            self.pre_nbr_stats[repo_id] = PreNbrData (repo_id, combo, row['pj_size'], row['lg_num'], 
                                                      row['age'], row['cmmt_num'], row['dev_num'], row['se_num'],
                                                      row['se_rem_num'], row['se_iibc_num'], row['se_pd_num'], row['se_other']) 

    def get_nbrdata (self, apity):
        for repo_id, predata in self.pre_nbr_stats.items():
            api_num = 0
            cur_apity = self.apitypes.get (repo_id)
            if cur_apity != None:
                if ((cur_apity in apity) or (apity in cur_apity)):
                    api_num = 1
            nbrdata = NbrData (predata.repo_id, cur_apity, api_num, predata.pj_size, predata.lg_num, 
                               predata.age, predata.cmmt_num, predata.dev_num, predata.se_num,
                               predata.se_rem_num, predata.se_iibc_num, predata.se_pd_num, predata.se_other)
            self.research_stats[repo_id] = nbrdata

    def compute_nbr (self, cdf, expr, r_val):
        df_train = cdf
        print ("\r\n============================== training data ================================")
        print (df_train)
              
        #Set up the X and y matrices for the training and testing data sets
        y_train, X_train = dmatrices(expr, df_train, return_type='dataframe')
        
        #Using the statsmodels GLM class, train the Poisson regression model on the training data set
        poisson_training_results = sm.GLM(y_train, X_train, family=sm.families.Poisson()).fit()
        
        #print out the training summary
        print ("\r\n============================== Poisson result ================================")
        print(poisson_training_results.summary())
        
        #print out the fitted rate vector
        print(poisson_training_results.mu)
        
        #Add the λ vector as a new column called 'BB_LAMBDA' to the Data Frame of the training data set
        df_train['BB_LAMBDA'] = poisson_training_results.mu
        
        #add a derived column called 'AUX_OLS_DEP' to the pandas Data Frame. This new column will store the values of the dependent variable of the OLS regression
        df_train['AUX_OLS_DEP'] = df_train.apply(lambda x: ((x[r_val] - x['BB_LAMBDA'])**2 - x[r_val]) / x['BB_LAMBDA'], axis=1)
        
        #use patsy to form the model specification for the OLSR
        ols_expr = """AUX_OLS_DEP ~ BB_LAMBDA - 1"""
        
        #Configure and fit the OLSR model
        aux_olsr_results = smf.ols(ols_expr, df_train).fit()
        
        #Print the regression params
        print(aux_olsr_results.params)
        
        #train the NB2 model on the training data set
        nb2_training_results = sm.GLM(y_train, X_train,family=sm.families.NegativeBinomial(alpha=aux_olsr_results.params[0])).fit()
        
        #print the training summary
        print ("\r\n============================== NB2 result ================================")
        print(nb2_training_results.summary())
        
    
    def _update(self):
        
        self.load_prenbr ()
        apitypes = self.load_apitypes ()
        print ("@@@@@@@@@@ apitypes => ", apitypes)

        for apity in apitypes:
            self.get_nbrdata (apity)
            self.save_data(apity)

        index = 0
        for apity in apitypes:
            df = pd.read_csv(Collect_NbrAPI.stat_dir + apity +".csv", header=0, 
                             infer_datetime_format=True, parse_dates=[0], index_col=[0])
            if not index:
                cdf = df
            
            cdf[apity] = df['apity_num']
            index += 1
        
        #Setup the regression expression in patsy notation. 
        #We are telling patsy that se_num is our dependent variable 
        #and it depends on the regression variables: combinations .... project variables

        print ("==================================== secutiry vulnerabilities ====================================")
        expr = """se_num ~ FFI + FFI_IMI + FFI_EBD + FFI_IMI_EBD + IMI + IMI_EBD + EBD + HIT + pj_size + lg_num + age + cmmt_num + dev_num"""
        self.compute_nbr (cdf, expr, "se_num")
        print ("==================================== secutiry vulnerabilities ====================================")
        
        print ("==================================== Risky_resource_management ====================================")
        expr = """se_rem_num ~ FFI + FFI_IMI + FFI_EBD + FFI_IMI_EBD + IMI + IMI_EBD + EBD + HIT + pj_size + lg_num + age + cmmt_num + dev_num"""
        self.compute_nbr (cdf, expr, "se_rem_num")
        print ("==================================== Risky_resource_management ====================================")

        print ("==================================== Insecure_interaction_between_components ====================================")
        expr = """se_iibc_num ~ FFI + FFI_IMI + FFI_EBD + FFI_IMI_EBD + IMI + IMI_EBD + EBD + HIT + pj_size + lg_num + age + cmmt_num + dev_num"""
        self.compute_nbr (cdf, expr, "se_iibc_num")
        print ("==================================== Insecure_interaction_between_components ====================================")
       
        print ("==================================== Porous_defenses ====================================")
        expr = """se_pd_num ~ FFI + FFI_IMI + FFI_EBD + FFI_IMI_EBD + IMI + IMI_EBD + EBD + HIT + pj_size + lg_num + age + cmmt_num + dev_num"""
        self.compute_nbr (cdf, expr, "se_pd_num")
        print ("==================================== Porous_defenses ====================================")

    def save_data(self, file_name=None):
        if (len(self.research_stats) == 0):
            return
        super(Collect_NbrAPI, self).save_data2(self.research_stats, file_name)
        self.research_stats = {}
         
    def _object_to_list(self, value):
        return super(Collect_NbrAPI, self)._object_to_list(value)

    def _object_to_dict(self, value):
        return super(Collect_NbrAPI, self)._object_to_dict(value)

    def _get_header(self, data):
        return super(Collect_NbrAPI, self)._get_header(data)


