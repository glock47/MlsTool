#!/usr/bin/python

from lib.Process_Data import Process_Data
from lib.Collect_Research_Data import Collect_Research_Data
from lib.Repository_Stats import Repository_Stats
from lib.System import System
from lib.TextModel import TextModel

from progressbar import ProgressBar
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import time
import re
import os
import ast
import sys
import requests


class Keyword_Stats ():
    def __init__ (self, keyword, count):
        self.keyword = keyword
        self.count = count

class SeCategory_Stats ():
    def __init__ (self, category, keywords):
        self.category = category
        self.keywords = keywords
        self.count = 0

    def is_match (self, keyword):
        if (keyword in self.keywords):
            return True
        else:
            return False

    def append_keyword (self, keyword, count):
        self.keywords.append (keyword)
        self.count += count

    def update (self, count):
        self.count += count

class CmmtLogs():
    def __init__ (self, message, fuzzy):
        self.message = message
        self.fuzzy = fuzzy       

class Collect_CmmtLogs(Collect_Research_Data):

    def __init__(self, repo_no, file_name='CmmtLogs_Stats'):
        super(Collect_CmmtLogs, self).__init__(file_name=file_name)
        
        self.Tm = TextModel ()
        self.keywords = self.load_keywords ()
        self.commits_num = 0
        self.repo_num  = 0
        self.repo_no   = repo_no
        self.file_path = ""
        self.max_cmmt_num = System.MAX_CMMT_NUM
        self.keywors_stats = {}
        
        self.secategory_stats = {}
        self.init_secategory ()

        self.exception = re.compile(r'^current$|^ctrl$|^design$|^designer$|^description$|^described$|^descriptive$|^desc$|^list$|^sure$|^flow$|^brace$|^able$|^action$|^back$|^open$|^read$|^the$|^char$|^site$|^tweak$|^print$|^printf$')
        
    def init_secategory (self):
        self.secategory_stats[0] = SeCategory_Stats ("Risky_resource_management", 
                                                     ['thread', 'concurrent', 'concurren', 'synch', 'deadlock', 'race', 'buffer', 'crash', 'stack', 'integer', 'overflow', 'Sensitive', 'Sprintf', 'underflow', 'signedness', 'length', 'overrun'])
        
        self.secategory_stats[1] = SeCategory_Stats ("Insecure_interaction_between_components", 
                                                     ['injection', 'blacklist', 'CSRF', 'Cross-Site', 'forger', 'Forgery', 'SQLI', 'exploit', 'XSRF', 'backdoor', 'insecure', 'threat', 'specialchar', 'penetration'])

        self.secategory_stats[2] = SeCategory_Stats ("Porous_defenses", 
                                                     ['leak', 'permission', 'OpenSSL', 'crypto', 'encryption', 'cipher', 'bcrypt', 'entropy', 'unauthenticated', 'weak', 'Exposure', 'expose', 'ciphers', 'wireguard', 'breakable'])

        self.secategory_stats[3] = SeCategory_Stats ("Other", [])

                                                     
    def is_filtered (self, word):
        return self.exception.match(word)
        
    def fuzz_match(self, message, threshhold):  
        fuzz_results = {}
        
        for word in message:
            if self.is_filtered(word):
                continue
            
            if word in self.keywords:
                #print ("[%s][100%]direct match" %word)
                fuzz_results[word] = 100
            else:
                result = process.extractOne(word, self.keywords, scorer=fuzz.ratio)
                #print ("[%s][%f]fuzz match" %(result[0], result[1]))
                if (result[1] >= threshhold):
                    fuzz_results[result[0]] = int (result[1])

        return fuzz_results

    def formalize_msg (self, message):
        message = str (message)
        if (message == ""):
            return None
        
        clean_text = self.Tm.clean_text (message)
        if (clean_text == ""):
            return None

        return self.Tm.subject(clean_text, 3)

    def is_processed (self, cmmt_stat_file):
        cmmt_stat_file = cmmt_stat_file + ".csv"
        return System.is_exist (cmmt_stat_file)

    def is_segfin (self, repo_num):
        if (self.repo_no == 0):
            return False
        
        if ((self.repo_num < self.repo_no) or (self.repo_num >= self.repo_no+1000)):
            return True

        return False  

    def is_continue (self, errcode):
        codes = [404, 500]
        if (errcode in codes):
            return False
        else:
            return True

    def get_issuetag (self, url, issue):
        url = url + "/issues/" + issue
        result = requests.get(url,
                              auth=("yawenlee", "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"),
                              headers={"Accept": "application/vnd.github.mercy-preview+json"})
        if (self.is_continue (result.status_code) == False):
            print("$$$%s: %s, URL: %s" % (result.status_code, result.reason, url))
            return None
        
        if (result.status_code != 200 and result.status_code != 422):
            print("%s: %s, URL: %s" % (result.status_code, result.reason, url))
            sleep(1200)
            return self.get_issuetag(url)     
        Labels = result.json()['labels']
        if len (Labels) == 0:
            return ""
        LabelName = Labels[0]['name']
        print ("Issue - ", issue, "'s labes -> ", LabelName)
                
    def _update_statistics(self, repo_item):
        start_time = time.time()

        if ((repo_item.languages_used < 2) or (len(repo_item.language_combinations) == 0)):
            return

        self.repo_num += 1
        if (self.is_segfin (self.repo_num)):
            return
        
        repo_id   = repo_item.id
        cmmt_file = System.cmmt_file (repo_id)
        if (System.is_exist(cmmt_file) == False):
            return

        cdf = pd.read_csv(cmmt_file)
        cmmt_stat_file = System.cmmt_stat_file (repo_id)
        if (self.is_processed (cmmt_stat_file)):
            if (cdf.shape[0] < self.max_cmmt_num):
                self.commits_num += cdf.shape[0]
            else:
                self.commits_num += self.max_cmmt_num
            return
                
        print ("[%u]%u start...commit num:%u" %(self.repo_num, repo_id, cdf.shape[0]))
        for index, row in cdf.iterrows():
            self.commits_num += 1

            Labels = ""
            if row['issue'] != ' ':
                Labels = self.get_issuetag (repo_item.url, row['issue'])

            message = row['message'] + " " + Labels #+ " " + row['content']
            message = self.formalize_msg (message)
            if (message == None):
                continue
            
            #print (message)
            fuzz_results = self.fuzz_match (message, 90)
            if fuzz_results:
                #print (fuzz_results)
                index = len (self.research_stats)
                self.research_stats[index] = CmmtLogs (message, fuzz_results)
            if (index >= self.max_cmmt_num):
                break

        #save by repository
        print ("[%u]%u -> accumulated commits: %u, timecost:%u s" %(self.repo_num, repo_id, self.commits_num, int(time.time()-start_time)) )
        self.save_data (cmmt_stat_file)
        self.research_stats = {}

    def get_keywords_stat (self):
        cmmt_stat_dir = os.walk("./Data/StatData/CmmtSet")
        keywors_stats = {}
        for path,dir_list,file_list in cmmt_stat_dir:  
            for file_name in file_list:
                stat_file = os.path.join(path, file_name)
                fsize = os.path.getsize(stat_file)/1024
                if (fsize == 0):
                    continue
                cdf = pd.read_csv(stat_file)
                for index, row in cdf.iterrows():
                    keywords = ast.literal_eval(row['fuzzy']).keys()
                    for key in keywords:
                        SeK = keywors_stats.get(key, None)
                        if (SeK == None):
                            keywors_stats[key] = 1
                        else:
                            keywors_stats[key] += 1
        
        keywors_stats = Process_Data.dictsort_value (keywors_stats, True)
        Index = 0
        for key, value in keywors_stats.items ():
            self.keywors_stats[Index] = Keyword_Stats (key, value)
            Index += 1
        super(Collect_CmmtLogs, self).save_data2(self.keywors_stats, "./Data/StatData/Keyword_Stats")


    def get_secategory (self):
        for index, keywors_stat in self.keywors_stats.items ():
            keyword = keywors_stat.keyword
            is_other = True
            for id, secate in self.secategory_stats.items ():
                if not secate.is_match (keyword):
                    continue
                secate.update (keywors_stat.count)
                is_other = False

            if (is_other):
                secate = self.secategory_stats[3]
                secate.append_keyword (keyword, keywors_stat.count)
                
        super(Collect_CmmtLogs, self).save_data2(self.secategory_stats, "./Data/StatData/SeCategory_Stats")
                    
        
    def _update(self):
        print ("Final: repo_num: %u -> accumulated commits: %u" %(self.repo_num, self.commits_num))
        print ("Start compute keyword stats...")
        self.get_keywords_stat ()
        print ("Start compute security categories...")
        self.get_secategory ()
        

    def load_keywords(self):
        df_keywords = pd.read_table(System.KEYWORD_FILE)
        df_keywords.columns = ['key']
        return df_keywords['key']

    def save_data(self, file_name=None):
        if (len(self.research_stats) == 0):
            return
        super(Collect_CmmtLogs, self).save_data2(self.research_stats, file_name)
         
    def _object_to_list(self, value):
        return super(Collect_CmmtLogs, self)._object_to_list(value)

    def _object_to_dict(self, value):
        return super(Collect_CmmtLogs, self)._object_to_dict(value)

    def _get_header(self, data):
        return super(Collect_CmmtLogs, self)._get_header(data)


