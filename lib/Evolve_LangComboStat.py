
import csv  

from lib.Process_Data import Process_Data
from types import SimpleNamespace
from lib.Evolve_Stat import Evolve_Stat
from lib.LangCombo_Stats  import LangCombo_Stats

MAX_RANK = 30

class ComboStat ():
    def __init__ (self, combo, id, distribution):
        self.combo  = combo
        self.id     = id
        self.distribution = distribution

class LangComboStat():

    def __init__ (self, year):
        self.year  = year
        self.lang_combonitions = {}  
        self.combonitions_range = {}

    def update (self, combo, count, range):
        self.lang_combonitions[combo] = count
        self.combonitions_range[combo] = range

    def get_count (self, combo):
        return self.lang_combonitions.get (combo, None)

    def get_range (self, combo):
        return self.combonitions_range.get (combo, None)

class Evolve_LangComboStat(Evolve_Stat):
    def __init__(self, file_name='LangCombo_Stats'):
        super(Evolve_LangComboStat, self).__init__(file_name=file_name)
        self.TopCombinations = {}

    def _update_statistics(self, year, item_list):
        langcombo_stat = LangComboStat (year)
        print ("item.combinationb count:%d" %len(item_list))

        index = 0
        for item in item_list: 
            item = SimpleNamespace(**item)
            langcombo_stat.update(item.combination, item.count, item.combo_id+1)
            print (str(index) + " --- " + item.combination)
            index += 1
            
            if (self.TopCombinations.get (item.combination, None) == None):
                self.TopCombinations[item.combination] = item.distribution
            else:
                self.TopCombinations[item.combination] += item.distribution
        self.evolve_stats[year] = langcombo_stat

    def _get_lang_set (self, combo):
        language = []
        for lang in combo.split(" "):
            language.append (lang)
        return set (language)

    def _write_csv(self, fields):  
        file = self.out_path + self.out_file + '.csv'
        print("---> Writing to" + file)       
        with open(file, 'w') as csv_file:
            writer = csv.writer(csv_file)
            col = ["year"] + fields
            writer.writerow(col)

            for year, stat in  self.evolve_stats.items():
                row = []

                row.append (year)
                for combo in fields:
                    count = stat.get_range (combo)
                    if (count == None):
                        row.append (str(MAX_RANK))
                    else:
                        count = count%MAX_RANK
                        if (count == 0):
                            count = MAX_RANK
                        row.append (str(count))    
                    
                if (len(row) < len (fields)):
                    continue
                    
                writer.writerow(row)
        csv_file.close()

    def _write_csv_by_year(self):
        fields = ["combination"]
        fields += [key for key in self.evolve_stats.keys()]
        print (fields)
        
        file = self.out_path + self.out_file + '_Year.csv'
        print("---> Writing to" + file)       
        with open(file, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(fields)
        
            for combo in self.TopCombinations.keys():
                row = []
        
                row.append (combo)
                for year, stat in self.evolve_stats.items():
                    count = stat.get_count (combo)
                    if (count == None):
                        row.append (str(count))
                    else:
                        row.append (str(count))
                if (len(row) < len (fields)):
                    continue
                            
                writer.writerow(row)
            csv_file.close()


    def _get_valid_combo(self):
        valid_combo = []
        ValidKeys = [key for key in self.evolve_stats.keys()]
        
        for combo in self.TopCombinations.keys():
            row = []

            IsValid = False
            NoneCount = 0
            for year, stat in self.evolve_stats.items():
                count = stat.get_count (combo)
                if (count == None):
                    if (IsValid == True):
                        break
                    row.append (str(count))
                    NoneCount += 1
                else:
                    IsValid = True
                    row.append (str(count))

            if ((len(row) < len (ValidKeys)) or (NoneCount*2 > len (ValidKeys))):
                continue
                    
            valid_combo.append(combo)

        return valid_combo#[1:51:1]
    
    def _update(self):
        self.TopCombinations = Process_Data.dictsort_value (self.TopCombinations, True)

        # get output field
        self._write_csv (self._get_valid_combo ())
        self._write_csv_by_year();


