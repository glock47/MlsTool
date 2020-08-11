#!/usr/bin/python

from lib.Process_Data import Process_Data
from lib.Collect_Research_Data import Collect_Research_Data
from lib.Repository_Stats import Repository_Stats
from lib.System import System
from lib.TextModel import TextModel
from datetime import datetime, timedelta
import time

import pandas as pd
from patsy import dmatrices
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

class PreNbrData():
    def __init__(self, repo_id, combo, pj_size, lg_num, age, commits_num, developer_num, se_num):
        self.repo_id  = repo_id
        self.combo    = combo
        self.pj_size  = pj_size    
        self.lg_num   = lg_num
        self.age      = age
        self.cmmt_num = commits_num
        self.dev_num  = developer_num
        self.se_num   = se_num

    def update (self, age, cmmt_num, dev_num, se_num):
        self.age      = age
        self.cmmt_num = cmmt_num
        self.dev_num  = dev_num
        self.se_num   = se_num


class NbrData():
    def __init__(self, repo_id, combo, combo_num, pj_size, lg_num, age, commits_num, developer_num, se_num):
        self.repo_id   = repo_id
        self.combo     = combo
        self.combo_num = combo_num
        self.pj_size   = pj_size    
        self.lg_num    = lg_num
        self.age       = age
        self.cmmt_num  = commits_num
        self.dev_num   = developer_num
        self.se_num    = se_num


