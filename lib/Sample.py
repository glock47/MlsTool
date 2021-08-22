
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

class SmItem ():
    def __init__(self, Id, Url, Langs, ApiType):
        self.Id       = Id
        self.Url      = Url
        self.Langs    = Langs 
        self.ApiType  = ApiType
        self.VulNum   = 0
        self.RemNum   = 0
        self.IibcNum  = 0
        self.PdNum    = 0
        self.GenNum   = 0

class Sample():

    LANGINTR_SET  = ["FFI", "FFI_IMI", "FFI_IMI_EBD", "IMI", "IMI_EBD"]
    LANGCOMBO_SET = [["python", "shell"], ["go", "shell"], ["css", "html", "javascript", "shell"], ["objective-c", "ruby"], ["html", "python"], 
                     ["c++", "python"], ["c", "python"], ["c", "c++", "shell"], ["java", "shell"], ["javascript", "php"], ["java", "javascript"], ["c", "shell"]]

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
            repo['langs'] = row['language_combinations']
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
        for SamIt in self.Samples:
            Id = SamIt.Id
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
        for SamIt in self.Samples:
            Id = SamIt.Id
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

    def GenSamples (self, FileName='Samples.csv'):
        ScFile = "Data/StatData/Samples/" + FileName
        Header = ['Id', 'Url', 'Langs', 'ApiType', 'RemNum', 'IibcNum', 'PdNum', 'GenNum', 'VulNum']
        with open(ScFile, 'w', encoding='utf-8') as CsvFile:       
            writer = csv.writer(CsvFile)
            writer.writerow(Header)  
            for SamIt in self.Samples:
                row = [SamIt.Id, SamIt.Url, SamIt.Langs, SamIt.ApiType, SamIt.RemNum, SamIt.IibcNum, SamIt.PdNum, SamIt.GenNum, SamIt.VulNum]
                writer.writerow(row)

    def StatCheck (self, Type2Num):
        Num = 0
        for type, num in Type2Num.items ():
            if num == self.SmpNum:
                Num += 1
        if Num >= 5:
            return True
        else:        
            return False

    def StatSamplingByLangs (self):
        Langs2Num = {}
        IdDict = {}
        RepoNum = len (self.RepoList)
        self.Samples = []
        while True: 
            RId  = random.randrange(1, 16777215, 1) % RepoNum
            Repo = self.RepoList [RId]
            Id   = Repo['id']

            Ai = self.ApiInfo.get (Id)
            if Ai == None:
                continue

            if IdDict.get (Id) != None:
                continue
            IdDict[Id] = True

            CmmtNum = self.GetCmmtNum (Id)
            if CmmtNum < self.CmmtNum:
                continue

            Langs = eval(Repo['langs'])
            if len (Langs) == 0:
                continue

            Langs = self.GetLangSelt (Langs[0].split())
            if len (Langs) == 0:
                continue
            
            Langs = "_".join(Langs)
            LangsNum = Langs2Num.get (Langs)
            if LangsNum == None:
                Langs2Num[Langs] = 1
            else:
                if LangsNum >= self.SmpNum:
                    continue
                else:
                    Langs2Num[Langs] = LangsNum + 1
            print ("[%d]%s -> sampling %d" %(len (self.Samples), Langs, Langs2Num[Langs]))
            SamIt = SmItem (Id, Repo['url'], Langs, Ai.ApiType)
            self.Samples.append (SamIt)
            
            if self.StatCheck(Langs2Num) == True:
                break
        self.GrabCmmts ('StatSampleByLangs.csv', False)
        self.Samples = []


    def StatSamplingByApis (self):      
            Apis2Num = {}
            IdDict = {}
            RepoNum = len (self.RepoList)
            self.Samples = []
            while True: 
                RId  = random.randrange(1, 16777215, 1) % RepoNum
                Repo = self.RepoList [RId]
                Id   = Repo['id']
    
                Ai = self.ApiInfo.get (Id)
                if Ai == None:
                    continue
    
                if IdDict.get (Id) != None:
                    continue
                IdDict[Id] = True
    
                CmmtNum = self.GetCmmtNum (Id)
                if CmmtNum < self.CmmtNum:
                    continue
    
                ApisNum = Apis2Num.get (Ai.ApiType)
                if ApisNum == None:
                    Apis2Num[Ai.ApiType] = 1
                else:
                    if ApisNum >= self.SmpNum:
                        continue
                    else:
                        Apis2Num[Ai.ApiType] = ApisNum + 1
                print ("[%d]%s -> sampling %d" %(len (self.Samples), Ai.ApiType, Apis2Num[Ai.ApiType]))
                Langs = self.GetLangSelt (Ai.Langs)
                SamIt = SmItem (Id, Repo['url'], Langs, Ai.ApiType)
                self.Samples.append (SamIt)
    
                if self.StatCheck(Apis2Num) == True:
                    break
            self.GrabCmmts ('StatSampleByApis.csv', False)
            self.Samples = []

    def StatSampling (self):
        self.StatSamplingByLangs ()
        self.StatSamplingByApis ()


    def ValidSmapling (self):
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

                Ai = self.ApiInfo.get (Id)
                if Ai == None:
                    continue

                if IdDict.get (Id) != None:
                    continue
                IdDict[Id] = True

                CmmtNum = self.GetCmmtNum (Id)
                if CmmtNum < self.CmmtNum:
                    continue

                Langs = self.GetLangSelt (Ai.Langs)
                SamIt = SmItem (Id, Repo['url'], Langs, Ai.ApiType)
                self.Samples.append (SamIt)
                
                Sn += 1
                if Sn >= self.SmpNum:
                    break

            if self.CheckValid () == True:
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
  
    def GrabCmmts (self, SampleFile='Samples.csv', GenFlag=True):
        CCm = Collect_CmmtLogs(0)
        
        IssueCmm = 0
        Index = 0
        for SamIt in self.Samples:
            RepoId = SamIt.Id
            ISUrl  = SamIt.Url + "/issues/"
            CMUrl  = SamIt.Url + "/commits/"
            print ("[%d][%s]Retrieve %s" %(Index, RepoId, ISUrl) )
            Index += 1
            
            SampleCmmts = []
            CNo = 0
            CmmtFile = System.cmmt_file (RepoId)
            df = pd.read_csv(CmmtFile)
            for index, row in df.iterrows():
                Cmmts = {}
                Cmmts['No'] = CNo
                Cmmts['Url'] = CMUrl + row['sha']
                Cmmts['Valid'] = False
                Cmmts['Message']  = row['message']

                Msg = str(row['message'])
                if row['issue'] != ' ':
                    IssueUrl = ISUrl + row['issue']
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

                Category = CCm.ClassifySeC(Msg)
                Cmmts['Category'] = Category

                if Category != 'None':
                    SamIt.VulNum += 1
                    if Category == "Risky_resource_management":
                        SamIt.RemNum += 1
                    elif Category == "Insecure_interaction_between_components":
                        SamIt.IibcNum += 1
                    elif Category == "Porous_defenses":
                        SamIt.PdNum += 1
                    else:
                        SamIt.GenNum += 1                    
                        
                SampleCmmts.append (Cmmts)
                CNo += 1
                if CNo >= self.CmmtNum:
                    break
            print ("\tDone...[%d/%d]"  %(len (SampleCmmts), CNo))
            if GenFlag == True:
                self.GenSampleCmmts (RepoId, SampleCmmts)

        self.GenSamples (SampleFile)
        print ("Total %d issue-Commits found!!" %IssueCmm)
        