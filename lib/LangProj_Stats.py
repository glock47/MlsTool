##### Language_Stats.py #####
from lib.Process_Data import Process_Data


class LangProj_Stats():

    Header_Names = ["language count", "project count", "distribution"]

    def __init__(self, language_count):
        self.language_count = language_count
        
        self.distribution = 0.0
        self.project_count = 0

    def update(self):
        self.project_count = self.project_count + 1

    def update_distribution(self, total_project):
        self.distribution = self.project_count/total_project      

    def object_to_list(self, key):

        # "language count"
        values = [self.language_count]

        # "project count"
        values.append(self.project_count)

        # "distribution"
        values.append(self.distribution)

    def object_to_dict(self, key):
        keys = LangProj_Stats.Header_Names
        values = self.object_to_list("")
        return {key: value for key, value in zip(keys, values)}
