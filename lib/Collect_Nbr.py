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

    prenbr_stats   = "Data/StatData/PreNbr_Stats.csv"
    topcombo_stats = "Data/StatData/LangCombo_Stats.csv"

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
            self.pre_nbr_stats[repo_id] = PreNbrData (repo_id, row['combo'], row['pj_size'], row['lg_num'], 
                                                      row['age'], row['cmmt_num'], row['dev_num'], row['se_num']) 

    def load_top_combo (self, top_num=30):
        cdf = pd.read_csv(Collect_Nbr.topcombo_stats)
        for index, row in cdf.iterrows():
            combo = row['combination']
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

    def compute_nbr (self):
        pass
    
    def _update(self):
        if (len(self.pre_nbr_stats) == 0):
            self.load_prenbr ()
        else:
            super(Collect_Nbr, self).save_data2(self.pre_nbr_stats, None)

        self.load_top_combo ()

        for combo in self.topcombo:
            print ("NBR --- %s" %combo)
            self.get_nbrdata (combo)
            self.save_data(combo)
            
            self.compute_nbr (combo+".csv")


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


