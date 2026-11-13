# -*- coding: utf-8 -*-
# Converted from opinion_mining.ipynb.
# Project role: original macro-level workflow
# This standalone source contains the notebook code cells in order.
# Jupyter-only directives are retained as comments for provenance.

# --- code cell 1 ---
import os
import re 
import json
import time
import spacy 
import gensim 
import warnings
warnings.filterwarnings("ignore")
from gensim import corpora 
import collections
import numpy as np 
import pandas as pd
from spacy import tokens
from typing import Iterable, List, Set

import nltk 
from nltk import FreqDist 
nltk.download('stopwords')
nltk.download('wordnet')
nlp = spacy.load("en_core_web_sm")

# --- markdown cell 2 ---
# # Preparation

# --- code cell 3 ---
_CMAP_DIR = os.path.join(os.getcwd(), "data/contractions.txt")
with open(_CMAP_DIR, "r") as file:
    _CMAP = json.load(file)

# --- code cell 4 ---
def load_words(lexicon_dir: str) -> Set[str]:
    file = open(os.path.join(lexicon_dir), encoding="ISO-8859-1")
    return set(line.strip() for line in file.readlines())
    
_LEXICON_DIR = os.path.join(os.getcwd(), "")
_POS_WORDS = load_words(os.path.join(_LEXICON_DIR, "data/pos_words.txt"))
_NEG_WORDS = load_words(os.path.join(_LEXICON_DIR, "data/neg_words.txt"))
_OPINION_WORDS = _POS_WORDS | _NEG_WORDS

# --- code cell 5 ---
def data_prepare(cityName):
    data = pd.read_csv('data/{}.csv'.format(cityName),lineterminator='\n')
    with_urls = []
    idx_urls = []
    i = 0
    for string in data["body"]:
        try:
            urls = re.findall("(?P<url>https?://[^\s]+)", string)
            if urls != []:
                with_urls.append(string)
                idx_urls.append(i)
        except:
            idx_urls.append(i)
        i += 1
    
    idx_urls = list(set(idx_urls))
    data = data.drop(index=idx_urls).reset_index()
    data = data.drop(columns=['index','Unnamed: 0'])
    return data

with open('data/cities.txt','r') as f:
    cities = []
    while 1:
        line = f.readline()
        if line == '':
            break
        cities.append(line.strip())
cities = cities[:-1]    

# --- markdown cell 6 ---
# # Pre-processing

# --- code cell 7 ---
def expand_contractions(text, contraction_mapping=_CMAP):
    contractions_pattern = re.compile('({})'.format('|'.join(
        contraction_mapping.keys())), flags=re.IGNORECASE|re.DOTALL)

    def expand_match(contraction):
        match = contraction.group(0)
        first_char = match[0]
        if contraction_mapping.get(match):
            expanded_contraction = contraction_mapping.get(match)
        else:
            expanded_contraction = contraction_mapping.get(match.lower())
        if expanded_contraction!=None:
            expanded_contraction = first_char+expanded_contraction[1:]
        return expanded_contraction

    expanded_text = contractions_pattern.sub(expand_match, text)
    expanded_text = re.sub("'s", "", expanded_text)
    expanded_text = re.sub("'", "", expanded_text)
    return expanded_text

# --- code cell 8 ---
def remove_special_characters(text):
    if remove_digits:
        pattern = r"[^.a-zA-z\s]"
    else:
        pattern = r"[^a-zA-z0-9.!?\s]"

    # Substitute all special characters with spaces
    text = re.sub(pattern, " ", text)
    # Substitute any white space character with a single space
    text = " ".join(text.split())
    return text

# --- code cell 9 ---
def basic_preprocessing(texts):
    texts = texts.map(expand_contractions)
    texts = texts.map(remove_special_characters)
    return texts

# --- code cell 10 ---
def apply_spacy(texts):
    nlp = spacy.load('en_core_web_sm')

    start_time = time.time()
    docs = list(nlp.pipe(texts))

    return docs

# --- markdown cell 11 ---
# # Opinion mining

# --- code cell 12 ---
def _is_opinion_mod(token):
    is_mod = token.dep_ in {"amod", "advmod"}
    is_op = token.text.lower() in _OPINION_WORDS
    return is_mod and is_op

