import sys
import datetime
from nltk.corpus import stopwords
todaysDate = datetime.datetime.now().strftime("%Y-%m-%d")
print(todaysDate)
import numpy as np
import pandas as pd
import string

from textblob import TextBlob


def replace_missing_texts(df, review_text_columns):
    """
    :param df: data frame (pandas)
    :param review_text_columns: a list with names of text columns to be replaced missing texts, e.g., ['text']
    :return: missing texts with "fillna"
    """
    for i in review_text_columns:
        df[i] = df[i].fillna("fillna")

    return df

def lexical_diversity(my_text_data):
    """
    input is list of text data
    output gives diversity_score
    """
    word_count = len(my_text_data)
    vocab_size = len(set(my_text_data))
    diversity_score = word_count / vocab_size
    return diversity_score

# part of speech dictionary
pos_dic = {
    'noun' : ['NN','NNS','NNP','NNPS'],
    'pron' : ['PRP','PRP$','WP','WP$'],
    'verb' : ['VB','VBD','VBG','VBN','VBP','VBZ'],
    'adj' :  ['JJ','JJR','JJS'],
    'adv' : ['RB','RBR','RBS','WRB']
}

# function to check and get the part of speech tag count of a words in a given sentence
def pos_check(x, flag):
    cnt = 0
    try:
        wiki = TextBlob(x)
        for tup in wiki.tags:
            ppo = list(tup)[1]
            if ppo in pos_dic[flag]:
                cnt += 1
    except:
        pass
    return cnt


def makePOSfeat(df, colnames):
    """
    part of speech tagging counts as engineered features
    :param df: pandas data-frame
    :param colnames: column(s) with text to count POS to create features
    :return: data-frame with more engineered features
    """
    for x in colnames:

        # part-of-speech tagging for
        df['noun_count' + x] = df[x].apply(lambda x: pos_check(x, 'noun'))
        df['verb_count' + x] = df[x].apply(lambda x: pos_check(x, 'verb'))
        df['adj_count' + x] = df[x].apply(lambda x: pos_check(x, 'adj'))
        df['adv_count' + x] = df[x].apply(lambda x: pos_check(x, 'adv'))
        df['pron_count' + x] = df[x].apply(lambda x: pos_check(x, 'pron'))


        df['count_word_raw' + x] = df[x].apply(lambda x: len(str(x).split()))
        # Unique word count
        df['count_unique_word_raw' + x] = df[x].apply(lambda x: len(set(str(x).split())))
        # Letter count
        df['count_letters_raw' + x] = df[x].apply(lambda x: len(str(x)))
        # punctuation count
        df["count_punctuations_raw" + x] = df[x].apply(lambda x: len([c for c in str(x) if c in string.punctuation]))
        # upper case words count
        df["count_words_upper_raw" + x] = df[x].apply(lambda x: len([w for w in str(x).split() if w.isupper()]))
        # title case words count
        df["count_words_title_raw" + x] = df[x].apply(lambda x: len([w for w in str(x).split() if w.istitle()]))
        # Number of stopwords
        df["count_stopwords_raw" + x] = df[x].apply(lambda x: len([w for w in str(x).lower().split() if w in stopwords]))
        # Average length of the words
        df['mean_word_len_raw' + x] = df[x].apply(lambda x: np.mean([len(w) for w in str(x).split()]))
        # Word count percent in each comment:
        df['word_unique_percent_raw' + x] = df['count_unique_word_raw' + x] * 100 / df['count_word_raw' + x]
        # percentage of punctuation
        df['punctuation_percent_raw' + x] = df['count_punctuations_raw' + x] * 100 / df['count_word_raw' + x]
        # lexical diversity
        df['lexical_diversity'+ x] = df[x].apply(
            lambda x1: lexical_diversity([wrd for wrd in x1.split() if not wrd.isnumeric()]))

    print(set(df.columns), "\nAdditional Feature Engineering--Note: still utilizing raw text inputs")
    return df

def POStagFeatEngTSV(pathname1, pathname2, pathname3):
    colnames = list(pd.read_csv(pathname1)['textColumns'])
    dataFrame = pd.read_csv(pathname2, sep="\t")
    dataFrame = replace_missing_texts(dataFrame, colnames)
    newDataFrame = makePOSfeat(dataFrame, colnames=colnames)
    print(newDataFrame.sample(2))
    newDataFrame.to_csv(pathname3, append=False, sep="\t")
    print("tab separated Part-of-speech data-set created")
    print(set(newDataFrame.columns))
    return newDataFrame

def POStagFeatEngCSV(pathname1, pathname2, pathname3):
    colnames = list(pd.read_csv(pathname1)['textColumns'])
    dataFrame = pd.read_csv(pathname2)
    dataFrame = replace_missing_texts(dataFrame, colnames)
    newDataFrame = makePOSfeat(dataFrame, colnames=colnames)

    print(newDataFrame.sample(2))
    newDataFrame.to_csv(pathname3, append=False)
    print("comma separated POS + other features +  data-set created")
    print(set(newDataFrame.columns))
    return newDataFrame


def POStagFeatEngSEMICOL(pathname1, pathname2, pathname3):
    colnames = list(pd.read_csv(pathname1)['textColumns'])
    dataFrame = pd.read_csv(pathname2)
    dataFrame = replace_missing_texts(dataFrame, colnames)
    newDataFrame = makePOSfeat(dataFrame, colnames=colnames)

    print(newDataFrame.sample(2))
    newDataFrame.to_csv(pathname3, append=False)
    print("comma separated POS + other features +  data-set created")
    print(set(newDataFrame.columns))
    return newDataFrame


if __name__ == '__main__':
    '''Convert data and normalize it in different ways.
        For example: if you want to convert a text file to a fully cleaned file, then you run as following:
            python3 making_textblobPosfeatures.py  <TSV|CSV|SEMICOL|JSONBZ2> <colnames_file_pathname1> <input_file_pathname2> <out_file_pathname3 >
    '''

    if sys.argv[1].upper() == 'TSV':
        POStagFeatEngTSV(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1].upper() == 'CSV':
        POStagFeatEngCSV(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1].upper() == 'SEMICOL':
        POStagFeatEngSEMICOL(sys.argv[2], sys.argv[3], sys.argv[4])
    # elif sys.argv[1].upper() == 'JSONBZ2':
    #     make_lexical_feats_bz2uJson(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("please provide a string such as TSV|CSV|SEMICOL|JSONBZ2 for format being read in and written out")


