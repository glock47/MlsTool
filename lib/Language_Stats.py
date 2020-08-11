##### Language_Stats.py #####
from lib.Process_Data import Process_Data


class Language_Stats():

    Header_Names = ["language", "count", "count_distribution", "bytes", "bytes_distribution", "percentage_sum",
                    "percentage_avg", "percentage_std", "percentage_median", "percentage_max", "percentage_min"]

    def __init__(self, language):
        self.language_name = language

        self.count = 0
        self.count_distribution = 0.0
        
        self.bytes = 0
        self.bytes_distribution = 0.0

        self.percentage_list = []

        self.percentage_sum = 0.0
        self.percentage_avg = 0.0
        self.percentage_std = 0.0
        self.percentage_min = 0.0
        self.percentage_max = 0.0
        self.percentage_median = 0.0

    def update(self, bytes, distribution):
        self.bytes = self.bytes + bytes
        self.count = self.count + 1

        self.percentage_list.append(distribution)
        self.percentage_sum += distribution;

    def update_distribution(self, total_count, total_bytes):
        self.count_distribution = self.count/total_count
        self.bytes_distribution = self.bytes/total_bytes

        self.percentage_min = min(self.percentage_list)
        self.percentage_max = max(self.percentage_list)

        percentage_stats = Process_Data.calculate_stats (self.percentage_list)
        self.percentage_avg = percentage_stats["avg"]
        self.percentage_std = percentage_stats["std"]
        self.percentage_median = percentage_stats["median"]
        

    def object_to_list(self, key):

        # "language name"
        values = [self.language_name]

        # "count"
        values.append(self.count)

        # "count distribution"
        values.append(self.count_distribution)

        # "bytes"
        values.append(self.bytes)

        # "bytes distribution"
        values.append(self.bytes_distribution)

        # "percentage sum"
        values.append(self.percentage_sum)

        # "percentage avg"
        values.append(self.percentage_avg)

        # "percentage std"
        values.append(self.percentage_std)

        # "percentage median"
        values.append(self.percentage_median)

        # "percentage max"
        values.append(self.percentage_max)

        # "percentage min"
        values.append(self.percentage_min)
        
        return values

    def object_to_dict(self, key):
        keys = Language_Stats.Header_Names
        values = self.object_to_list("")
        return {key: value for key, value in zip(keys, values)}