class Collect_Nbr(Collect_Research_Data):

    stat_dir = "Data/StatData/"
    prenbr_stats   = stat_dir + "PreNbr_Stats.csv"
    topcombo_stats = stat_dir + "LangCombo_Stats.csv"

    def __init__(self, repo_no, file_name='PreNbr_Stats'):
        super(Collect_Nbr, self).__init__(file_name=file_name)
        self.repo_num = 0
        self.repo_no  = repo_no        
        self.max_cmmt_num = System.MAX_CMMT_NUM
        self.pre_nbr_stats = {}
        self.topcombo = []

    def is_prenbr_ready (self):
        return System.is_exist(Collect_Nbr.prenbr_stats)

    def get_cmmtinfo (self, NbrStats):
        repo_id = NbrStats.repo_id

        cmmt_file = System.cmmt_file (repo_id)
        if (System.is_exist(cmmt_file) == False):
            return

        #developers & commit_num
        cdf = pd.read_csv(cmmt_file)
        
        commits_num = 0
        if (cdf.shape[0] < self.max_cmmt_num):
            commits_num = cdf.shape[0]
        else:
            commits_num = self.max_cmmt_num

        developers = {}
        max_date   = "1999-01-01T13:44:12Z"
        min_date   = "2020-12-31T13:44:12Z"
        for index, row in cdf.iterrows():
            developers[row['author']] = 1
            date = row['date']
            if (date > max_date):
                max_date = date
            if (date < min_date):
                min_date = date
        developer_num = len (developers)

        max_time = datetime.strptime(max_date, '%Y-%m-%dT%H:%M:%SZ')
        min_time = datetime.strptime(min_date, '%Y-%m-%dT%H:%M:%SZ')
        age = (max_time - min_time).days
        
            
        #security bug num
        cmmt_stat_file = System.cmmt_stat_file (repo_id) + ".csv"
        if (System.is_exist(cmmt_stat_file) == False):
            return
        cdf = pd.read_csv(cmmt_stat_file)
        se_num = cdf.shape[0]

        NbrStats.update (age, commits_num, developer_num, se_num)
        self.pre_nbr_stats[repo_id] = NbrStats


    def is_segfin (self, repo_num):
        if (self.repo_no == 0):
            return False
        
        if ((self.repo_num < self.repo_no) or (self.repo_num >= self.repo_no+1000)):
            return True

        return False

    
    def _update_statistics(self, repo_item):
        start_time = time.time()
        if (self.is_prenbr_ready ()):
            return
        
        self.repo_num += 1      
        if ((repo_item.languages_used < 2) or (len(repo_item.language_combinations) == 0)):
            return
       
        repo_id = repo_item.id

        combo = "".join (repo_item.language_combinations)
        combo = combo.replace ("c++", "cpp")
        combo = combo.replace ("objective-c", "objectivec")
        combo = combo.replace (" ", "_")

        #basic
        NbrStats = PreNbrData (repo_id, combo, repo_item.size, repo_item.languages_used, 0, 0, 0, 0)     
        
        #commits
        self.get_cmmtinfo (NbrStats)

        print ("[%u]%u -> timecost:%u s" %(self.repo_num, repo_id, int(time.time()-start_time)) )

    def load_prenbr (self):
        cdf = pd.read_csv(Collect_Nbr.prenbr_stats)
        for index, row in cdf.iterrows():
            repo_id = row['repo_id']
            combo = row['combo']
            combo = combo.replace ("c++", "cpp")
            combo = combo.replace ("objective-c", "objectivec")
            self.pre_nbr_stats[repo_id] = PreNbrData (repo_id, combo, row['pj_size'], row['lg_num'], 
                                                      row['age'], row['cmmt_num'], row['dev_num'], row['se_num']) 

    def load_top_combo (self, top_num=30):
        cdf = pd.read_csv(Collect_Nbr.topcombo_stats)
        for index, row in cdf.iterrows():
            combo = row['combination']
            combo = combo.replace ("c++", "cpp")
            combo = combo.replace ("objective-c", "objectivec")
            combo = combo.replace (" ", "_")
            self.topcombo.append(combo)
            if (index >= top_num):
                break
        return

    def get_nbrdata (self, combo):
        for repo_id, predata in self.pre_nbr_stats.items():
            combo_num = 0
            if ((combo in predata.combo) or (predata.combo in combo)):
                combo_num = 1
            nbrdata = NbrData (predata.repo_id, predata.combo, combo_num, predata.pj_size, predata.lg_num, 
                               predata.age, predata.cmmt_num, predata.dev_num, predata.se_num)
            self.research_stats[repo_id] = nbrdata

    def compute_nbr (self, cdf):
        df_train = cdf
        print ("\r\n============================== training data ================================")
        print (df_train)
        
        #Setup the regression expression in patsy notation. 
        #We are telling patsy that BB_COUNT is our dependent variable 
        #and it depends on the regression variables: DAY, DAY_OF_WEEK, MONTH, HIGH_T, LOW_T and PRECIP
        expr = """se_num ~ css_html_javascript + c_cpp_shell + python_shell + javascript_typescript + html_python + html_ruby + css_html_javascript_python + javascript_python + css_html_javascript_shell + css_html_javascript_ruby + c_python + html_javascript_python + html_java + makefile_python + html_php + objectivec_ruby + go_shell + cpp_java_shell + javascript_php + css_html_javascript_php + objectivec_ruby_swift + javascript_shell + java_shell + c_cpp_python + html_javascript_java_c + c_cpp_cmake + css_javascript_php + java_javascript + css_html_javascript_python_shell + cpp_python + cpp_cmake + pj_size + lg_num + age + cmmt_num + dev_num"""
        
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
        df_train['AUX_OLS_DEP'] = df_train.apply(lambda x: ((x['se_num'] - x['BB_LAMBDA'])**2 - x['se_num']) / x['BB_LAMBDA'], axis=1)
        
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
        if (len(self.pre_nbr_stats) == 0):
            self.load_prenbr ()
        else:
            super(Collect_Nbr, self).save_data2(self.pre_nbr_stats, None)

        self.load_top_combo ()

        for combo in self.topcombo:
            print ("NMR --- %s " %combo)
            #print ("%s + " %combo, end="")
            self.get_nbrdata (combo)
            self.save_data(combo)

        index = 0
        for combo in self.topcombo:
            df = pd.read_csv(Collect_Nbr.stat_dir + combo+".csv", header=0, 
                             infer_datetime_format=True, parse_dates=[0], index_col=[0])
            if not index:
                cdf = df
            
            cdf[combo] = df['combo_num']
            index += 1
            
        self.compute_nbr (cdf)


    def save_data(self, file_name=None):
        if (len(self.research_stats) == 0):
            return
        super(Collect_Nbr, self).save_data2(self.research_stats, file_name)
        self.research_stats = {}
         
    def _object_to_list(self, value):
        return super(Collect_Nbr, self)._object_to_list(value)

    def _object_to_dict(self, value):
        return super(Collect_Nbr, self)._object_to_dict(value)

    def _get_header(self, data):
        return super(Collect_Nbr, self)._get_header(data)


