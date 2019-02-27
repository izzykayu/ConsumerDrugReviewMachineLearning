import nltk
import sys
""""
    [a-zA-Z]+
    [A-Z][a-z]*
    p[aeiou]{,2}t
    \d+(\.\d+)?
    ([^aeiou][aeiou][^aeiou])*
    \w+|[^\w\s]+
"""
import re
import pandas as pd

train = pd.read_csv('drugLibTrain_raw.tsv', sep="\t")
print(list(train.columns))
import os
# outfile = open('cleaned_mimic_notes.txt', 'a')
# counter = 0
# # for index,line in enumerate(test_sample['TEXT']):
# #     counter += 1
# #     new_note = clean_mimic(line)+ os.linesep
# #     outfile.write(new_note)
#
# print('cleaned and wrote out ',counter, 'notes!')
# outfile.close()
# apple =
# def train():

def preprocessing(text):
    """

    :param text: string such as the icd billing code descpL Shiga toxin-producing Escherichia coli [E. coli] (STEC) O157"
    :return: pre-processed to exclude digits and to account for processing
    age and other numbers commonly found in health consumer or health professional narratives

    """
    text = text.strip().replace('\n\n', '#')
    text = text.replace ('\n', '')
    text = text.replace(u'＝','=').replace(u'＞', '>').replace(u'＜','<').replace(u'≤','<=').replace (u'≥','>=').replace(u'≦','<=').replace(u'≧','>=').replace(u'mm³','mm^3').replace(u'µl','ul').replace(u'µL','ul').replace(u'·','').replace(u'‐','-').replace(u'—','-')

    text = text.replace('((', '(').replace('))', ')')
    text = re.sub('(\d+)( |)(~|/|&|\|)( |)(\d+)',r'\1 - \5',text) # e.g., '10~20' to '10 ~ 20'
    text = re.sub(r"(\d+),(\d{3})", r'\1\2', text) # 10,123 to 10123
    text = re.sub(r"(\d+),(\d{1,2})", r'\1.\2', text) # 10,1 to 10.1
    text = re.sub(r"between (\d+), (\d{1,2}) (and|or) ", r'between \1.\2 \3 ', text) # 'between 7, 5 and ' to 'between 7.5 and '
    text = re.sub(r"(\d+) (y(\.|/)?o)", r'age is \1 years', text) # Process age
    text = re.sub(r" +", " ", text)
    # while '  ' in text:
    #     text = text.replace('  ',' ')
    # # avoid connected values separated by splitting, e.g., ", but below 10%"
    # text = re.sub(", ("+connect+") ", r' \1 ', text) #

    return text.lower()


text = 'That U.S.A. poster-print costs $12.40...'
pattern = r'''(?x)    # set flag to allow verbose regexps
...     ([A-Z]\.)+        # abbreviations, e.g. U.S.A.
...   | \w+(-\w+)*        # words with optional internal hyphens
...   | \$?\d+(\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
...   | \.\.\.            # ellipsis
...   | [][.,;"'?():-_`]  # these are separate tokens; includes ], [
... '''
print(nltk.regexp_tokenize(text, pattern))



if __name__ == '__main__':

    wtn = WordsToNumbers()
    for num in nums:
        print("%d : %s", num, str(wtn.parseWord(num)))