#!/usr/bin/python

from lib.System import System
from lib.Process_Data import Process_Data
import csv
import sys
import os
import requests
import pandas as pd
from time import sleep
import re
import nltk
nltk.download('stopwords');nltk.download('brown');nltk.download('punkt');nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False



class Diff ():
    def __init__(self, file, content):
        self.file = file
        self.content = content

    def AddFile (self, file):
        self.file += " " + file

    def AddContent (self, content):
        self.content += " " + content

class Commit ():
    def __init__(self, id, sha, author, date, message):
        self.id      = id
        self.sha     = sha
        self.author  = author
        self.date    = date
        self.message = message
        self.issue   = ' '

        self.Diffs   = None

    def AddDiff (self, DF):
        if self.Diffs == None:
            self.Diffs = DF
        else:
            self.Diffs.AddFile(DF.file)
            self.Diffs.AddContent(DF.content)
        

class CloneRepo():
    def __init__(self, RepoPath, startNo=0, endNo=65535):
        self.RepoPath = RepoPath        
        self.RepoList = []
        self.UserName = "wangtong0908"
        self.Token    = "8ad9a6cddbd384072d2410d3f32dad4455c67d64"

        self.Commits  = []
        self.Exts = ['.h', '.c', '.cpp', '.cc', '.i', '.js', '.css', '.json', '.sh', '.jsx', '.xml', '.yml',
                     '.jade', '.scss', '.coffee', '.py', '.php', '.php3', '.ps1', '.zsh', '.bash', ".sh", '.pl', 
                     '.go', '.sh', '.java', '.asp', '.aspx', '.ashx', '.cs', '.html', 'cls', 'csc', '.cxx', 
                     '.hpp', '.jsp', '.pas', '.phtml', '.s', '.vbs']
        self.BaseDir = os.getcwd ()

        self.startNo = startNo
        self.endNo   = endNo

    def CleanText(self, Text):
        Text = str (Text)
        Text = re.sub(r'[+|/]', ' ', Text)
        Text = re.sub(r'[^\w\d,.]', ' ', Text)
        Text = Text.lower()
        words = Text.split()
        words = [re.sub(r'[^a-z]', ' ', word) for word in words if word.isalnum()]
        return Text      
        
    def Cleaning(self, Text, min_len=3, max_len=16):
        Text = self.CleanText (Text)       
        words = nltk.word_tokenize(Text)
        words = [lemmatizer.lemmatize(word) for word in words]
        stopwords_list = stopwords.words('english') 
        words = [word for word in words if word not in stopwords_list and len(word) >= min_len and len(word) < max_len]
        #words = list (set (words))
        return " ".join(words)

    def WriteCommts (self, RepoId):
        CmmtFile = self.BaseDir + "/Data/CmmtSet/" + str (RepoId) + ".csv"
        Header = ['id', 'sha', 'author', 'date', 'issue', 'message', 'file', 'content']
        with open(CmmtFile, 'w', encoding='utf-8') as CsvFile:       
            writer = csv.writer(CsvFile)
            writer.writerow(Header)  
            for cmmt in self.Commits:
                if cmmt.Diffs == None:
                    row = [cmmt.id, cmmt.sha, cmmt.author, cmmt.date, cmmt.issue, cmmt.message, "", ""]
                else:
                    row = [cmmt.id, cmmt.sha, cmmt.author, cmmt.date, cmmt.issue, cmmt.message, cmmt.Diffs.file, cmmt.Diffs.content]
                writer.writerow(row)
        CsvFile.close()

    def PassLangs (self, LangFile="lang.ll"):
        with open(LangFile, 'r', encoding='latin1') as Lfile:
            Langs = []
            for line in Lfile:
                ll = re.findall(r"%  (.+?)\n", line)
                #print ("Line = ", line, ", lang = ", ll)
                if len (ll) == 0:
                    continue
                Langs.append (ll[0].strip().lower())
            #print ("Old langs -> ", Langs)
            return Langs
        
    def CheckLangs (self, Langs, Date='2018-06-01'):
        print ("New langs -> ", Langs)
        CmmDate = None
        Cmmt = None
        for cmmt in self.Commits:
            CmmDate = re.findall('\d{4}-\d{2}-\d{2}', cmmt.date)[0]
            if CmmDate < Date:
                Cmmt = cmmt
                break
        if Cmmt == None:
            Cmmt = self.Commits[-1]
        HistCmd = "git checkout " + Cmmt.sha
        os.system (HistCmd)
        LangCmd = "github-linguist > lang.ll"
        os.system (LangCmd)

        HistLangs = self.PassLangs ()
        if len (HistLangs) < len (Langs):
            print ("Hist langs -> ", HistLangs)
            return False
        else:
            return True

    def is_continue (self, errcode):
        codes = [404, 500]
        if (errcode in codes):
            return False
        else:
            return True


    def IsInExt (self, Ext):
        lower = Ext.lower ()
        if lower in self.Exts:
            return True
        else:
            return False

    def HttpCall (self, url):
        result = requests.get(url,
                              auth=(self.UserName, self.Token),
                              headers={"Accept": "application/vnd.github.mercy-preview+json"})
        if (self.is_continue (result.status_code) == False):
            print("$$$%s: %s, URL: %s" % (result.status_code, result.reason, url))
            return None
        
        if (result.status_code != 200 and result.status_code != 422):
            print("%s: %s, URL: %s" % (result.status_code, result.reason, url))
            sleep(1200)
            return self.HttpCall(url)     
        return result.json()

    def GetClonePath (self, CloneRepoPath):
        RepoPath = "Data/OriginData/" + self.RepoPath
        df = pd.read_csv(RepoPath)
        for index, row in df.iterrows():            
            repo = {}
            repo['id']  = row['id']
            
            ApiUrl = row['url']
            print ("[%d] Retrieve %s -> %s" %(index, row['id'], row['url']))
            Data = self.HttpCall (ApiUrl)
            if Data == None:
                continue
            repo['clone_url'] = Data['clone_url']
            repo['language_dictionary'] = eval(row['language_dictionary'])        
            self.RepoList.append (repo)

    def GetRepoList(self):
        RepoPath = "Data/OriginData/" + self.RepoPath
        df = pd.read_csv(RepoPath)
        for index, row in df.iterrows():            
            repo = {}
            repo['id']  = row['id']
            repo['clone_url'] = row['clone_url']
            repo['language_dictionary'] = eval(row['language_dictionary'])
            self.RepoList.append (repo)
        print ("Total %d Repositories" %len(self.RepoList))
        
    
    def WriteCsv (self, Data, FileName):
        with open(FileName, 'w', encoding='utf-8') as csv_file:       
            writer = csv.writer(csv_file)
            header = list(Data[0].keys()) 
            writer.writerow(header)            
            for item in Data:
                if item != None:
                    row = list(item.values())
                    writer.writerow(row)
        csv_file.close()


    def ParseLog (self, LogFile):
        
        with open(LogFile, 'r', encoding='latin1') as Lfile:
            state = 0
            Cmmt = None
            Message = ""
            Index   = 0
            Df      = None
            DfContent = ""
            for line in Lfile:
                if line[0:2] in ["- ", "@@",  "--", "++", "in"]:
                    continue
                
                if line[0:7] == "commit ":
                    if Df != None:
                        Df.content = self.Cleaning(DfContent) 
                        Cmmt.AddDiff (Df)
                        #print (DfContent)
                        Df = None
                        DfContent = ""
                                
                    Id  = len(self.Commits)
                    Sha = line[8:-1]
                    Cmmt = Commit (Id, Sha, None, None, None)
                    self.Commits.append (Cmmt)
                    state = 0
                elif line[0:8] == "Author: ":
                    Cmmt.author = line[9:-1]
                elif line[0:6] == "Date: ":
                    Cmmt.date = line[7:-1]
                    state = 1
                    Message = ""
                else:
                    if len (line) < 6 :
                        if Message != "":
                           Cmmt.message = Message
                           state = 2
                           Message = ""
                           #print (Cmmt.sha, " -> ", Cmmt.message)
                        continue

                    # message
                    if state == 1:
                        Message += ' ' + line

                    #diff
                    if state == 2:
                        if line[0:12] == "diff --git a":
                            if Df != None:
                                Df.content = self.Cleaning(DfContent)
                                Cmmt.AddDiff (Df)
                                Df = None
                                DfContent = ""
                                #print (DfContent)
                            Path, Name = os.path.split(line[13:-1])
                            File, Ext  = os.path.splitext(Name)
                            self.Extersion [Ext] = True
                            if self.IsInExt (Ext):
                                Df = Diff (Name, "") 
                            
                            continue
                    #diff content
                    if Df != None:
                        DfContent += ' ' + line
                 
    def ParseLogSmp (self, LogFile):      
        import re
        IssueNum = 0
        self.Commits  = []
        with open(LogFile, 'r', encoding='latin1') as Lfile:
            Cmmt   = None
            Author = None
            Date   = None
            Message = ""
            Index   = 0
            for line in Lfile:
                if line[0:7] == "commit ":
                    if Cmmt != None:
                        Cmmt.message = Message
                        Message = ''
                    Id  = len(self.Commits)
                    Sha = line[7:-1]
                    Cmmt = Commit (Id, Sha, None, None, None)
                    self.Commits.append (Cmmt)
                elif line[0:8] == "Author: ":
                    Cmmt.author = line[9:-1]
                elif line[0:7] == "Merge: ":
                    continue
                elif line[0:6] == "Date: ":
                    Cmmt.date = line[7:-1]
                else:
                    if len (line) < 6 :
                        continue
                    
                    issue = re.findall(r"#(\d+?)[\s\r\n]", line)
                    if len (issue) == 0:
                        issue = re.findall(r"/issues/(\d+?)[\s\r\n]", line)
                    if len (issue) != 0:
                        issue = issue[0]
                        if is_number (issue) == True:
                            #print ("\tExist issue -> ", line, ", issue -> ", issue)
                            Cmmt.issue = issue
                            IssueNum += 1
   
                    Message += ' ' +  self.Cleaning(line)
                    #print ("Get msg -> ", Message)
            return IssueNum
    
    def CloneLog (self, RepoId, RepoDir, Langs):
        Repo = RepoDir + "/" + os.listdir(RepoDir)[0]     
        os.chdir(Repo)
        print ("Repo -> ", Repo)

        LogFile = str (RepoId) + ".log"
        #LogCmd = "git log -20000 --date=iso -p > " + LogFile # for ParseLog
        LogCmd = "git log -20000 --date=iso > " + LogFile     # for ParseLogSmp
        os.system (LogCmd)
        print (LogCmd)
        print ("ParseLog....")
        IssueNum = self.ParseLogSmp (LogFile)
        IssueRate = int (IssueNum*100/len (self.Commits))
        if self.CheckLangs (Langs) == True and IssueRate >= 1  and len (self.Commits) >= 1000:
            print ("@@@@@@ CmmtsNum = %d, IssueNum = %d" %(len(self.Commits), IssueNum))
            self.WriteCommts (RepoId)
            #os.remove (LogFile)
            return True
        else:
            RmCmd = "rm -rf " + RepoDir
            os.system (RmCmd)
            return False

    def Clean (self, RepoDir):
        if not os.path.exists (RepoDir):
            return
        os.chdir(RepoDir)
        CleanCmd = "find . -name \".git\" | xargs rm -rf"
        os.system (CleanCmd)
        
    def Clone (self):
        self.Extersion = {}
        self.GetRepoList ()
        BaseDir = self.BaseDir + "/Data/Repository/"
        if not os.path.exists (BaseDir):
            os.mkdir (BaseDir)
        print (BaseDir)
        Id = 0
        for repo in self.RepoList:
            if Id < self.startNo or Id > self.endNo:
                Id += 1
                continue

            RepoDir = BaseDir + str(repo['id'])
            if System.access_tag (str(repo['id'])):
                self.Clean (RepoDir)
                Id += 1
                continue
            
            if not os.path.exists (RepoDir):
                os.mkdir (RepoDir)
            else:
                RmCmd = "rm -rf " + RepoDir + "/*"
                os.system (RmCmd)         
            os.chdir(RepoDir)

            CloneCmd = "git clone " + repo['clone_url']
            print ("[", Id, "] --> ", CloneCmd)
            os.system (CloneCmd)
            Id += 1

            LangsDict = repo['language_dictionary']
            Langs = [lang.lower() for lang in LangsDict.keys()]
            if self.CloneLog (repo['id'], RepoDir, Langs) == True:
                self.Clean (RepoDir)
            System.set_tag (str(repo['id']))
            

