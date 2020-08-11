#!/usr/bin/python

import sys, getopt
from progressbar import ProgressBar
from lib.System import System

from lib.Evolve_LangStat import Evolve_LangStat
from lib.Evolve_LangComboStat import Evolve_LangComboStat
from lib.Evolve_MultiLangStat import Evolve_MultiLangStat

from lib.Evolve_LangProjStat import Evolve_LangProjStat


def main(argv):
    type = ''
   
    # get step
    try:
        opts, args = getopt.getopt(argv,"ht:",["type="])
    except getopt.GetoptError:
        print ("evolve.py -t <type_name>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ("evolve.py -t <type_name>");
            sys.exit()
        elif opt in ("-t", "--type"):
            type = arg;


    #if (type == "lang"):
    evolve_stat = Evolve_LangStat('Language_Stats')
    evolve_stat.process ()

    #if (type == "langcombo"):
    evolve_stat = Evolve_LangComboStat('LangCombo_Stats')
    evolve_stat.process ()

    #if (type == "multi"):
    evolve_stat = Evolve_MultiLangStat('Repository_Stats')
    evolve_stat.process ()

     #if (type == "langproj"):
    evolve_stat = Evolve_LangProjStat('LangProj_Stats')
    evolve_stat.process ()

if __name__ == "__main__":
   main(sys.argv[1:])