
from lib.System import System

from lib.Process_Data import Process_Data
from lib.Collect_Research_Data import Collect_Research_Data
from lib.TextModel import TextModel

from progressbar import ProgressBar

from pandas import DataFrame
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

class Association_Stats:
    def __init__ (self, antecedents, consequents, confidience, cluster_topics):
        self.antecedents         = antecedents       
        #self.confidience        = confidience
        self.cluster_topics      = cluster_topics
        self.consequents         = consequents

class Collect_Association(Collect_Research_Data):

    def __init__(self, file_name="Association_Stats"):
        super(Collect_Association, self).__init__(file_name)
        self.topic_list = []
        self.language_list = []
        self.unique_items = {}
        self.lang_topic_stats = {}

    def _insert_item (self, item):
        if (self.unique_items.get (item, None) == None):
            self.unique_items [item] = True
    
    def _update_statistics(self, correlation_item):

        self.topic_list.append (correlation_item.cluster_topic_id)
        self._insert_item (correlation_item.cluster_topic_id)

        combination = "".join(correlation_item.language)
        combination = combination.replace (" ", "_")
        self.language_list.append (combination)
        self._insert_item (combination)

    def _one_hot_encoding (self, df, unique_items):
        encoded_vals = []
        for index, row in df.iterrows():
            row_set = set ([row.x, row.y])

            labels = {}
            uncommons = list(set(unique_items) - row_set)
            commons = list(set(unique_items).intersection(row_set))
            for uc in uncommons:
                labels[uc] = 0
            for com in commons:
                labels[com] = 1
            encoded_vals.append(labels)
        
        return encoded_vals

    def _get_set_value (self, set_item):
        list_item = list (set_item)
        return list_item[0]
    
    def _update(self):
        unique_items = [key for key in self.unique_items.keys()]
        print ("unique_items num = %d/%d" %(len(unique_items), len(self.topic_list)))
        
        Data = {'x': self.topic_list, 'y': self.language_list}  
        df = DataFrame(Data, columns=['x', 'y'])

        encoded_vals = self._one_hot_encoding (df, unique_items)
        ohe_df = pd.DataFrame(encoded_vals)

        freq_items = apriori(ohe_df, min_support=0.01, use_colnames=True)
        print ("freq_items:")
        print (freq_items.head(100))

        rules = association_rules(freq_items, metric="confidence", min_threshold=0.01)
        print ("association_rules:")
        print (rules.head(100))

        #load cluster information
        cluster_stats = Process_Data.load_data(file_path=System.getdir_stat(), file_name="Cluster_Stats")
        #cluster_stats = Process_Data.dict_to_list(cluster_stats)

        for index, item in rules.iterrows():
            antecedents = str(self._get_set_value(item['antecedents']))
            consequents = self._get_set_value(item['consequents'])
            confidence = item['confidence']
             
            if (antecedents.isdigit()):
                cluster_topics = cluster_stats[int(antecedents)]['cluster_topics']
                self.research_stats [index] = Association_Stats (antecedents, consequents, confidence, cluster_topics)
            else:
                cluster_topics = cluster_stats[int(consequents)]['cluster_topics']
                self.lang_topic_stats [index] = Association_Stats (antecedents, consequents, confidence, cluster_topics)
        
        print ("Topic Associat to Language = %d, Language Associat to Topic = %d"\
               %(len(self.research_stats), len(self.lang_topic_stats)))

    def save_data(self):
        if (len (self.research_stats)):
            super(Collect_Association, self).save_data(self.research_stats, "Topic_Associat_to_Language")

        if (len (self.lang_topic_stats)):
            super(Collect_Association, self).save_data(self.lang_topic_stats, "Language_Associat_to_Topic")
    
    def _object_to_list(self, value):
        return super(Collect_Association, self)._object_to_list(value)
    
    def _object_to_dict(self, value):
        return super(Collect_Association, self)._object_to_dict(value)
    
    def _get_header(self, data):
        return super(Collect_Association, self)._get_header(data)

    
