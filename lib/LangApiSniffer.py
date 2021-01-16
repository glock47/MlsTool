##### LangFfiSniffer.py #####
import os
import re
from lib.Process_Data import Process_Data
from lib.Collect_Research_Data import Collect_Research_Data

LANG_API_FFI = "FFI"
LANG_API_ID  = "Implicit dependence"
LANG_API_HD  = "Hidden dependence"

class State ():
    def __init__(self, id, signature, next=None):
        self.id = id
        self.signature = signature
        self.next = []
        if next != None:
            self.next.append(next)

    def AddNext (self, next):
        self.next.append (next)

    def Match (self, String):
        #print ("\t[State]", self.signature, " ---- ", String)
        if re.search(self.signature, String) != None:
            return True
        else:
            return False
        

class ApiClassifier ():
    def __init__(self, name, clstype, fileType):
        self.name     = name
        self.clstype  = clstype
        self.fileType = fileType.split()
        self.States = []

    def AddState (self, state):
        self.States.append (state)

    def Match (self, File):
        Ext = os.path.splitext(File)[-1].lower()
        if Ext not in self.fileType:
            return False

        #print ("Entry classifier: ", self.name)
        StateStack = self.States
        with open (File, "r") as sf:
            for line in sf:
                if len (line) < 4:
                    continue
                for state in StateStack:
                    isMatch = state.Match(line)
                    #print ("\t Match: ", isMatch, " Line: ", line)
                    if isMatch == False:
                        continue

                    if len (state.next) == 0:
                        return True
                    for next in state.next:
                        StateStack.append (next)
        return False

class LangApiSniffer(Collect_Research_Data):
    def __init__(self, file_name='ApiSniffer'):
        super(LangApiSniffer, self).__init__(file_name=file_name)
        self.ClfList  = []
        self.Repo2Clf = {}
        self.TopLanguages = ["c","c++","java", "javascript","python","html","php","go", "ruby", "objective-c", "css", "shell"]

        self.InitClass ()

    def AddClf (self, Classifier):
        self.ClfList.append (Classifier)

    def _update(self):
        pass

    def _update_statistics(self, repo_item):
        ReppId  = repo_item.id
        RepoDir = "./Data/Repository/" + str(ReppId)
        ApiCls  = self.Sniffer(RepoDir)
        if ApiCls != None:
           print ("Match success: ", ReppId, " -> ", ApiCls.name, " = ", ApiCls.clstype)
           self.Repo2Clf[ReppId] = ApiCls       

    def Sniffer (self, Dir):
        RepoDirs = os.walk(Dir) 
        for Path, Dirs, Fs in RepoDirs:
            for f in Fs:
                File = os.path.join(Path, f)
                #print ("\t->>>Scan: ", File)
                for Clf in self.ClfList:
                    IsMatch = Clf.Match (File)
                    if IsMatch == True:
                        return Clf
        return None
    
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

    def InitClass (self):
        ############################################################
        # Class: Java and C
        ############################################################
        Class = ApiClassifier ("Java-C", LANG_API_FFI, ".java .c")
        S0 = State (0, "System.loadLibrary")
        S1 = State (1, " native ")
        S0.AddNext(S1)
        Class.AddState(S0)

        S2 = State (2, "JNIEXPORT.*JNICALL.*JNIEnv")
        Class.AddState(S2)
        
        self.ClfList.append (Class)

        ############################################################
        # Class: Java and Python
        ############################################################
        Class = ApiClassifier ("Java-Python", LANG_API_FFI, ".py .java")
        S0 = State (0, "from java.* import")
        Class.AddState(S0)
        S1 = State (1, "import org.python.core.*")
        Class.AddState(S1)
        self.ClfList.append (Class)

        ############################################################
        # Class: Java and JavaScript
        ############################################################
        Class = ApiClassifier ("Java-JavaScript", LANG_API_FFI, ".java")
        S0 = State (0, "@JavascriptInterface")
        Class.AddState(S0)
        self.ClfList.append (Class)

        ############################################################
        # Class: Java and TypeScript
        ############################################################
        Class = ApiClassifier ("Java-TypeScript", LANG_API_FFI, ".ts")
        S0 = State (0, "Cocos2dxJavascriptJavaBridge")
        Class.AddState(S0)
        self.ClfList.append (Class)

        ############################################################
        # Class: Java and Ruby
        ############################################################
        Class = ApiClassifier ("Java-Ruby", LANG_API_FFI, ".java .rb")
        S0 = State (0, "require \"java\"")
        Class.AddState(S0)
        S1 = State (1, "org.jruby.javasupport.bsf.JRubyEngine")
        Class.AddState(S1)
        self.ClfList.append (Class)

        ############################################################
        # Class: C and Python
        ############################################################
        Class = ApiClassifier ("C-Python", LANG_API_FFI, ".c .py")
        S0 = State (0, "from cffi import FFI")
        Class.AddState(S0)
        S1 = State (1, "#include <Python.h>")
        S2 = State (2, "PyObject|Py_Initialize|PyMethodDef")
        S1.AddNext(S2)
        Class.AddState(S1)
        self.ClfList.append (Class)


        
    
    
