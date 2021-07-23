
from lib.System import System
from lib.Process_Data import Process_Data
from datetime import datetime, timedelta
from time import sleep
import requests
from progressbar import ProgressBar
# Reads/Writes in a CSV formatted file
import csv  # reader()
import sys  # sys.maxsize
import os
import pandas as pd
# Allows code to read in large CSV files
csv.field_size_limit(sys.maxsize)

from lib.TextModel import TextModel
text_model = TextModel()


"""
       * Overall Github API V3 Guide: https://developer.github.com/v3/

       * Repository Search Query Parameters: https://help.github.com/en/articles/searching-for-repositories

           stars: >= n           -> matches repositories with the at least n stars
           pushed: >= n          -> matched repositories that have last pushed on or after yyyy-mm-dd
           created: >= n         -> matched repositories that were created on or after yyyy-mm-dd
           is: public/private    -> matches repositories that obey this condition
           mirror: false/true    -> matches repositories that obey this boolean
           archived: false/true  -> matches repositories that obey this boolean

       * API Parameters:

           https://developer.github.com/v3/search/#constructing-a-search-query
           sort = stars, forks, help-wanted-issues, or updated
           order = desc, asc

           https://developer.github.com/v3/#pagination
           page: n
           per_page: 1-100
"""

START_YEAR  = System.START_YEAR
END_YEAR    = System.END_YEAR
MIN_RELEASE = (1 + END_YEAR-START_YEAR)
PAGE_COUNT  = System.PAGE_COUNT
PER_PAGE    = System.PER_PAGE

UPDATE_ACTIVE = "active"
UPDATE_MAX    = "max"
UPDATE_MIN    = "min"

