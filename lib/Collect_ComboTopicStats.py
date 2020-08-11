
from lib.System import System

from lib.Process_Data import Process_Data
from lib.Collect_Research_Data import Collect_Research_Data
from lib.TextModel import TextModel

from progressbar import ProgressBar
from scipy.stats import spearmanr
from scipy.stats import kendalltau


class Topics_Stats():
    def __init__(self, id, topic):
        self.id    = id
        self.topic = topic
        self.count = 0
        self.distribution  = 0.0

    def update (self):
        self.count = self.count + 1

    def update_distribution (self, topic_num):
        self.distribution= self.count/topic_num


class RepoCluster_Stats():
    def __init__(self, cluster, repo_id, subjects, topics, combinations):
        self.cluster = cluster
        self.repo_id = repo_id
        self.subjects= subjects
        self.topics  = topics
        self.combinations = combinations

class Cluster_Stats():
    def __init__(self, label_id, repo_num, cluster_topics):
        self.label_id = label_id
        self.repository_count = repo_num
        self.cluster_topics = cluster_topics
        self.languages = []
        self.combinations = {}

    def update (self, combinations):
        for combo in combinations:
            combo_item = self.combinations.get (combo, None)
            if (combo_item == None):
                self.combinations[combo] = 1
            else:
                self.combinations[combo] = self.combinations[combo] + 1

            for lang in combo.split(" "):
                if (lang not in self.languages):
                    self.languages.append (lang )

    def update2 (self, combinations, cluster_topics):
        self.update (combinations)
        self.repository_count += 1
        self.cluster_topics = []
        self.cluster_topics.append (cluster_topics)

class Correlation_Data():
    def __init__(self, cluster_topic, cluster_topic_id, topic, topic_id, lang, lang_id):
        self.cluster_topic = cluster_topic
        self.cluster_topic_id = cluster_topic_id

        self.topic    = topic
        self.topic_id = topic_id
        
        self.language     = lang
        self.language_id = lang_id

    def get_langcombo (self):
        return self.language, self.language_id

    def update_langcombo (self, lang, lang_id):
        self.language     = lang
        self.language_id = lang_id
        


class TopicCombo_Matrix():
    def __init__(self, topic):
        self.topic    = topic
        self.conbinations = {}

    def update (self, lang_combo, lang_combo_count):  
        if (self.conbinations.get(lang_combo, None) == None):
            self.conbinations[lang_combo] = lang_combo_count
        else:
            self.conbinations[lang_combo] += lang_combo_count

class Spearman_Stats():
    def __init__(self, correlation_data):
        self.topic_list = []
        self.combo_list = []

        for index, data in correlation_data.items():          
            self.combo_list.append(data.language_id)
            self.topic_list.append(data.cluster_topic_id)

        coefficient, p_value = spearmanr(self.topic_list, self.combo_list)
        print("---> Spearmans correlation coefficient= %.3f, p_value = %.3f" % (coefficient, p_value))
        self.topic_list = [0,1,2,3,4,5,4,6]
        self.combo_list = [5,7,8,11,13,14,13,13]
        coefficient, p_value = spearmanr(self.topic_list, self.combo_list)
        print("---> TEST Spearmans cospearmanrrrelation coefficient= %.3f, p_value = %.3f" % (coefficient, p_value))
        print ("")

