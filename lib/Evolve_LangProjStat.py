
import csv  
from types import SimpleNamespace
from lib.Evolve_Stat import Evolve_Stat


class Evolve_LangProjStat(Evolve_Stat):

    def __init__(self, file_name='LangProj_Stats'):
        super(Evolve_LangProjStat, self).__init__(file_name=file_name)

        self.StatByYear = {}

    def _update_statistics(self, year, item_list):

        self.StatByYear[year] = item_list

    
    def _write_csv(self, file_name, valid_counts):
        fields  = ['year']
        
        fields += valid_counts
        
        file = self.out_path + file_name + '.csv'
        print("---> Writing to" + file)       
        with open(file, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(fields)

            for year, stat_list in self.StatByYear.items():
                row = []

                row.append (year)

                for count in valid_counts:

                    value = 0
                    for item in stat_list: 
                        item = SimpleNamespace(**item)
                     
                        if (count == item.language_count):
                            value = item.distribution
                        else:
                            continue
                    
                    row.append (str(value))

                writer.writerow(row)
        
        csv_file.close()
        return

    def _update(self):

        valid_counts = []
        for count in range (1, 21, 1):
            valid_counts.append (count)

        self._write_csv ("Evolve_LangProj", valid_counts)


