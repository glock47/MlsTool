
import os
import sys
import csv
from time import sleep
import pandas as pd
import random
import requests
from lib.System import System
from lib.Collect_CmmtLogs import Collect_CmmtLogs

class ApiInfo ():
    def __init__(self, Id, Langs, ApiType):
        self.Id = Id
        self.Langs = Langs
        self.ApiType = ApiType 

class Sample():

    LANGINTR_SET  = ["FFI", "FFI_EBD", "FFI_IMI", "FFI_IMI_EBD", "IMI", "IMI_EBD"]
    LANGCOMBO_SET = [["python", "shell"], ["html", "java"], ["go", "shell"], ["objective-c", "ruby"], ["css", "html", "javascript", "shell"], 
                     ["css", "html", "javascript", "python"], ["java", "shell"], ["javascript", "shell"], ["c", "c++", "python"], 
                     ["c", "python"], ["c", "c++", "python", "shell"], ["html", "javascript", "shell"], ["javascript", "php"]]

    def __init__(self, SmpNum=50, CmmtNum=500):
        self.SmpNum   = SmpNum
        self.CmmtNum  = CmmtNum
        self.Samples  = []
        
        self.RepoList = []
        self.GetRepoList()

        self.ApiInfo  = {}
        self.GetApiInfo ()

        System.mkdir('Data/StatData/Samples') 

    def GetApiInfo (self):
        AiPath = "Data/StatData/ApiSniffer.csv"
        df = pd.read_csv(AiPath)
        for index, row in df.iterrows():  
            Ai = ApiInfo (row['id'], row['languages'], row['clfType'])
            self.ApiInfo[Ai.Id] = Ai
    
    def GetRepoList (self):
        RepoPath = "Data/StatData/Repository_Stats.csv"
        df = pd.read_csv(RepoPath)
        for index, row in df.iterrows():  
            repo = {}
            repo['id']  = row['id']
            repo['url'] = row['url']
            cmmt_stat_file = System.cmmt_stat_file (repo['id']) + '.csv'
            if System.is_exist (cmmt_stat_file) == False:
                continue
            self.RepoList.append (repo)
        print ("@@@@@ Get repository number: %d" %len (self.RepoList))

    def GetLangSelt (self, Langs):
        LangSet = []
        for Lc in Sample.LANGCOMBO_SET:
            Contains = True
            #print (Lc, " ----> ", Langs)
            for L in Lc:
                #print ("\t", L)
                if L not in Langs:
                    Contains = False
                    break
            if Contains == False:
                continue
            LangSet.append (Lc)
        if len (LangSet) == 0:
            return []

        MaxLen = 2
        MaxLangs = LangSet[0]
        for L in LangSet:
            if len (L) > MaxLen:
                MaxLen = len (L)
                MaxLangs = L
        
        return MaxLangs

    def CheckLangSlt (self):
        LangSet = []
        for repo in self.Samples:
            Id = repo['id']
            Ai = self.ApiInfo.get (Id)
            Ls = self.GetLangSelt (Ai.Langs)
            if len (Ls) == 0:
                continue
            LangSet.append (Ls)

        #print ("LangSet size is ", len (LangSet), ", Details: ", LangSet)
        if len (LangSet) > self.SmpNum/3:
            return True
        else:
            return False


    def CheckApis (self):
        ApiSet = []
        for repo in self.Samples:
            Id = repo['id']
            Ai = self.ApiInfo.get (Id)
            ApiType = Ai.ApiType
            if ApiType in Sample.LANGINTR_SET:
                ApiSet.append (ApiType)

        ApiSet = set(ApiSet)
        #print ("ApiSet size is ", len (ApiSet), ", Details: ", ApiSet)
        if len (ApiSet) > 3:
            return True
        else:
            return False
                

    def CheckValid (self):
        if self.CheckLangSlt () == False:
            return False

        if self.CheckApis () == False:
            return False
        
        return True

    
    def GetCmmtNum (self, RepoId):
        CmmtFile = System.cmmt_file (RepoId)
        with open(CmmtFile, 'r') as f:
            return len(f.readlines())

    def GenSamples (self):
        ScFile = "Data/StatData/Samples/Samples.csv"
        Header = ['id', 'languages', 'api-type']
        with open(ScFile, 'w', encoding='utf-8') as CsvFile:       
            writer = csv.writer(CsvFile)
            writer.writerow(Header)  
            for smp in self.Samples:
                Id = smp['id']
                Ai = self.ApiInfo.get (Id)
                ApiType = Ai.ApiType
                Ls = self.GetLangSelt (Ai.Langs)
                writer.writerow([Id, Ls, ApiType])
    
    def Smapling (self):
        TryNum = 0;
        while True:
            TryNum += 1
            
            Sn = 0           
            IdDict = {}
            RepoNum = len (self.RepoList)
            self.Samples = []
            while True: 
                RId  = random.randrange(1, 16777215, 1) % RepoNum
                Repo = self.RepoList [RId]
                Id   = Repo['id']
                
                if self.ApiInfo.get (Id) == None:
                    continue

                if IdDict.get (Id) != None:
                    continue
                IdDict[Id] = True

                CmmtNum = self.GetCmmtNum (Id)
                if CmmtNum < self.CmmtNum:
                    continue
                
                self.Samples.append (Repo)
                
                Sn += 1
                if Sn >= self.SmpNum:
                    break

            if self.CheckValid () == True:
                self.GenSamples ()
                break

        self.GrabCmmts ()

    def is_continue (self, errcode):
        codes = [404, 410, 500]
        if (errcode in codes):
            return False
        else:
            return True

    def GetIssueTag (self, url):
        result = requests.get(url,
                              auth=("yawenlee", "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"),
                              headers={"Accept": "application/vnd.github.mercy-preview+json"})
        if (self.is_continue (result.status_code) == False):
            print("$$$%s: %s, URL: %s" % (result.status_code, result.reason, url))
            return " "
        
        if (result.status_code != 200 and result.status_code != 422):
            print("%s: %s, URL: %s" % (result.status_code, result.reason, url))
            sleep(1200)
            return self.GetIssueTag(url)     
        Labels = result.json()['labels']
        if len (Labels) == 0:
            return " "
        LabelName = Labels[0]['name']
        #print ("\tTag = ", LabelName)
        return LabelName

    def IsValidIssue (self, Tag):
        Tag = Tag.lower ()
        ValidTags = ['bug', 'security', 'issue', 'enhancement', 'critical']
        
        for Tg in ValidTags:
            if Tag.find(Tg) != -1:
                return True
        return True

    def GenSampleCmmts (self, RepoId, SampleCmmts):
        if len (SampleCmmts) == 0:
            return

        ScFile = "Data/StatData/Samples/" + str (RepoId) + ".csv"
        Header = SampleCmmts[0].keys()
        with open(ScFile, 'w', encoding='utf-8') as CsvFile:       
            writer = csv.writer(CsvFile)
            writer.writerow(Header)  
            for Smc in SampleCmmts:
                row = Smc.values()
                writer.writerow(row)
  
    def GrabCmmts (self):
        CCm = Collect_CmmtLogs(0)
        
        IssueCmm = 0
        Index = 0
        for repo in self.Samples:
            RepoId = repo['id']
            Url    = repo['url'] + "/issues/"
            print ("[%d][%s]Retrieve %s" %(Index, RepoId, Url) )
            Index += 1
            
            SampleCmmts = []
            CNo = 0
            CmmtFile = System.cmmt_file (RepoId)
            df = pd.read_csv(CmmtFile)
            for index, row in df.iterrows():
                Cmmts = {}
                Cmmts['No'] = CNo
                Cmmts['Valid'] = False
                Cmmts['Message']  = row['message']

                Msg = str(row['message'])
                if row['issue'] != ' ':
                    IssueUrl = Url + row['issue']
                    Cmmts['Issue-url'] = IssueUrl
                    
                    Tag = self.GetIssueTag (IssueUrl)
                    Cmmts['Tag'] = Tag
                    
                    if self.IsValidIssue (Tag) == True: 
                        Cmmts['Valid'] = True     
                        Msg += " " + Tag
                    IssueCmm += 1
                else:
                    Cmmts['Issue-url'] = ' '
                    Cmmts['Tag'] = ' '
                Cmmts['Category'] = CCm.ClassifySeC(Msg)
                        
                SampleCmmts.append (Cmmts)
                CNo += 1
                if CNo >= self.CmmtNum:
                    break
            print ("\tDone...[%d/%d]"  %(len (SampleCmmts), CNo))
            self.GenSampleCmmts (RepoId, SampleCmmts)
        print ("Total %d issue-Commits found!!" %IssueCmm)
        