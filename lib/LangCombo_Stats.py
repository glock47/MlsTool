##### Language_Stats.py #####
from lib.Process_Data import Process_Data


class LangCombo_Stats():

    Header_Names = ["id", "combination", "count", "distribution"]

    def __init__(self, id, combination):
        self.combo_id = id
        self.combination = combination
        self.count = 0
        self.distribution = 0.0
        self.language_used = len(list(combination.split(" ")))

    def update(self):
        self.count = self.count + 1

    def update_distribution(self, total_combination):
        self.distribution = self.count/total_combination      

    def object_to_list(self, key):

        # "id"
        values = [self.combo_id]

        # "combination"
        values = [self.combination]

        # "count"
        values.append(self.count)

        # "distribution"
        values.append(self.distribution)

    def object_to_dict(self, key):
        keys = LangCombo_Stats.Header_Names
        values = self.object_to_list("")
        return {key: value for key, value in zip(keys, values)}
