# List of all stop words in the English Language
import nltk
nltk.download('stopwords');nltk.download('brown');nltk.download('punkt');nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.cluster import KMeansClusterer
from sklearn.cluster import AffinityPropagation


import numpy as np
from gensim.models import Word2Vec
from gensim.models.phrases import Phraser, Phrases

from nltk.stem import WordNetLemmatizer
# lemmatization words using the NLTK library
lemmatizer = WordNetLemmatizer()

from textblob import TextBlob

from progressbar import ProgressBar


# Regex
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer

from sklearn.feature_extraction.text import TfidfTransformer

from sklearn.cluster import MiniBatchKMeans, KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

import matplotlib.pyplot as plt

import pandas as pd
from pandas import DataFrame



class TextModel:

    def __init__(self):
        self.cluster_num    = 50
        self.claster_labels = None
        self.word_model     = None

    def clean_text(self, text, length=1024):
        # Change all the text to lower case
        text = text.lower()
        # Converts all '+' and '/' to the word 'and'
        text = re.sub(r'[+|/]', ' and ', text)
        # Removes all characters besides numbers, letters, and commas
        text = re.sub(r'[^\w\d,]', ' ', text)
        # Word Tokenization
        words = text.split()
        # Remove Non-alpha text
        words = [re.sub(r'[^a-z]', '', word) for word in words if word.isalnum()]
        if len (words) > length:
            words = words[0:length]
        # Joins tokenized string into one string
        text = ' '.join(words)
        return text

    def subject(self, text, min_len=4):
        text_blob = TextBlob(text)
        noun_str  = ' '.join(list(text_blob.noun_phrases))
        words = self.preprocess_text(noun_str, min_len)
        return words        
        
    def preprocess_text(self, text, min_len=4):  
        
        # Word Tokenization
        words = nltk.word_tokenize(text)

        # Word Lemmatization
        words = [lemmatizer.lemmatize(word) for word in words]
        
        # Removes all stop words from text and words that are less than two characters in length
        words = [word for word in words if word not in stopwords.words('english') and len(word) > min_len]
        '''
            Lemmatization: removes inflectional endings only and
            to return the base or dictionary form of a word, which is known as the lemma
        '''

        return words

    def _tfidf_vectorizer(self):
        '''
        max_df: this is the maximum frequency within the documents a given feature can have to be used in the tfi-idf matrix.
            If the term is in greater than 80% of the documents it probably cares little meanining (in the context of film synopses)
        min_df: Here I pass 0.2; the term must be in at least 20% of the document.
        ngram_range: this just means I'll look at unigrams and bigrams
        '''
        vectorizer = TfidfVectorizer(
            max_df=0.5,
            #min_df=0.2,
            max_features=1000,
            use_idf=True,
            # Try to strip accents from characters. Using unicode is slightly slower but more comprehensive than 'ascii'
            strip_accents='unicode',
            # Analyzes words and not characters
            analyzer='word',
            # One and Two worded tokens
            ngram_range=(1, 2),
            # These three parameters are set so they do not alter the already tokenized object to be fill/transform
            tokenizer=lambda x: x,
            preprocessor=lambda x: x,
            token_pattern=None
        )
        return vectorizer

    def tfidf_cluster_text(self, words):

        sample_num = len (words)
        #self.cluster_num = sample_num - 5
        print ("****************TF-IDF: sample num = %d cluster_num = %d ****************" %(sample_num, self.cluster_num))

        tfidf_model = self._tfidf_vectorizer()
        self.word_model = tfidf_model
        
        tfidf_matrix = tfidf_model.fit_transform(words)

        km_model = KMeans(n_clusters=self.cluster_num)
        km_model.fit(tfidf_matrix)
        score_base = silhouette_score(tfidf_matrix, labels=km_model.predict(tfidf_matrix))

        pbar = ProgressBar()
        for n in pbar(range (1, 10, 1)):
            model = KMeans(n_clusters=self.cluster_num)
            model.fit(tfidf_matrix)
            score = silhouette_score(tfidf_matrix, labels=model.predict(tfidf_matrix))
            if (score > score_base):
                score_base = score
                km_model = model
                
        print("The Silhouette Coefficient [1,-1]: %.5f" % score_base)
        self.claster_labels = km_model.labels_.tolist()

        cluster = {}
        order_centroids = km_model.cluster_centers_.argsort()[:, ::-1]
        terms = tfidf_model.get_feature_names()
        for i in range(self.cluster_num):
            cluster_words = []
            for ind in order_centroids[i, :1]:
                cluster_words.append(terms[ind])
            cluster[i] = cluster_words
        
        return cluster

    def cluster_text_labels(self):
        return self.claster_labels


    def get_tfidf_matrix(self, words):

        self.word_model = CountVectorizer()
        X = self.tfidf_model.fit_transform(words)
        
        transformer = TfidfTransformer()
        tfidf = transformer.fit_transform(X)

        return (tfidf.toarray())

    def get_tfidf_features(self):
        return self.word_model.get_feature_names()

    def average_word_vectors(self, words, model, vocabulary, num_features):    
        feature_vector = np.zeros((num_features,),dtype="float64")
        nwords = 0.        
        for word in words:
            if word in vocabulary: 
                nwords = nwords + 1.
                feature_vector = np.add(feature_vector, model[word])
        
        if nwords:
            feature_vector = np.divide(feature_vector, nwords)
            
        return feature_vector
        
   
    def averaged_word_vectorizer(self, corpus, model, num_features):
        vocabulary = set(model.wv.index2word)
        features = [self.average_word_vectors(tokenized_sentence, model, vocabulary, num_features)
                        for tokenized_sentence in corpus]
        return np.array(features)

    def document_word(self, words, model, vocabulary, num_features):    
        doc_words = []     
        for word in words:
            if word in vocabulary: 
                doc_words.append (word)
            
        return doc_words
 
    def get_document_word(self, corpus, model, num_features):
        vocabulary = set(model.wv.index2word)
        documents_words = [self.document_word(tokenized_sentence, model, vocabulary, num_features)
                           for tokenized_sentence in corpus]
        return np.array(documents_words)

    def word2vec_cluster_text(self, words):
        
        sample_num = len (words)
        print ("****************WORD2VEC: sample num = %d cluster_num = %d ****************" %(sample_num, self.cluster_num))

        # Phrase Detection
        common_terms = ["of", "with", "without", "and", "or", "the", "a"]
        phrases = Phrases(words, common_terms=common_terms)
        bigram = Phraser(phrases)
        all_sentences = list(bigram[words])

        feature_num = 1000
        word_2_vec = Word2Vec(all_sentences,
                              # Ignore words that appear less than this
                              min_count=1,
                              # Dimensionality of word embeddings
                              size=feature_num, 
                              # Number of processors (parallelisation)
                              workers=2,
                              # Context window for words during training
                              window=3,\
                              # Number of epochs training over corpus
                              iter=20)       

        print ("WORD2VEC: len = %d, dimension = %d"  %(len(word_2_vec.wv.vocab), word_2_vec.vector_size))


        # get document level embeddings
        document_w2v = self.averaged_word_vectorizer(corpus=all_sentences, model=word_2_vec, num_features=feature_num)

        #cluster whole documents
        km_model = KMeans(n_clusters=self.cluster_num)
        km_model.fit(document_w2v)
        self.claster_labels = km_model.labels_.tolist()

        # get topic for each document
        documents_words = self.get_document_word (corpus=all_sentences, model=word_2_vec, num_features=feature_num)

        return documents_words, km_model.labels_.tolist()

        