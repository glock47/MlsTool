##### Collect_RQ2_Data.py #####

from lib.Collect_Research_Data import Collect_Research_Data
from lib.Description_Stats import Description_Stats

class Collect_DiscripStats(Collect_Research_Data):

    def __init__(self, file_name="Description_Stats"):
        self.language_map = {}
        super(Collect_DiscripStats, self).__init__(file_name=file_name)

    def _update_statistics(self, repo_item):
        
        if (len(repo_item.language_combinations) < 1):
            return
        
        repo_id = repo_item.id
        discrip_stats = Description_Stats(repo_item)
        if (discrip_stats.has_subject()):
            self.research_stats[repo_id] = discrip_stats

        for lang in repo_item.all_languages:
            if (self.language_map.get (lang, None) == None):
                self.language_map[lang] = True

    def _update(self):
        for discrip_stat in self.research_stats.values():
            discrip_stat.subjects = self._update_values (discrip_stat.subjects)
            discrip_stat.processed_text = self._update_values (discrip_stat.processed_text)
            
    def _update_values (self, value_list):
        values = []
        for val in value_list:
            if (self.language_map.get (val, None) == True):
                continue
            values.append (val)
        return values                

    def save_data(self):
        super(Collect_DiscripStats, self).save_data(self.research_stats)

    def _object_to_list(self, value):
        return super(Collect_DiscripStats, self)._object_to_list(value)

    def _object_to_dict(self, value):
        return super(Collect_DiscripStats, self)._object_to_dict(value)

    def _get_header(self, data):
        return super(Collect_DiscripStats, self)._get_header(data)