# --- code cell 13 ---
def sentiment_aspects(docs):

    sent_dict_list = []
    for doc in docs:
        sent_dict = collections.Counter()
        for token in doc:
      # check if the word is an opinion word, then assign sentiment
            if token.text.lower() in _OPINION_WORDS:
                if token.text.lower() in _POS_WORDS:
                    sentiment = 1 
                elif token.text.lower() in _NEG_WORDS:
                    sentiment = -1
                else:
                    sentiment = 0
                    
                if (token.dep_ == "advmod"):
                    continue
                elif (token.dep_ == "amod"):
                    sent_dict[token.head.text.lower()] += sentiment
                else:
                    for child in token.children:
                        if _is_opinion_mod(child):
                            sentiment *= 1.5
                        # check for negation words and flip the sign of sentiment
                        if child.dep_ == "neg":
                            sentiment *= -1
                    for child in token.children:
                        if (token.pos_ == "VERB") & (child.dep_ == "dobj"):
                            # if verb, check if there's a direct object
                            sent_dict[child.text.lower()] += sentiment
                            # check for conjugates (a AND b), then add both to dictionary
                            subchildren = []
                            conj = 0
                            for subchild in child.children:
                                if subchild.text.lower() == "and": 
                                    conj=1
                                if (conj == 1) and (subchild.text.lower() != "and"):
                                    subchildren.append(subchild.text.lower())
                                    conj = 0
                            for subchild in subchildren:
                                sent_dict[subchild] += sentiment              
                    # check for negation
                    for child in token.head.children:
                        noun = ""
                        if _is_opinion_mod(child):
                            sentiment *= 1.5
                        if (child.dep_ == "neg"):
                            sentiment *= -1

                    # check for nouns
                    for child in token.head.children:
                        noun = ""
                        if (child.pos_ == "NOUN") and (child.text not in sent_dict):
                            noun = child.text.lower()
                            # Check for compound nouns
                            for subchild in child.children:
                                if subchild.dep_ == "compound":
                                    noun = subchild.text.lower() + " " + noun
                                    sent_dict[noun] += sentiment
        sent_dict_list.append(collections.Counter(sent_dict))

    return sent_dict_list

# --- code cell 14 ---
def find_aspects(csv_path: str):
    reviews = data_prepare(csv_path)

    reviews = reviews['body'][:50000]
    n_reviews = len(reviews)
    print("Collected {} comments from city {}".format(n_reviews,csv_path))
    if n_reviews < 5000:
        return []

    valid_reviews = reviews.dropna()
    n_reviews = len(valid_reviews)

    # Basic preprocessing
    texts = basic_preprocessing(valid_reviews)

    # Create spacy docs using `nlp.pipe`
    spacy_docs = apply_spacy(texts)
    # Use docs to find aspects
    aspects = sentiment_aspects(spacy_docs)

    # Add columns to the DataFrame
    pd.options.mode.chained_assignment = None
    valid_reviews["processed_text"] = texts
    valid_reviews["aspects"] = aspects

    return valid_reviews

# --- code cell 15 ---
city_aspects = {}
for city in cities:
    start_time = time.time()
    aspect = find_aspects(city)
    if len(aspect) == 0:
        continue
    print("Get {} aspects from {}\n".format(city, len(aspect)))
    print(time.time()-start_time)

    aspect_dict = {}
    aspect_refine = {}
    for i in aspect['aspects']:
        items=list(i.items())
        for item in items:
            try:
                aspect_dict[item[0]].append(item[1])
            except:
                aspect_dict[item[0]] = []
    for term in aspect_dict.keys():
        if len(aspect_dict[term])>10:
            aspect_refine[term]=np.mean(aspect_dict[term])
    city_aspects[city] = aspect_refine

# --- code cell 16 ---
np.save('data/city_aspects.npy',city_aspects)

# --- markdown cell 17 ---
# # Generate categories

# --- code cell 18 ---
valid_city = []
feature_set = []
for city in city_aspects:
    if len(city_aspects[city].keys())>50:
        valid_city.append(city)
        feature_set = feature_set + list(city_aspects[city].keys())
feature_set = set(feature_set)

# --- code cell 19 ---
with open("data/features.txt","w") as f:
    for feature in feature_set:
        f.write(feature+'\n')

# --- code cell 20 ---
keyword_feature_final = pd.read_csv('data/keyword_feature.csv')

# --- code cell 21 ---
feature_keys = {}
for i in list(dict(zip(keyword_feature_final['category'],keyword_feature_final['keywords'])).items()):
    feature_keys[i[0][1:-1]]=[k[1:-1] for k in i[1][1:-1].split(",")]

# --- markdown cell 22 ---
# # Create city data

# --- code cell 23 ---
feature_value = {"city":[]}
for city in city_aspects:
    feature_value["city"].append(city)
    aspect_city = city_aspects[city]
    for feature in feature_keys:
        key_list = feature_keys[feature]
        key_value = []
        for key in key_list:
            try:
                key_value.append(aspect_city[key])
            except:
                pass
        try:
            value = np.mean(key_value)
        except:
            value = 0
        try:
            feature_value[feature].append(value)
        except:
            feature_value[feature] = [value]

# --- code cell 24 ---
df_final = pd.DataFrame(feature_value)
df_final.to_csv('data/before_dropna.csv')
df_final = df_final.dropna().reset_index().drop(columns=['index'])
df_final.to_csv("data/aspect_cities.csv")
