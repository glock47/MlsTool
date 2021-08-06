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
from time import sleep
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
        self.reEngine = None

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
    def __init__ (self, sha, message, catetory, matched):
        self.sha      = sha
        self.message  = message
        self.catetory = catetory
        self.matched  = matched

class Collect_CmmtLogs(Collect_Research_Data):

    def __init__(self, start_no=0, end_no=65535, re_use=False, file_name='CmmtLogs_Stats'):
        super(Collect_CmmtLogs, self).__init__(file_name=file_name)
        self.re_use = re_use 
        self.Tm = TextModel ()
        self.keywords = self.load_keywords ()
        self.commits_num = 0
        self.repo_num  = 0
        self.start_no  = start_no
        self.end_no    = end_no
        self.file_path = ""
        self.max_cmmt_num = System.MAX_CMMT_NUM
        self.keywors_stats = {}
        
        self.secategory_stats = {}
        self.init_secategory ()

    def init_secategory (self):
        
        self.secategory_stats[0] = SeCategory_Stats ("Risky_resource_management", 
                                                     ['path traversal', 'deadlock', 'data race', 'data leak', 'buffer overflow', 'stack overflow', 'memory overflow', 'Out memory',
                                                      'integer overflow', 'integer underflow', 'overrun', 'integer wraparound', 'uncontrolled format', 'Data loss', 'uninitialized memory',
                                                      'dangerous function', 'untrusted control', 'improper limitation', 'Improper Validation', 'integrity check', 'null pointer', 
                                                      'missing init', 'Incorrect Length', 'Forced Browsing', 'User-Controlled Key', 'Critical Resource', 'Exposed Dangerous',
                                                      'crashing length', 'Memory corruption', 'Memory leak', 'Double free', 'Use after free', 'Dangling pointers', 'overflow fix', 'boundary check'])
  
        self.secategory_stats[1] = SeCategory_Stats ("Insecure_interaction_between_components", 
                                                     ['sql injection', 'command injection', 'csrf', 'cross site', 'Request Forgery', 'sqli', 'xsrf', 'backdoor', 'Open Redirect',
                                                      'untrusted site', 'specialchar', 'unrestricted upload', 'unrestricted file', 'man in the middle', 'reflected xss', 'get based xss',
                                                      'Improper Neutralization', 'Dangerous Type', 'Cursor Injection', 'Dangling Database Cursor', 'Unintended Proxy', 'Unintended Intermediary',
                                                      'Argument Injection', 'Argument Modification', 'XSS Manipulation', 'Incomplete Blacklist', 'Origin Validation Error'])

        self.secategory_stats[2] = SeCategory_Stats ("Porous_defenses", 
                                                     ['missing authentication', 'missing authorization', 'hard coded credential', 'missing encryption', 'untrusted input', 'unnecessary privilege', 
                                                      'sensitive data', 'User-Controlled Key', 'Authorization Bypass',  'Hard coded Password', 'Hard coded Cryptographic', 'Key Management Error',
                                                      'incorrect authorization', 'incorrect permission', 'broken cryptographic', 'risky cryptographic', 'excessive authentication', 'privilege escalation',
                                                      'without a salt', 'unauthenticated', 'information disclosure', 'authentication bypass', 'cnc vulnerability', 'access control', 'cleartext storage',
                                                      'Least Privilege Violation', 'Insufficient Compartmentalization', 'Dropped Privileges', 'Assumed Immutable Data', 'Insufficient Entropy',
                                                      'Cryptographically Weak PRNG', 'adaptive chosen ciphertext', 'chosen ciphertext attack', 'Authorization Bypass'])

        self.secategory_stats[3] = SeCategory_Stats ("General", 
                                                    ['security', 'denial service', 'insecure', 'penetration', 'bypass security', 'crash', 'vulnerability fix'])

        if self.re_use == True:
            self.re_compile ()         
            self.re_match_test ()
        else:
            self.threshhold = 90
            self.fuzz_match_test ()

        TotalPhrase = 0
        for Id, Sec in self.secategory_stats.items():
            keywords = Sec.keywords
            print ("===> %s ---- key phrase number ---->%d" %(Sec.category, len(keywords)))
            TotalPhrase += len(keywords)
        print ("===> Whole ---- key phrase number ---->%d" %(TotalPhrase))

    def re_compile (self):
        for Id, Sec in self.secategory_stats.items():
            keywords = Sec.keywords
            regx = r''
            for key in keywords:
                if len (regx) != 0:
                    regx += '|'
                regx += key
            Sec.reEngine = re.compile (regx)
        
    def re_match_test (self):
        for Id, Sec in self.secategory_stats.items():
            reEngine = Sec.reEngine
            keywords = " ".join(Sec.keywords)
            clean_text = self.Tm.clean_text (keywords)
            Res = reEngine.match (keywords)
            print (clean_text, " ---> ", Res)
            if Res != None:
                print (Sec.category, " >>> match ---> success!!")
            else:
                print (Sec.category, " >>> match ---> fail!!")

    def re_match (self, message, threshhold=0):
        message = " ".join(message)
        for Id, Sec in self.secategory_stats.items():
            reEngine = Sec.reEngine
            Res = reEngine.match (message)
            if Res != None:
                #Sec.count += 1
                return Sec.category, Res.group(0)
        return None, None 

    def fuzz_match_test(self):
        print (self.secategory_stats)
        message = ['sqli',  'injection', 'commands', 'injection']
        Clf, Matched = self.fuzz_match (message, self.threshhold)
        if Clf == "Insecure_interaction_between_components":
            print ("\t fuzz_match_test -> %s pass!!!!" %message)
        else:
            print ("\t fuzz_match_test -> %s fail!!!!" %message)

        message = ['path',  'traversal', 'deadlock', 'race']
        Clf, Matched = self.fuzz_match (message, self.threshhold)
        if Clf == "Risky_resource_management":
            print ("\t fuzz_match_test -> %s pass!!!!" %message)
        else:
            print ("\t fuzz_match_test -> %s fail!!!!" %message)

        message = ['hard', 'coded', 'credential', 'encryption']
        Clf, Matched = self.fuzz_match (message, self.threshhold)
        if Clf == "Porous_defenses":
            print ("\t fuzz_match_test -> %s pass!!!!" %message)
        else:
            print ("\t fuzz_match_test -> %s fail!!!!" %message)

    
    def fuzz_match(self, message, threshhold=90):  
        fuzz_results = {}
        #print ("fuzz_match -> ", message)
        for Id, Sec in self.secategory_stats.items():
            keywords = Sec.keywords
            for str in keywords:
                key_len = len(str.split())
                msg_len = len (message)
                gram_meg = []
                
                if key_len < msg_len:
                    for i in range (0, len (message)):
                        end = i + key_len
                        if end > msg_len:
                            break
                        msg = " ".join(message[i:end])
                        gram_meg.append (msg)
                    #print ("\t[%s][%s] Try -> %s" %(Sec.category, str, gram_meg))
                    result = process.extractOne(str, gram_meg, scorer=fuzz.ratio)
                    #print ("\t\t1 => [%s][%f]fuzz match" %(result[0], result[1]))
                    if (result[1] >= threshhold):
                        fuzz_results[result[0]] = int (result[1])           
                        #Sec.count += 1
                        return Sec.category, fuzz_results 
                elif key_len == msg_len:
                    msg = " ".join(message)
                    gram_meg.append (msg)
                    result = process.extractOne(str, gram_meg, scorer=fuzz.ratio)
                    #print ("\t\t2 => [%s][%f]fuzz match" %(result[0], result[1]))
                    if (result[1] >= threshhold):
                        fuzz_results[result[0]] = int (result[1])
                        
                        #Sec.count += 1
                        return Sec.category, fuzz_results
                
                
        return None, None

    def formalize_msg (self, message):
        message = str (message)
        if (message == ""):
            return []
        
        clean_text = self.Tm.clean_text (message, 64)
        if (clean_text == ""):
            return []

        return self.Tm.subject(clean_text, 3)

    def is_processed (self, cmmt_stat_file):
        cmmt_stat_file = cmmt_stat_file + ".csv"
        return System.is_exist (cmmt_stat_file)

    def is_segfin (self, repo_num):
        if ((self.repo_num < self.start_no) or (self.repo_num >= self.end_no)):
            return True
        return False  
                
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
        if self.is_processed (cmmt_stat_file) or os.path.exists(cmmt_stat_file):
            if (cdf.shape[0] < self.max_cmmt_num):
                self.commits_num += cdf.shape[0]
            else:
                self.commits_num += self.max_cmmt_num
            print ("[%u]%u -> accumulated commits: %u, timecost:%u s" %(self.repo_num, repo_id, self.commits_num, int(time.time()-start_time)))
            return
                
        print ("[%u]%u start...commit num:%u" %(self.repo_num, repo_id, cdf.shape[0]))
        for index, row in cdf.iterrows():
            self.commits_num += 1

            message = str(row['message']) #+ " " + row['content']
            message = self.formalize_msg (message)
            if len (message) == 0:
                continue
                
            #print ("Message length -> %d " %len (message))
            Clf = None
            Matched = None
            if self.re_use == True:
                Clf, Matched = self.re_match (message)
            else:
                Clf, Matched = self.fuzz_match (message, self.threshhold)
            
            if Clf != None:
                #print (Clf)
                No = len (self.research_stats)
                self.research_stats[No] = CmmtLogs (row['sha'], message, Clf, Matched)
                print ("<%d>[%d/%d] retrieve cmmits -> %d" %(self.repo_num, index, cdf.shape[0], No))
            if (index >= self.max_cmmt_num):
                break

        #save by repository
        print ("[%u]%u -> accumulated commits: %u, timecost:%u s" %(self.repo_num, repo_id, self.commits_num, int(time.time()-start_time)) )
        self.save_data (cmmt_stat_file)
        self.research_stats = {}

    def ClassifySeC (self, Msg):
        message = self.formalize_msg (Msg)
        if (message == None):
            return "None"

        Clf, Matched = self.fuzz_match (message, 90)
        if Clf != None:
            for id, secate in self.secategory_stats.items ():
                if Clf == secate.category:
                    print ("@@@@ Match %s!!!" %secate.category)
                    return secate.category                  
            return "None"            
        else:
            #print ("@@@@ Match None!!!")
            return "None"
        
    def _update(self):
        print ("Final: repo_num: %u -> accumulated commits: %u" %(self.repo_num, self.commits_num))

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
                    Clf = row['catetory']
                    for Id, Sec in self.secategory_stats.items():
                        if Sec.category == Clf:
                            Sec.count += 1                 
        super(Collect_CmmtLogs, self).save_data2(self.secategory_stats, "./Data/StatData/SeCategory_Stats")
        

    def load_keywords(self):
        df_keywords = pd.read_table(System.KEYWORD_FILE)
        df_keywords.columns = ['key']
        return df_keywords['key']

    def save_data(self, file_name=None):
        if (len(self.research_stats) == 0):
            if file_name != None:
                Empty = "touch " + file_name
                os.system (Empty)
            return
        super(Collect_CmmtLogs, self).save_data2(self.research_stats, file_name)
         
    def _object_to_list(self, value):
        return super(Collect_CmmtLogs, self)._object_to_list(value)

    def _object_to_dict(self, value):
        return super(Collect_CmmtLogs, self)._object_to_dict(value)

    def _get_header(self, data):
        return super(Collect_CmmtLogs, self)._get_header(data)


