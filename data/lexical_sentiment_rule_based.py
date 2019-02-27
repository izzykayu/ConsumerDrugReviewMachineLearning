#
# rule-based + lexical resources sentiment analysis with the Afinn and Vader Lexicons, along with an exploration of
# TO DO: emotion related features related to the NRC lexicon
# TO DO: negation/ negex triggers
# TO DO:fix up argparse

from afinn import Afinn
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import sys


afinn_sentiment_analyzer = Afinn(emoticons=True)
vader_sentiment_analyzer = SentimentIntensityAnalyzer(lexicon_file='vader_lexicon.txt')

def create_sentiment_scores(review, textCols):
    """
    :param review: this is pandas data-frame
    :param textCols: this is a list of columns with text where you want to apply sentiment analysis/
    utilize emotion lexical resources and etc
    :return: a data-frame with new columns (5 new features for each of the text column names passed)
    """
    for x in textCols:
        review[x] = review[x].fillna("fillna")
        review['AfinnScore' + x] = review[x].apply(lambda u: afinn_sentiment_analyzer.score(str(u)))
        review['VaderNegScore' + x] = review[x].apply(lambda u: vader_sentiment_analyzer.polarity_scores(str(u))['neg'])
        review['VaderNeuScore' + x] = review[x].apply(lambda u: vader_sentiment_analyzer.polarity_scores(str(u))['neu'])
        review['VaderPosScore' + x] = review[x].apply(lambda u: vader_sentiment_analyzer.polarity_scores(str(u))['pos'])
        review['VaderCompScore' + x] = review[x].apply(lambda u: vader_sentiment_analyzer.polarity_scores(str(u))['compound'])
    return review


coln = list(pd.read_csv('druglibcolnames.txt')['textColumns'])
print('example columns of text for feature engineering', coln)
# print(create_sentiment_scores(rev, coln))


def make_lexical_feats_TSV(pathname1, pathname2, pathname3):
    """

    :param pathname1: pathname to column names
    :param pathname2: pathname to input tab delimited file
    :param pathname3: pathname to where to write out new tab delimited file with new features
    :return: data-frame with new features
    """
    textColnames = list(pd.read_csv(pathname1)['textColumns'])
    print(textColnames)
    dataFrame = pd.read_csv(pathname2, sep="\t")
    # filling NA values with holder "__NA__
    review = dataFrame.fillna("__NA__")
    dF = create_sentiment_scores(review, textCols=textColnames)
    print(dF.sample(2))
    dF.to_csv(pathname3, sep='\t', index=False)
    print("completed writing new data frame tab sep file with lexical FE")
    print(set(dF.columns))
    return dF

def make_lexical_feats_CSV(pathname1, pathname2, pathname3):
    """
    comma separated files (example, mimic)
    :param pathname1: names of text columns to derive features from
    :param pathname2: infile pathname (dataframe in a csv file)
    :param pathname3: outfile pathname
    :return: df
    """
    textColnames = list(pd.read_csv(pathname1)['textColumns'])
    dataFrame = pd.read_csv(pathname2, sep=",")
    dF = create_sentiment_scores(dataFrame, textCols=textColnames)
    print(dF.sample(2))
    dF.to_csv(pathname3, sep=',', index=False)
    print("completed writing new data frame with lexical engineered features (comma sep file)")
    print(set(dF.columns))
    return dF


def make_lexical_feats_SEMICOLON(pathname1, pathname2, pathname3):
    textColnames = list(pd.read_csv(pathname1)['textColumns'])
    dataFrame = pd.read_csv(pathname2, sep=";")

    dF = create_sentiment_scores(dataFrame, textCols=textColnames)
    print(dF.sample(2))
    dF.to_csv(pathname3, sep=';', index=False)
    print("completed writing new data frame with new FE (semicolon-delimited file)")
    print(set(dF.columns))
    return dF


if __name__ == '__main__':
    '''rule-based feature engineering based on the afinn sentiment scorer and the vader sentiment analyzer 
        For example: if you want to create sentiment and emotion features based on the lexicons Afinn, Vader, and NRC
        and your df is in a tsv file, then you run as following:
        python3 lexical_sentiment_rule_based.py <TSV|CSV|SEMICOL> <colnames_file_pathname1> <input_file_pathname2> <out_file_pathname3>
    concrete example:
    python3 lexical_sentiment_rule_based.py TSV druglibcolnames.txt drugLibTest_raw.tsv drugLibTest_raw_SentimentFE.tsv
    '''

    if sys.argv[1].upper() == 'TSV':
        make_lexical_feats_TSV(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1].upper() == 'CSV':
        make_lexical_feats_TSV(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1].upper() == 'SEMICOL':
        make_lexical_feats_SEMICOLON(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("please provide a string such as TSV|CSV|SEMICOL for format being read in and written out")