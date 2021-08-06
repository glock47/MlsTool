##### Collect_Research_Data.py #####

from lib.System import System
from lib.Process_Data import Process_Data
# Allows for abstract classes
import abc  # abc.ABCMeta, @abc.abstractmethod
from progressbar import ProgressBar  # ProgressBar()
from types import SimpleNamespace
# Reads/Writes in a CSV formatted file
import csv  # reader()
import sys  # sys.maxsize
# Allows code to read in large CSV files
csv.field_size_limit(sys.maxsize)
# Displays a progress bar while looping through an iterable object


class Collect_Research_Data(metaclass=abc.ABCMeta):

    Language_Combination_Limit = 20

    def __init__(self, file_name):
        self.file_name = file_name
        self.file_path = System.getdir_stat()
        self.research_stats = {}
        self.lang_proj_stats = {}
        
    @abc.abstractmethod
    def save_data(self, data, file_name=None):
        if (file_name == None):
            file_name = self.file_name
        self.__write_data_to_csv(data, file_name, True)
        self.__serialize_objects(data, file_name)


    def save_data2(self, data, file_name=None):
        if (file_name == None):
            file_name = self.file_name
        self.__write_data_to_csv(data, file_name)

    def __write_data_to_csv(self, data, file_name, flag=False):
        file = self.file_path + file_name
        if file.find ('.csv') == -1:
            file += '.csv'
        if (flag == True):
            print("---> Writing to " + file)       
        with open(file, 'w') as csv_file:
            writer = csv.writer(csv_file)
            # Writes the dictionary keys to the csv file
            writer.writerow(self._get_header(data))
            # Writes all the values of each index of dict_repos as separate rows in the csv file
            for key, value in data.items():
                row = self._object_to_list(value)
                writer.writerow(row)
        csv_file.close()

    @abc.abstractmethod
    def _object_to_list(self, value):
        return list(value.__dict__.values())

    @abc.abstractmethod
    def _object_to_dict(self, value):
        return value.__dict__

    @abc.abstractmethod
    def _get_header(self, data):
        headers = list(list(data.values())[0].__dict__.keys())
        return [header.replace(" ", "_") for header in headers]

    def __serialize_objects(self, data, file_name):
        print("---> Storing Serialized Object to " + file_name)
        # Converts all class objects to list of values
        serialized_objects = {key: self._object_to_dict(value) for key, value in data.items()}
        # Pickles data
        Process_Data.store_data(file_path=self.file_path, file_name=file_name, data=serialized_objects)

    def process_data(self, list_of_repos):
        pbar = ProgressBar()
        for repo_item in pbar(list_of_repos):
            repo_item = SimpleNamespace(**repo_item)
            self._update_statistics(repo_item)
        self._update()

    def process_data2(self, list_of_repos):
        for repo_item in list_of_repos:
            repo_item = SimpleNamespace(**repo_item)
            self._update_statistics(repo_item)
        self._update()

    @abc.abstractmethod
    def _update(self):
        print("Abstract Method that is implemented by inheriting classes")

    @abc.abstractmethod
    def _update_statistics(self, current_repository):
        print("Abstract Method that is implemented by inheriting classes")

    def save_csv(self, file_name, header, dict):
        file = self.file_path + file_name + '.csv'
        print("---> Writing to " + file)
        
        with open(file, 'w') as csv_file:
            writer = csv.writer(csv_file)            
            writer.writerow(header)
            for item in dict.items():
                writer.writerow(item)
        csv_file.close()