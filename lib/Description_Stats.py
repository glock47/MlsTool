##### Description_Stats.py #####

from lib.Process_Data import Process_Data
from lib.TextModel import TextModel

txt_model = TextModel()

class Description_Stats():
    '''
    Header_Names = ["id", "subjects", "processed text", "language combinations"]
    '''
    def __init__(self, repo):
        self.id = repo.id

        #clean text
        clean_text = txt_model.clean_text(repo.description)

        #get all nouns as subjects
        self.subjects = txt_model.subject(clean_text)
        #print ("TextModel.subjects = %s" %(str(self.subjects)))
 
        self.processed_text = txt_model.preprocess_text(clean_text) + repo.topics
        #print ("TextModel.preprocess_text = %s" %(self.processed_text))  

        # List of language combos
        self.language_combinations = repo.language_combinations

        self.description = clean_text

    def has_subject(self):
        if (self.subjects):
            return True
        else:
            return False

    