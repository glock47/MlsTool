

import abc 
import csv
import sys
from progressbar import ProgressBar
from types import SimpleNamespace

from lib.System import System
from lib.Process_Data import Process_Data


csv.field_size_limit(sys.maxsize)


class Evolve_Stat(metaclass=abc.ABCMeta):

    def __init__(self, file_name):
        self.file_name = file_name
        self.file_path = System.getdir_stat()
        
        self.out_file  = "Evolve_" + file_name      
        self.out_path  = System.getdir_evolve()
        self.evolve_stats = {}

    def save_data(self, data, file_name=None):
        if (file_name == None):
            file_name = self.out_file
        file = self.out_path + file_name + '.csv'
        print("---> Writing to " + file)       
        with open(file, 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(self._get_header(data))
            for key, value in data.items():
                row = self._object_to_list(value)
                writer.writerow(row)
        csv_file.close()

    def _object_to_list(self, value):
        return list(value.__dict__.values())

    def _get_header(self, data):
        headers = list(list(data.values())[0].__dict__.keys())
        return [header.replace(" ", "_") for header in headers]

    def process(self):
        start_year = System.START_YEAR
        end_year = System.END_YEAR
        
        pbar = ProgressBar()
        for year in pbar(range (start_year, end_year+1, 1)):
            System.setdir (str(year), str(year))
            item_list = Process_Data.load_data(file_path=System.getdir_stat(), file_name=self.file_name)
            item_list = Process_Data.dict_to_list(item_list)
            
            #item_list = SimpleNamespace(**item_list)
            self._update_statistics(year, item_list)
        self._update()

    @abc.abstractmethod
    def _update(self):
        print("Abstract Method that is implemented by inheriting classes")

    @abc.abstractmethod
    def _update_statistics(self, year, item_list):
        print("Abstract Method that is implemented by inheriting classes")
