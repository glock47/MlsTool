
import csv  
from types import SimpleNamespace

from lib.Evolve_Stat import Evolve_Stat
from lib.Process_Data import Process_Data

class MultiLangStat():
    def __init__ (self, year, multi_percent):
        self.year  = year
        self.multi_language_usage = multi_percent


class AvgMlStat():
    def __init__ (self, year, avg_num):
        self.year  = year
        self.average_count = avg_num


class Evolve_MultiLangStat(Evolve_Stat):

    def __init__(self, file_name='Repository_Stats'):
        super(Evolve_MultiLangStat, self).__init__(file_name=file_name)
        self.evolve_stats_avgml = {}


    def _update_statistics(self, year, item_list):
        print ("item_list count = %d" %len(item_list))

        multi_count = 0
        lang_count = 0
        for item in item_list: 
            item = SimpleNamespace(**item)
            if (item.languages_used > 1):
                multi_count += 1

            lang_count += item.languages_used

        self.evolve_stats_avgml[year] = AvgMlStat (year, lang_count/len(item_list))
        self.evolve_stats[year] = MultiLangStat (year, multi_count/len(item_list))

    def _update(self):
        super(Evolve_MultiLangStat, self).save_data(self.evolve_stats, "Evolve_MultiLang_Stats")
        super(Evolve_MultiLangStat, self).save_data(self.evolve_stats_avgml, "Evolve_MultiLang_AvgNum")