class Collect_ComboTopicStats(Collect_Research_Data):

    def __init__(self, file_name="ComboTopic_Stats"):
        super(Collect_ComboTopicStats, self).__init__(file_name)
        self.text_model = TextModel()

        self.discrip_items = []
        self.description_texts = []
        self.conbinations = []
        
        self.repocluster_stats = {}
        self.cluster_stats = {}
        self.label_reponum = {}

        self.topic_stats = {}

        self.correlation_data = {}

    def _replace_language (self, list, replace_dict):
        list = " ".join (list)
        list = self.text_model.preprocess_text (list, 0)
        new_list = []
        for str in list:
            rp_val = replace_dict.get (str, None)
            if (rp_val != None):
                new_list.append (rp_val)
            else:
                new_list.append (str)
        return new_list
    
    def _update_statistics(self, discrip_item):

        self.discrip_items.append(discrip_item)
        self.description_texts.append(discrip_item.subjects)

        replace_dict = {"c":"c_language", "c++":"cpp"}
        combinations = self._replace_language (discrip_item.language_combinations, replace_dict) 
        combinations = " ".join (combinations)
        self.conbinations.append(combinations)

    def _tfidf_cluster ():
        #tf-idf cluster
        cluster = self.text_model.tfidf_cluster_text(self.description_texts)

        self._update_repocluster_stats(cluster, self.text_model.cluster_text_labels())
        self._update_cluster_stats(cluster)
        self._update_topics_stats()

        #spearman statistic
        self._update_correlation_data()
        spearman_stat = Spearman_Stats(self.correlation_data)

    
    def _update(self):   

        #word2vec cluster
        documents_words, cluster_labels = self.text_model.word2vec_cluster_text(self.description_texts)

        self._update_repocluster_stats2(documents_words, cluster_labels)
        self._update_cluster_stats2 (documents_words, cluster_labels)
        self._update_correlation_data2(documents_words, cluster_labels)
  
    def _update_cluster_stats2(self, documents_words, cluster_labels):
        pjt_id = 0
        for label in cluster_labels:
            words = " ".join(documents_words[pjt_id])
            combinations  = self.repocluster_stats[pjt_id].combinations
            
            cluster_stat = self.cluster_stats.get (label, None)
            if (cluster_stat == None):
                cluster_stat = Cluster_Stats(label, 0, words)
                self.cluster_stats[label] = cluster_stat
            
            cluster_stat.update2 (combinations, words)
            pjt_id += 1

        print ("---> Sort language combinations of each cluster...")
        pbar = ProgressBar()
        for id, item in pbar(self.cluster_stats.items()):
            item.combinations = Process_Data.dictsort_value (item.combinations, True)

           

    def _update_repocluster_stats2(self, documents_words, cluster_labels):
            print ("---> Update cluster of repository...")
            pbar = ProgressBar()
            index = 0
            for item in pbar(self.discrip_items):
                label = cluster_labels[index]
                ctext = RepoCluster_Stats(label, item.id, item.subjects, documents_words[index], item.language_combinations)
                self.repocluster_stats[index] = ctext
    
                if (self.label_reponum.get(label, None) == None):
                    self.label_reponum[label] = 1
                else:
                    self.label_reponum[label] = self.label_reponum[label] + 1
    
                index = index + 1

    def get_lang_set (self, combo):
        language = []
        for lang in combo.split(" "):
            language.append (lang)
        return set (language)
        
    def _update_correlation_data2(self, documents_words, cluster_labels):
        pjt_id = 0
        for document in documents_words:
            combinations  = self.repocluster_stats[pjt_id].combinations
            cluster_topic = " ".join(documents_words[pjt_id])
            cluster_topic_id = cluster_labels[pjt_id]
            self.correlation_data[pjt_id] = Correlation_Data (cluster_topic, cluster_topic_id, 0, 0, combinations, 0) 
            pjt_id += 1

        return
        #update combinations, interaction
        self._interact_combinations()
        
    def _interact_combinations (self):
        
        for cor in self.correlation_data.values ():
            lang, lang_id = cor.get_langcombo ()
            lang_set = self.get_lang_set (lang[0])         
            lang_len = len (lang_set)
    
            for item in self.correlation_data.values ():
                if ((cor == item) or (cor.topic_id != item.topic_id)):
                    continue
                
                la, id = item.get_langcombo ()
                la_set = self.get_lang_set (la[0])
                la_len = len (la_set)
                if (la_len >  lang_len):
                    continue
    
                new_lang = list(lang_set.intersection(la_set))
                if (len(new_lang) == len(la_set)):
                    item.update_langcombo (lang, lang_id)
            
    
    def _update_correlation_data(self):

        #topic tfidf matrix
        description_texts = []
        for description in self.description_texts:
            description_texts.append (" ".join (description))

        description_texts = description_texts
        topic_tfidf = self.text_model.get_tfidf_matrix(description_texts)
        topic_set   = self.text_model.get_tfidf_features()
        #print ("%d--->%s" %(len(topic_set), str(topic_set)))
        #print (topic_tfidf)

        #combination tfidf matrix
        conbinations = self.conbinations
        combo_tfidf = self.text_model.get_tfidf_matrix(conbinations)
        combo_set   = self.text_model.get_tfidf_features()
        #print ("%d--->%s" %(len(combo_set), str(combo_set)))
        #print (combo_tfidf)

        #update weight for each combination and topic value 
        for i in range(len(combo_tfidf)):
            combo_weight = 0
            for j in range(len(combo_set)):
                combo_weight += combo_tfidf[i][j]

            max_topic = ""
            max_topic_val = 0
            for k in range(len(topic_set)):
                if (max_topic_val < topic_tfidf[i][k]):
                    max_topic_val = topic_tfidf[i][k]
                    max_topic     = topic_set[k]         

            combinations  = self.repocluster_stats[i].combinations
            cluster_topic = self.repocluster_stats[i].topics[0]
            cluster_topic_id = self.topic_stats[cluster_topic].id
            self.correlation_data[i] = Correlation_Data (cluster_topic, cluster_topic_id,\
                                                         max_topic, max_topic_val,\
                                                         combinations, combo_weight)    

    
    def _update_repocluster_stats(self, cluster, cluster_labels):
        print ("---> Update cluster of repository...")
        pbar = ProgressBar()
        index = 0
        for item in pbar(self.discrip_items):
            label = cluster_labels[index]
            ctext = RepoCluster_Stats(label, item.id, item.subjects, cluster[label], item.language_combinations)
            self.repocluster_stats[index] = ctext

            if (self.label_reponum.get(label, None) == None):
                self.label_reponum[label] = 1
            else:
                self.label_reponum[label] = self.label_reponum[label] + 1

            index = index + 1

    def _update_cluster_stats(self, cluster):
        for id, topics in cluster.items():
            cluster_stat = Cluster_Stats(id, self.label_reponum[id], topics)
            self.cluster_stats[id] = cluster_stat

        print ("---> Statistic cluster and language combinations...")
        pbar = ProgressBar()
        for id, item in pbar(self.repocluster_stats.items()):
            cluster_stat = self.cluster_stats[item.cluster]
            cluster_stat.update (item.combinations)

        print ("---> Sort language combinations of each cluster...")
        pbar = ProgressBar()
        for id, item in pbar(self.cluster_stats.items()):
            item.combinations = Process_Data.dictsort_value (item.combinations, True)


    def _update_topics_stats(self):
        topic_id  = 0
        topic_num = 0
        for id, repocluster in self.repocluster_stats.items():
            for topic in repocluster.topics:
                topic_stat = self.topic_stats.get(topic, None) 
                if (topic_stat == None):
                    topic_stat = Topics_Stats(topic_id, topic)
                    self.topic_stats[topic] = topic_stat
                    topic_id = topic_id + 1
                topic_stat.update()
                topic_num += 1

        for topic_stat in self.topic_stats.values():
            topic_stat.update_distribution (topic_num)

    def save_data(self):
        super(Collect_ComboTopicStats, self).save_data(self.repocluster_stats, "RepoCluster_Stats")
        super(Collect_ComboTopicStats, self).save_data(self.cluster_stats, "Cluster_Stats")
        #super(Collect_ComboTopicStats, self).save_data(self.topic_stats, "Topic_Stats")
        super(Collect_ComboTopicStats, self).save_data(self.correlation_data, "Correlation_Data")
    
    def _object_to_list(self, value):
        return super(Collect_ComboTopicStats, self)._object_to_list(value)
    
    def _object_to_dict(self, value):
        return super(Collect_ComboTopicStats, self)._object_to_dict(value)
    
    def _get_header(self, data):
        return super(Collect_ComboTopicStats, self)._get_header(data)

    
