
import os


class System():

    START_YEAR   = 2010
    END_YEAR     = 2019
    PAGE_COUNT   = 10
    PER_PAGE     = 100
    RELEASE      = "release"

    VERSION_REPO_NUM = 100

    OriginCollect= "OriginData"
    OriginStat   = "StatData"
    Evoluation   = "Evoluation"

    BaseDir      = "./Data"
    CollectDir   = OriginCollect
    StatisticDir = OriginStat

    Version      = "None"

    CMMT_DIR     = BaseDir + "/CmmtSet/"
    CMMT_STAT_DIR= BaseDir + "/" + OriginStat + "/CmmtSet/"

    KEYWORD_FILE = BaseDir + "/" + OriginCollect + "/keywords.txt"

    MAX_CMMT_NUM = 20 * 1024

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
        return (System.BaseDir + "/" + System.StatisticDir + "/")

    @staticmethod
    def getdir_evolve():
        evolve_dir =  (System.BaseDir + "/" + System.Evoluation + "/")
        System.mkdir (evolve_dir)
        return evolve_dir

    def get_release_version():
        return 
 
