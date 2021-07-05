##### Repository_Stats.py #####
from lib.Collect_Research_Data import Collect_Research_Data
from lib.Process_Data import Process_Data


class Repository_Stats():
    '''
    Header_Names = ["id", "languages used", "main language",
                    "all languages", "total bytes written", "language dictionary",
                    "valid language combinations", "language combinations",
                    "owner type", "size", 
                    "open issues", "stars", "watchers", "forks", "description"]
    '''
    def __init__(self, repo):
        # This is a id that is unique to this repository only
        self.id = repo.id
        repo.language_dictionary = Process_Data.dictsort_value(repo.language_dictionary, True)
        
        # Dictionary of languages as keys with values the amount of bytes written in said language
        self.language_dictionary = repo.language_dictionary
        
        # Amount of bytes written in all of the languages used in this repository
        self.total_bytes_written = sum(list(self.language_dictionary.values()))

        # distribution of languages in current repository
        self.language_distribution = repo.language_dictionary.copy()
        for key in self.language_distribution.keys():
            self.language_distribution[key] = self.language_distribution[key]/self.total_bytes_written
        
        # A list of all the programming language names used in this repository
        self.all_languages = list(repo.language_dictionary.keys())
        
        # String value of the primary language, in bytes written, of the current repo
        self.main_language = Process_Data.calculate_top_dict_key(self.language_dictionary, None)
        # Amount of languages used in current repository instance
        self.languages_used = len(self.all_languages)
        
        # Dictionary of language combos that include this language in the key with all values set to 1
        all_languages = self.all_languages[0:1:1]
        all_languages.sort()
        language_combinations = Process_Data.create_unique_combo_list(
            all_languages,
            len(all_languages),
            max_combo_count=Collect_Research_Data.Language_Combination_Limit,
            min_combo_count=2
        )

        language_combinations_new = []
        if (True):            
            for n in range (2, 6, 1):
                n_combinations = self._get_n_combination (n)
                if (len (n_combinations) == n):      
                    language_combinations_new.append(n_combinations)
        else:
            n_combinations = self._get_n_combination (2)
            if (len(n_combinations) > 1):
                language_combinations_new.append (n_combinations)

        self.language_combinations = language_combinations_new

        
        # The type of owner of the repository
        self.owner_type = repo.owner_type
        # The amount of open issues the repository has
        self.open_issues = repo.open_issues
        # The amount of stars the repository has
        self.stars = repo.stargazers_count
        # The amount of people who are watching the repository
        self.watchers = repo.subscribers_count
        # The amount of times the repository was forked
        self.forks = repo.forks
        # The total size of the repository in KB
        self.size = repo.size
        self.topics = repo.topics
        # The description of the repository
        self.description = str(repo.description)
        self.url = repo.url

    def _get_n_combination (self, n):
        all_languages = []
        # only select language from the top languages
        for lang in self.all_languages:
            if (Process_Data.IsInTopLanguages(lang)):   
                all_languages.append (lang)

        #print (str(all_languages) + " ------ " + str(self.all_languages))
        
        #print ("all_languages: = " + str(all_languages))
        n_combination = []
        if (n <= len (all_languages)):
            n_combination = all_languages[0:n:1]
            n_combination.sort()
            #n_combination = ' '.join(n_combination)

        return n_combination
 
    
    