
import csv  
from types import SimpleNamespace

from lib.Evolve_Stat import Evolve_Stat
from lib.Process_Data import Process_Data


class LangStat():
    def __init__ (self, year, lang_count):
        self.year  = year
        self.count = lang_count

class Evolve_LangStat(Evolve_Stat):

    def __init__(self, file_name='Language_Stats'):
        super(Evolve_LangStat, self).__init__(file_name=file_name)

        self.StatByYear = {}
        self.TopLanguagesByCount = {}
        self.TopLanguagesByBytes = {}
        self.TopLanguagesByPercent = {}

    def _update_statistics(self, year, item_list):
        print ("item_list count = %d" %len(item_list))
        lang_stat = LangStat (year, len(item_list))
        self.evolve_stats[year] = lang_stat

        self.StatByYear[year] = item_list

        for item in item_list: 
            item = SimpleNamespace(**item)

            if (self.TopLanguagesByCount.get (item.language, None) == None):
                self.TopLanguagesByCount[item.language] = item.count
            else:
                self.TopLanguagesByCount[item.language] += item.count
            
            if (self.TopLanguagesByBytes.get (item.language, None) == None):
                self.TopLanguagesByBytes[item.language] = item.bytes
            else:
                self.TopLanguagesByBytes[item.language] += item.bytes

            if (self.TopLanguagesByPercent.get (item.language, None) == None):
                self.TopLanguagesByPercent[item.language] = item.percentage_sum
            else:
                self.TopLanguagesByPercent[item.language] += item.percentage_avg

    def _write_csv_by_year(self, file_name, fields, stat_dict, type):

        valid_languages = []
        file = self.out_path + file_name + '_Year.csv'
        print("---> Writing to" + file)       
        with open(file, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(fields)

            for lang in stat_dict.keys():
                row = []

                row.append (lang)
                for year, stat_list in self.StatByYear.items():
                    value = 0
                    for item in stat_list: 
                        item = SimpleNamespace(**item)
                                              
                        if (lang == item.language):
                            if (type == "count"):
                                value = item.count
                            elif (type == "bytes"):
                                value = item.bytes
                            else:
                                value = item.percentage_avg
                            break
                        else:
                            continue
                    if (value != 0):
                        row.append (str(value))
                    else:
                        break
                        row.append ("None")

                if (len(row) < len (fields)):
                    continue
                writer.writerow(row)
                valid_languages.append (lang)
        
        csv_file.close()
        return valid_languages

       
    def _get_lang_rank (self, lang, stat_dict):
        rank = 1
        for ls in stat_dict.keys():
            if ls == lang:
                return rank
            rank += 1
        return 0
    
    def _write_csv(self, file_name, valid_languages, stat_dict, type):
        fields  = ['year']
        
        fields += valid_languages
        
        file = self.out_path + file_name + '.csv'
        print("---> Writing to" + file)       
        with open(file, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(fields)

            for year, stat_list in self.StatByYear.items():
                row = []

                row.append (year)

                for lang in valid_languages:
                    rank = 0
                    for item in stat_list: 
                        item = SimpleNamespace(**item)
                        rank += 1
                                              
                        if (lang == item.language):
                            if (type == "count"):
                                value = item.count
                            elif (type == "bytes"):
                                value = item.bytes
                            else:
                                value = rank
                            break
                        else:
                            continue
                    
                    if (value != 0):
                        row.append (str(value))
                    else:
                        break
  

                if (len(row) < len (fields)):
                    continue
                writer.writerow(row)
        
        csv_file.close()
        return

    def _update(self):
        super(Evolve_LangStat, self).save_data(self.evolve_stats)

        self.TopLanguagesByCount = Process_Data.dictsort_value (self.TopLanguagesByCount, True)
        self.TopLanguagesByBytes = Process_Data.dictsort_value (self.TopLanguagesByBytes, True)
        self.TopLanguagesByPercent = Process_Data.dictsort_value (self.TopLanguagesByPercent, True)

        # get output field
        StatFields = ["language"]
        StatFields += [key for key in self.evolve_stats.keys()]
        self._write_csv_by_year ("Evolve_Language_Count", StatFields, self.TopLanguagesByCount, "count")
        self._write_csv_by_year ("Evolve_Language_Bytes", StatFields, self.TopLanguagesByBytes, "bytes")
        
        valid_languages = self._write_csv_by_year ("Evolve_Language_Percent", StatFields, self.TopLanguagesByPercent, "percent")
        self._write_csv ("Evolve_Language_Percent", valid_languages, self.TopLanguagesByPercent, "percent")


