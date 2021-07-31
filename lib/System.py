
import os


class System():

    START_YEAR   = 2011
    END_YEAR     = 2020
    PAGE_COUNT   = 10
    PER_PAGE     = 100
    RELEASE      = "release"

    VERSION_REPO_NUM = 100

    OriginCollect= "OriginData"
    OriginStat   = "StatData"
    Evoluation   = "Evoluation"

    BaseDir      = os.getcwd() + "/Data"
    CollectDir   = OriginCollect
    StatisticDir = OriginStat

    Version      = "None"

    CMMT_DIR     = BaseDir + "/CmmtSet/"
    if not os.path.exists (CMMT_DIR):
        os.mkdir (CMMT_DIR)
        
    CMMT_STAT_DIR= BaseDir + "/" + OriginStat + "/CmmtSet/"
    if not os.path.exists (CMMT_STAT_DIR):
        os.mkdir (CMMT_STAT_DIR)

    KEYWORD_FILE = BaseDir + "/" + OriginCollect + "/keywords.txt"

    MAX_CMMT_NUM = 20 * 1024

    TagSet       = BaseDir + "/TagSet"
    if not os.path.exists (TagSet):
        os.mkdir (TagSet)

    IssueDir     = BaseDir + "/Issues"
    if not os.path.exists (IssueDir):
        os.mkdir (IssueDir)

    @staticmethod
    def issue_file(id):
        return (System.IssueDir + "/" + str(id) + ".csv")
    
    @staticmethod
    def cmmt_file(id):
        return (System.CMMT_DIR + str(id) + ".csv")

    @staticmethod
    def cmmt_stat_file(id):
        return (System.CMMT_STAT_DIR + str(id))

    @staticmethod
    def is_exist(file):
        isExists = os.path.exists(file)
        if (not isExists):
            return False
        
        fsize = os.path.getsize(file)/1024
        if (fsize == 0):
            return False
        return True      

    @staticmethod
    def mkdir(path):
        path=path.strip()
        path=path.rstrip("\\")
        isExists=os.path.exists(path)
        if not isExists:
            os.makedirs(path)

    @staticmethod
    def set_release(release):
        System.Version = release

    @staticmethod
    def get_release():
        return System.Version
        
    @staticmethod
    def setdir(collect_dir, stat_dir):
        System.CollectDir = System.OriginCollect + collect_dir
        System.StatisticDir = System.OriginStat  + stat_dir

        path = System.BaseDir + "/" + System.CollectDir
        System.mkdir (path)

        path = System.BaseDir + "/" + System.StatisticDir
        System.mkdir (path)

    @staticmethod
    def getdir_collect():
        return (System.BaseDir + "/" + System.CollectDir + "/")

    @staticmethod
    def getdir_collect_origin():
        return (System.BaseDir + "/" + System.OriginCollect + "/")

    @staticmethod
    def getdir_stat():
        StatDir = System.BaseDir + "/" + System.StatisticDir + "/"
        if not os.path.exists(StatDir):
            System.mkdir (StatDir)
        return StatDir

    @staticmethod
    def getdir_evolve():
        EvolveDir =  (System.BaseDir + "/" + System.Evoluation + "/")
        if not os.path.exists(EvolveDir):
            System.mkdir (EvolveDir)
        return EvolveDir

    def get_release_version():
        return

    @staticmethod
    def set_tag(tag):
        NewDir = System.TagSet
        if not os.path.exists (NewDir):
            os.mkdir (NewDir)
        file = open(NewDir + "/" + tag, 'w')
        file.close()
        
    @staticmethod
    def access_tag(tag):
        tagPath = System.TagSet + "/" + tag
        isExists = os.path.exists(tagPath)
        if not isExists:
            return False
        return True
 
