
import os
import pandas as pd
import random
from lib.System import System

class ApiInfo ():
    def __init__(self, Id, Langs, ApiType):
        self.Id = Id
        self.Langs = Langs
        self.ApiType = ApiType 

class Sample():

    LANGINTR_SET  = ["FFI", "FFI_ID", "FFI_IRI", "FFI_IRI_ID", "IRI", "IRI_ID"]
    LANGCOMBO_SET = [["python", "shell"], ["c", "c++"], ["go", "shell"], ["objective-c", "ruby"], ["css", "html", "javascript", "shell"], 
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
            self.RepoList.append (repo)

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

        print ("LangSet size is ", len (LangSet), ", Details: ", LangSet)
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
            print (ApiType)
            if ApiType in Sample.LANGINTR_SET:
                ApiSet.append (ApiType)

        ApiSet = set(ApiSet)
        print ("ApiSet size is ", len (ApiSet), ", Details: ", ApiSet)
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
        
    
    def Smapling (self):
        while True:
            Sn = 0
            TryNum = 0;
            IdDict = {}
            RepoNum = len (self.RepoList)
            while True:
                TryNum += 1
                if Sn >= 50:
                    break
                
                RId  = random.randrange(1, 16777215, 1) % RepoNum
                Repo = self.RepoList [RId]
                Id   = Repo['id']
                
                if self.ApiInfo.get (Id) == None:
                    continue

                if IdDict.get (Id) != None:
                    continue
                IdDict[Id] = True

                self.Samples.append (Repo)
                Sn += 1

            if self.CheckValid () == True:
                break

        self.GrabCmmts ()

    def GetIssueTag (self, url):
        result = requests.get(url,
                              auth=("yawenlee", "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"),
                              headers={"Accept": "application/vnd.github.mercy-preview+json"})
        if (self.is_continue (result.status_code) == False):
            print("$$$%s: %s, URL: %s" % (result.status_code, result.reason, url))
            return ""
        
        if (result.status_code != 200 and result.status_code != 422):
            print("%s: %s, URL: %s" % (result.status_code, result.reason, url))
            sleep(1200)
            return self.get_issuetag(url, issue)     
        Labels = result.json()['labels']
        if len (Labels) == 0:
            return ""
        LabelName = Labels[0]['name']
        return LabelName

    def GrabCmmts (self):
        for repo in self.Samples:
            RepoId = repo['id']
            Url    = repo['url'] + "/issues/"

            Cmmts = {}
            CNo = 0
            CmmtFile = System.cmmt_file (RepoId)
            df = pd.read_csv(CmmtFile)
            for index, row in df.iterrows():
                if row['issue'] == ' ':
                    continue

                IssueUrl = Url + row['issue']
                Tag = self.GetIssueTag (IssueUrl)
                if Tag != 'bug':
                    continue
                
                Cmmts['No'] = CNo
                Cmmts['Issue-url'] = IssueUrl
                Cmmts['Tag'] = Tag
 
            
        