class IssueItem():
    def __init__ (self, url, state, title, label, comments_url, diff_url, patch_url):
        self.url   = url
        self.state = state
        self.title = title
        self.label = label
        self.comments_url = comments_url
        self.diff_url = diff_url
        self.patch_url = patch_url
        
class Collect_Issues(Collect_Research_Data):
    def __init__(self, start_no=0, end_no=65535, file_name='CmmtLogs_Issues'):
        super(Collect_Issues, self).__init__(file_name=file_name)
        self.repo_num  = 0
        self.file_path = ""
        self.start_no  = start_no
        self.end_no    = end_no

    def is_segfin (self, repo_num):
        if ((self.repo_num < self.start_no) or (self.repo_num >= self.end_no)):
            return True
        return False

    def is_continue (self, errcode):
        codes = [410, 404, 500]
        if (errcode in codes):
            return False
        else:
            return True

    def get_issue (self, url, issue):
        url = url + "/issues/" + issue
        result = requests.get(url,
                              auth=("yawenlee", "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"),
                              headers={"Accept": "application/vnd.github.mercy-preview+json"})
        if (self.is_continue (result.status_code) == False):
            #print("$$$%s: %s, URL: %s" % (result.status_code, result.reason, url))
            return None
        
        if (result.status_code != 200 and result.status_code != 422):
            print("%s: %s, URL: %s" % (result.status_code, result.reason, url))
            sleep(1200)
            return self.get_issue(url, issue)     
        return result.json()
                
    def _update_statistics(self, repo_item):
        start_time = time.time()

        self.repo_num += 1
        if (self.is_segfin (self.repo_num)):
            return
        
        repo_id   = repo_item.id
        cmmt_file = System.cmmt_file (repo_id)
        if (System.is_exist(cmmt_file) == False):
            return

        cdf = pd.read_csv(cmmt_file)
        issue_file = System.issue_file (repo_id)
        if os.path.exists(issue_file):
            return
                
        print ("[%u]%u start...commit num:%u" %(self.repo_num, repo_id, cdf.shape[0]))
        ExIssues = {}
        for index, row in cdf.iterrows():
            IsNo = row['issue']
            if IsNo == ' ':
                continue

            if ExIssues.get (IsNo) != None:
                continue

            IssJson = self.get_issue (repo_item.url, IsNo)
            if IssJson == None:
                continue

            # get label
            Label   = ' '
            Labels = IssJson['labels']
            if len (Labels) != 0:
                Label = Labels[0]['name']

            # get pullrequest
            diff_url  = ' ' 
            patch_url = ' '
            if 'pull_request' in IssJson:
                pull_request = IssJson['pull_request']
                diff_url  = pull_request['diff_url']
                patch_url = pull_request['patch_url']
            
            No = len (self.research_stats)
            self.research_stats[No] = IssueItem (IssJson['url'], IssJson['state'], IssJson['title'], Label, 
                                                 IssJson['comments_url'], diff_url, patch_url)
            ExIssues [IsNo] = True
            print ("<%d>[%d/%d] %d -> retrieve %s" %(self.repo_num, index, cdf.shape[0], No, IssJson['url']))

        self.save_data (issue_file)
        self.research_stats = {}

    def _update(self):
        pass

    def save_data(self, file_name=None):
        if (len(self.research_stats) == 0):
            if file_name != None:
                Empty = "touch " + file_name
                os.system (Empty)
            return
        super(Collect_Issues, self).save_data2(self.research_stats, file_name)
                     
    def _object_to_list(self, value):
        return super(Collect_Issues, self)._object_to_list(value)
            
    def _object_to_dict(self, value):
        return super(Collect_Issues, self)._object_to_dict(value)
            
    def _get_header(self, data):
        return super(Collect_Issues, self)._get_header(data)
    