class Github_API():

    Fields_Wanted = ['id', 'size', 'forks', 'clone_url',
                     'open_issues', 'subscribers_count',
                     'stargazers_count', 'language_dictionary',
                     'owner_type', 'url', 'created_at',
                     'pushed_at', 'topics', 'description']

    def __init__(self, file_name='Repository_List'):
        self.list_of_repositories = []
        self.file_name = file_name
        self.file_path = System.getdir_collect ()
        self.updated_time = {}
        self.cur_year = 0
        self.date_created = ""
        self.username = ""
        self.password = ""
        self.init_star  = 30000
        self.delta_star = 100
        self.min_star   = 1000

    def collect_repositories(self):
        self.collect_repositories_by_year()

    def collect_repository_versions(self):
        print("Updating Repository Versions...")
        
        self.list_of_repositories = Process_Data.load_data(file_path=System.getdir_collect_origin(), file_name='Repository_List')

        self.update_repositories(System.get_release(), System.VERSION_REPO_NUM) 
        list_of_languages = self.update_languages()
        self.clean_repositories(list_of_languages)
        self.remove_invalid_repositories()

        file_name = 'Repository_List'
        Process_Data.store_data(file_path=self.file_path, file_name=file_name, data=self.list_of_repositories)
        self.write_csv(file_name)

    def collect_repositories_by_year(self, year=0):
        if (year):
            self.init_star  = 1500
            self.delta_star = 50
            self.min_star   = 50
        
        # Obtains initial 'unclean' repositories
        self.get_repos_by_year(year)
        
        # Initial amount of 'unclean' repositories obtained
        original_repo_count = len(self.list_of_repositories)
        print("%d Repositories have been read in from Github" % original_repo_count)
        # Updates some of the values and adds new ones for each repository
        self.update_repositories()
        
        # get releases of all repositories
        #self.list_of_repositories = self.get_repo_releases(self.list_of_repositories)
        
        # Updates all of the language of each repository to include all languages used and not just the top one
        list_of_languages = self.update_languages()
        # Changes some of the repository values that need to be further cleaned
        self.clean_repositories(list_of_languages)
        # Removes all the repositories that do not meet the minimum requirements to be deemed 'clean'
        self.remove_invalid_repositories()

        # Obtains and displays the final amount of repositories compared to the starting amount
        if (year):
            self.list_of_repositories = self.list_of_repositories[1:1001:1]
        final_repo_count = len(self.list_of_repositories)
        print("Valid Repositories Remaining %d of %d [%.2f%%]" % (final_repo_count, original_repo_count,
                                                                  (final_repo_count / original_repo_count) * 100))
        Process_Data.store_data(file_path=self.file_path, file_name=self.file_name, data=self.list_of_repositories)
        self.write_csv()

    def update_repositories(self, field='url', repo_num=65535):
        print("Updating Repository Data[%s]..." %field)
        pbar = ProgressBar()
        index = 0
        for repo in pbar(self.list_of_repositories):
            url = repo[field]
            #print ("---> update_repositories: Url=" + url)
            result = self.http_get_call(url)
            self.list_of_repositories[index] = dict(result)
            index += 1
            if (index >= repo_num):
                break

    def update_languages(self):
        print("Updating Repository Language Data...")
        language_dict = {}
        pbar = ProgressBar()
        for repo in pbar(self.list_of_repositories):
            #print ("repo = " + str(repo))
            url = repo['languages_url']
            repo['language'] = self.http_get_call(url)
            #print ("---> update_languages: Url=" + url + "Language=" + str(repo['language']))
            language_dict.update(repo['language'])
        return [lang.lower() for lang in language_dict.keys()] 

    def get_date_updated(self, year=0, months=6):
        #print("Date Last Updated Time-Span (months): ", end="")
        #months = int(input())
        print("Date Update Time-Span (months): %d"  %months)
        days = months * 30

        date = datetime.strptime("2021-06-30", "%Y-%m-%d") - timedelta(days=days)
        self.updated_time[UPDATE_MAX] = "+pushed:<=" + date.strftime("%Y-%m-%d")
        self.updated_time[UPDATE_ACTIVE] = "+pushed:>=" + date.strftime("%Y-%m-%d")

        date = date - timedelta(days=12*30)
        self.updated_time[UPDATE_MIN] = "+pushed:>=" + date.strftime("%Y-%m-%d")
        self.cur_year = year

    def get_date_created(self):
        #print("Date Created Time-Span (years): ", end="")
        #years = int(input())
        years = (END_YEAR - 2018) + 1
        print("Date Created Time-Span (years): %d"  %years)
        days = years * 365.24
        date = datetime.today() - timedelta(days=days)
        self.date_created = "+created:<=" + date.strftime("%Y-%m-%d")

    def get_basic_auth(self):
        if (os.getenv("GIT_NAME", "None") != "None" and os.getenv("GIT_PWD", "None") != "None"):
            print("Github Username:****** \r\n", end="")
            self.username = os.environ["GIT_NAME"]
            print("Github Password:****** \r\n", end="")
            self.password = os.environ["GIT_PWD"] 
        else:        
            print("Github Username: ", end="")
            self.username = str(input())
            print("Github Password: ", end="")
            self.password = str(input())

    def remove_invalid_repositories(self):
        updated_repos = []
        for repo in self.list_of_repositories:
            language_count = len(repo['language_dictionary'])
            character_count = len(str(repo['description']))
            if language_count > 1 and character_count > 8:
                updated_repos.append(repo)
        self.list_of_repositories = updated_repos

    def clean_repositories(self, langs):
        index = 0
        for repo in self.list_of_repositories:
            topics = [topic.lower() for topic in repo['topics']]
            # Removes all topics that are just programming language names
            repo['topics'] = [topic for topic in topics if topic not in langs]
            # Makes all languages lowercase
            language_dictionary = {language.lower(): val for language, val in repo['language'].items()}
            repo['language_dictionary'] = Process_Data.dictsort_key(language_dictionary)
            # Makes all descriptions proper strings
            description = str(repo['description'])
            repo['description'] = text_model.clean_text (description)
            # Sets 'owner' field to owner's 'type'
            repo['owner_type'] = repo['owner']['type']
            self.list_of_repositories[index] = {field: repo[field] for field in Github_API.Fields_Wanted}
            index += 1

    def http_get_call(self, url):
        result = requests.get(url,
                              auth=(self.username, self.password),
                              headers={"Accept": "application/vnd.github.mercy-preview+json"})
        if (result.status_code != 200 and result.status_code != 422):
            print("Status Code %s: %s, URL: %s" % (result.status_code, result.reason, url))
            # Sleeps program for one hour and then makes call again when api is unrestricted
            sleep(300)
            return self.http_get_call(url)
        return result.json()

    def get_page_of_repos(self, updated_key, page_num, star_count, sort='asc'):
        url = 'https://api.github.com/search/repositories?' \
              + 'q=stars:' + star_count + '+is:public+mirror:false'\
              + self.updated_time[updated_key] 

        if (updated_key == UPDATE_ACTIVE):
            url += self.date_created
        
        url += '&sort=stars&per_page=' + str(PER_PAGE) + '&order=' + sort + '&page=' + str(page_num)  # 4250
        
        if page_num == 1:
            print(url)
        return self.http_get_call(url)

    def get_page_of_release(self, url, page_num):
        release_url = url + '/releases?' + 'per_page=100' + '&page=' + str(page_num)  # 4250
        if page_num == 1:
            print(release_url)
        return self.http_get_call(release_url)

    def get_repos(self, updated_key):
        print("---> [%s]Obtaining Repositories from Github..." %updated_key)
        page_count = PAGE_COUNT+1        
        list_of_repositories = []

        init_star = self.init_star
        while init_star > self.min_star:
            b_star = init_star - self.delta_star
            e_star = init_star
            init_star = init_star - self.delta_star

            star_count = str(b_star) + ".." + str(e_star)
            star_repos = []
            star_IDS   = []
            for sort in ['asc', 'desc']:      
                # Reads in 100 repositories from 10 pages resulting in 1000 repositories
                for page_num in range(1, page_count, 1):
                    # Gets repos from github in json format
                    json_repos = self.get_page_of_repos(updated_key, page_num, star_count, sort)
                    # json_repos['items'] = list of repo dictionary objects OR is not a valid key
                    if 'items' in json_repos:
                        # Append new repos to the end of 'list_of_repositories'
                        repos = json_repos['items']
                        if len (star_IDS) == 0:
                            star_repos += repos
                            list_of_repositories += repos
                        else:
                            for rp in repos:
                                if rp['id'] in star_IDS:
                                    continue
                                star_repos.append (rp)
                                list_of_repositories.append (rp)
                        if (len(repos) < PER_PAGE) or page_num == 10:
                            print ("[%s][%d] get repo counts = %d / %d" %(star_count, page_num, len(repos), len (list_of_repositories)))
                            break
                    else:
                        # If 'items' is not a valid key then there are no more repos to read in
                        break
                if len (star_repos) < 1000:
                    break
                for repo in star_repos:
                    star_IDS.append (repo['id'])
        return list_of_repositories

    def get_active_repos(self):
        self.get_basic_auth()
        self.get_date_created()
        self.get_date_updated()
        self.list_of_repositories = self.get_repos(UPDATE_ACTIVE)

    def get_repos_by_year(self, year=0):
        if (year == 0):
            self.get_active_repos()
        else:
            print ("[%d]" %year, end = "")
            self.get_basic_auth()
            self.get_date_created()
            
            months = (2020-year) * 12
            self.get_date_updated (year, months)
            
            #get repositories end at the end of the year
            repositories_max = self.get_repos(UPDATE_MAX)
            print ("****** repositories_max  =%d" %len(repositories_max))

            list_of_repositories = []
            for repo in repositories_max:
                if (repo.get('pushed_at', None) == None):
                    continue
                push_time = datetime.strptime(repo['pushed_at'], '%Y-%m-%dT%H:%M:%SZ').year
                if ((push_time == self.cur_year) or (self.cur_year == START_YEAR and push_time <= self.cur_year)):
                    list_of_repositories.append(repo)
                    
            print ("[%d]collect repositories %d/%d" %(self.cur_year, len(list_of_repositories), len(repositories_max)))
            self.list_of_repositories = list_of_repositories[1:1501:1]

    def init_release_field(self, repo):
         for year in range(START_YEAR, END_YEAR+1, 1):
            key = "release" + str(year)
            repo[key] = ""

    def is_version_valid(self, repo):
        for year in range(START_YEAR, END_YEAR+1, 1):
            key = "release" + str(year)
            if (repo.get(key, None) == ""):
                return False
        return True
    
    def get_repo_releases(self, list_of_repositories):
        #add new Fields_Wanted
        for year in range(START_YEAR, END_YEAR+1, 1):
            key = System.RELEASE + str(year)
            Github_API.Fields_Wanted.append(key)

        version_repositories = []
            
        pbar = ProgressBar()
        repo_index = 0
        repo_num = len(list_of_repositories)
        for repo in pbar(list_of_repositories):
            print("[%d/%d]" %(repo_index, repo_num), end=" ")
            repo_index = repo_index + 1
            
            url = repo['url']
            repo_releases = []
            for page_num in range(1, 10, 1):
                releases = self.get_page_of_release(url, page_num)
                if (releases):
                    repo_releases = repo_releases + releases
                else:
                    break
            
            self.init_release_field(repo)
            if (len(repo_releases) < MIN_RELEASE):
                continue

            #classifier releases by year
            for release in repo_releases:
                url  = release['url']           
                
                publish_time  = datetime.strptime(release['published_at'], '%Y-%m-%dT%H:%M:%SZ').date()
                year = publish_time.year
                if (year > END_YEAR or year < START_YEAR):
                    continue

                key = System.RELEASE + str(year)
                if (repo.get(key, None) == ""):
                    #print ("[%d]set key = %s" %(repo['id'], key))
                    repo[key] = url

            if (self.is_version_valid(repo)):
                version_repositories.append(repo)

        return version_repositories
                

    def write_csv(self, file_name=None):
        if (file_name == None):
            file_name = self.file_name
        file = self.file_path + file_name + '.csv'
        print("---> Writing to" + file)       
        with open(file, 'w') as csv_file:
            writer = csv.writer(csv_file)
            # Writes the dictionary keys to the csv file
            writer.writerow(Github_API.Fields_Wanted)
            # Writes all the values of each index of dict_repos as separate rows in the csv file
            for repository in self.list_of_repositories:
                row = []
                for field in Github_API.Fields_Wanted:
                    row.append(repository[field])
                writer.writerow(row)
        csv_file.close()

    def update_repolist(self):
        list_of_repositories = []
        file = self.file_path + self.file_name + '.csv'
        df = pd.read_csv(file)
        for index, row in df.iterrows():
            CmmtFile = System.cmmt_file (row['id'])
            if System.is_exist(CmmtFile) == False:
                continue
            row['language_dictionary'] = eval (row['language_dictionary'])
            row['topics'] = eval (row['topics'])
            list_of_repositories.append (row)
        self.list_of_repositories = list_of_repositories

        file_name = 'Repository_List'
        Process_Data.store_data(file_path=self.file_path, file_name=file_name, data=self.list_of_repositories)
        self.write_csv(file_name)
        print ("@@@@ Total %d repositories collected...." %len(list_of_repositories))

