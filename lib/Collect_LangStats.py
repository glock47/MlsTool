##### Collect_RQ1_Data.py #####
from lib.Process_Data import Process_Data

from lib.Collect_Research_Data import Collect_Research_Data
from lib.Language_Stats import Language_Stats

class Collect_LangStats(Collect_Research_Data):

    def __init__(self, file_name='Language_Stats'):
        super(Collect_LangStats, self).__init__(file_name=file_name)
        self.all_language_count = 0
        self.all_language_bytes = 0
        self.repo_count = 0

    def _update_statistics(self, repo_item):
        #if repo_item.languages_used > Collect_Research_Data.Language_Combination_Limit:
        #    return

        self.repo_count += 1
        for language, distribution in repo_item.language_distribution.items():
            if language not in self.research_stats:
                self.research_stats[language] = Language_Stats(language)
                
            lang_bytes = repo_item.language_dictionary[language]
            self.research_stats[language].update(lang_bytes, distribution)
                
            self.all_language_count = self.all_language_count + 1
            self.all_language_bytes = self.all_language_bytes + lang_bytes

    def _sort_by_percent_sum (self):
        #collect items whose count > 1
        languages = {}
        for lang, stat in self.research_stats.items():
            languages[lang] = stat.percentage_sum

        #sort dict
        return Process_Data.dictsort_value (languages, True)
    
    def _update(self):
        for lang, lang_stat in self.research_stats.items():
            lang_stat.update_distribution(self.repo_count, self.all_language_bytes)

        sort_languages = self._sort_by_percent_sum ()
        research_stats = {}
        for lang in sort_languages.keys():
            research_stats[lang] = self.research_stats[lang]
        self.research_stats = research_stats

    def _get_header(self, data):
        return Language_Stats.Header_Names

    def _object_to_list(self, value):
        return value.object_to_list("")

    def _object_to_dict(self, value):
        return value.object_to_dict("")

    def save_data(self):
        super(Collect_LangStats, self).save_data(self.research_stats)

