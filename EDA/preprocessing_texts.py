import re
from nltk import sent_tokenize, word_tokenize
from nltk.tokenize import TweetTokenizer
import string
from collections import Counter
import csv
from tqdm import tqdm
## TO DOL still neeed to fix up argparse
import unicodedata
import sys
import datetime
import ujson
import bz2
import os
print(datetime.datetime.today())
# Import the necessary modules
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.stem import PorterStemmer
import argparse
import pandas as pd
import re


connect = ""

examplePharmacyBookText1 = """Pharmacy Note Assessment: AT is a 6 day-old male infant who is brought into the emergency department with a fever of 38 C.
The parents report that AT has been irritable for the past 4 hours with a very
rapid breathing. He has been making grunting noises and crying a lot.
AT weighed 7 pounds at birth, which was an unremarkable spontaneous vaginal delivery.
AT was in the newborn nursery for 3 days after delivery before being discharged with his mother.
AT’s mother had a temperature of 38 o C during labor and was given ampicillin 500 mg IV q6h for three days after delivery and sent home afebrile with amoxicillin 500 mg.
T.I.D. for 7 more days. The mother admits to not feeling very well the last few days
before delivery attributing it to a “cold”.

PE: VS: BP 110/70, HR-120, RR 65(normal 30-50), T 38 o C, wt. 2,955g .
Chest: CTA; there is grunting and mild intercostals retractions
Abd: Soft, distended, (+) bowel sounds, Liver normal size
Ext: Brachial pulses palpable, capillary refill 4 sec
Neuro: Mildly hypotonic
Labs: 140/100 glucose 100, Ca 8.5, T Bili 1.5, WBC 3000 
(80% Lymphs, 4.0/21/1.2 15% bands, 5% polys) Hct 45, Plt 250K, pH 7.3, Scr 0.4
CSF: WBC 850 (70% polys, 25% monos, 5% lymphs), protein 200, glucose 40
Cultures and serology pending.
Initial assessment: Bacterial meningitis"""

examplePharmacyBookText2 = """P.J. has indicated that she is injecting insulin to treat her diabetes . What questions might be 
asked to evaluate P.J.’s use of and response to insulin ?

M.B., a 35-year-old man, presents to the ED with a chief complaint of chest palpitations for 4 hours. He relates a 
history of many similar self-terminating episodes since he was a teenager. He took an unknown medication 5 years ago 
that decreased the occurrence of the pal- pitations, but he stopped taking it because of side effects. M.B.’s vital 
signs are BP, 96/68 mm Hg; pulse, 226 beats/minute, irregular; respiratory rate, 15 breaths/ minute; and temperature, 
98.7◦F. A rhythm strip confirms AF, with a QRS width varying from 0.08 to 0.14 seconds. To control the ventricular 
rate, 10 mg IV verapamil is admin- istered for 2 minutes. Within 2 minutes of completing the infusion, VF is noted on 
the monitor. M.B. is defibrillated, and normal sinus rhythm is restored. A subsequent ECG demonstrates a P-R interval 
of 100 ms (normal, 120 to 200 ms) and delta waves, compatible with WPW. What is WPW syndrome? """

def flatten(l):
    return [item for sublist in l for item in sublist]


def to_string(s):
    """
    makes to string

    """
    try:
        return str(s)
    except:
        #Change the encoding type if needed
        return s.encode('utf-8')

def preprocessing_clinical_text(text):
    """

    :param text: string such as the icd billing code descpL Shiga toxin-producing Escherichia coli [E. coli] (STEC) O157"
    :return: pre-processed to exclude digits and to account for processing
    age and other numbers commonly found in health consumer or health professional narratives

    """
    text = text.strip().replace('\n\n', '#')
    text = " ".join(sent_tokenize(text))
    text = text.replace ('\n', '')
    text = text.replace(u'＝','=').replace(u'＞', '>').replace(u'＜','<').replace(u'≤','<=').replace (u'≥','>=').replace(u'≦','<=').replace(u'≧','>=').replace(u'mm³','mm^3').replace(u'µl','ul').replace(u'µL','ul').replace(u'·','').replace(u'‐','-').replace(u'—','-')
    text = text.replace('((', '(').replace('))', ')')
    text = re.sub('(\d+)( |)(~|/|&|\|)( |)(\d+)',r'\1 - \5',text) # e.g., '10~20' to '10 ~ 20'
    text = re.sub(r"(\d+),(\d{3})", r'\1\2', text) # 10,123 to 10123
    text = re.sub(r"(\d+),(\d{1,2})", r'\1.\2', text) # 10,1 to 10.1
    text = re.sub(r"between (\d+), (\d{1,2}) (and|or) ", r'between \1.\2 \3 ', text) # 'between 7, 5 and ' to 'between 7.5 and '
    text = re.sub(r"(\d+) (y(\.|/)?o)", r'age is \1 years', text) # Process age
    text = re.sub(r"\d", "d", text) # pre-processing digits
    text = re.sub(r" +", " ", text)
    while '  ' in text:
        text = text.replace('  ',' ')

    return text.lower().strip()


textPhysicalExamSnippet = 'PE: VS: BP 110/70, HR-120, RR 65(normal 30-50), T 38 o C, wt.'

example_text = """P.J. has indicated that she is injecting insulin to treat her diabetes. What questions might be 
asked to evaluate P.J.’s use of and response to insulin?

M.B., a 35-year-old man, presents to the ED with a chief complaint of chest palpitations for 4 hours. He relates a 
history of many similar self-terminating episodes since he was a teenager. He took an unknown medication 5 years ago 
that decreased the occurrence of the palpitations, but he stopped taking it because of side effects. M.B.’s vital 
signs are BP, 96/68 mm Hg; pulse, 226 beats/minute, irregular; respiratory rate, 15 breaths/ minute; and temperature, 
98.7◦F. A rhythm strip confirms AF, with a QRS width varying from 0.08 to 0.14 seconds. To control the ventricular 
rate, 10 mg IV verapamil is administered for 2 minutes. Within 2 minutes of completing the infusion, VF is noted on 
the monitor. M.B. is defibrillated, and normal sinus rhythm is restored. A subsequent ECG demonstrates a P-R interval 
of 100 ms (normal, 120 to 200 ms) and delta waves, compatible with WPW. What is WPW syndrome? """


def splitSentence(content):
    """
    Given block of text, split into sentence
    Output: list of sentences
    """
    # Multiple space to single space, remove separators like - and _
    if pd.notnull(content):
        content = re.sub('\s*\t\t\t', ' ', content)
        content = re.sub('--+|==+|__+', ' ', content)
        content = re.sub('\.\s+', '. ',content)
        content = re.sub(':\s+', ': ',content)
        content = re.sub('\s+\[\*', ' [*', content)
        content = re.sub(' \s+', '. ',content)
        content = re.sub('\?', ' ', content)
        lsS = content.split('. ')
    else:
        lsS = []
    return lsS

def mkdir_if_not_exist(path):
    """
    path to directory
    """
    if not os.path.isdir(path):
        os.mkdir(path)


# Turn a Unicode string to plain ASCII, thanks to http://stackoverflow.com/a/518232/2809427
def unicodeToAscii(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
        )


def normalizeString(s):
    tknzr = TweetTokenizer()
    s = " ".join(tknzr.tokenize(s))
    s = re.sub(r"\d", "d", s)
    s = unicodeToAscii(s.lower().strip())
    s = re.sub(r"([.!?]+)", r" \1", s)
    s = re.sub(r"[^a-zA-Z.!?-]+", r" ", s)
    s = to_string(s)

    return s


def tokenize_multiple_return_strings(articles):
    """
    articles: a list of strings for example
    articles = zeroStartTrain['NOTE_TEXT'].to_list()
    """
    articles_new = [normalizeString(ar) for ar in articles]
    tokens = flatten([word_tokenize(ar) for ar in articles])

# Convert the tokens into lowercase: lower_tokens
    lower_tokens = [t.lower() for t in tokens]

# Create a Counter with the lowercase tokens: bow_simple
    bow_simple = Counter(lower_tokens)

# Print the 10 most common tokens
    print(bow_simple.most_common(10))
    return articles_new


def preProc(text):
    """
    text is a string, for example: "Please keep humira refrigeraterd.
    """

    text2 = normalizeString(text)

    tokens = [word for sent in sent_tokenize(text2) for word in
          word_tokenize(sent)]

    tokens = [word.lower() for word in tokens]

    stopwds = stopwords.words('english')
    tokens = [token for token in tokens if token not in stopwds]

    tokens = [word for word in tokens if len(word) >= 3]

    stemmer = PorterStemmer()
    try:
        tokens = [stemmer.stem(word) for word in tokens]

    except:
        tokens = tokens

    tagged_corpus = pos_tag(tokens)

    Noun_tags = ['NN', 'NNP', 'NNPS', 'NNS']
    Verb_tags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']

    lemmatizer = WordNetLemmatizer()


    def pratLemmatiz(token, tag):
        if tag in Noun_tags:
            return lemmatizer.lemmatize(token, 'n')
        elif tag in Verb_tags:
            return lemmatizer.lemmatize(token, 'v')
        else:
            return lemmatizer.lemmatize(token, 'n')


    pre_proc_text = " ".join([pratLemmatiz(token, tag) for token, tag in tagged_corpus])

    return pre_proc_text


def update(s):

    s = re.sub('\d', 'd', s)
    s = re.sub('\d+:\d+(:\d+)?\s*((a|A)|(p|P))(m|M)(\s*est|EST)?', ' <time> ', s)
    s = re.sub('( |^|\(|:|\+|-|\?|\.|/)\d+((,\d+)*|(\.\d+)?|(/\d+)?)', ' <num> ', s) # cases like: 12,23,345; 12.12; .23, 12/12;
    s = re.sub(r'([a-zA-Z->])([<\),!:;\+\?\"])', r'\1 \2 ', s)
    s = re.sub(r'([\(,!:;\+>\?\"])([a-zA-Z<-])', r' \1 \2', s)
    s = re.sub('\s+', ' ', s)
    return s

def clean_mimic(s):
    s = re.sub('\[\*\*.*\*\*\]|\\n|\s+', ' ', s).replace('  ', ' ').lower()
    return s

def replcDeid(s):
    """
    replace de-identified elements in the sentence (date, name, address, hospital, phone)
    """
    s = re.sub('\[\*\*\d{4}-\d{2}-\d{2}\*\*\]', '<date>', s)
    s = re.sub('\[\*\*.*?Name.*?\*\*\]', '<name>', s)
    s = re.sub('\[\*\*.*?(phone|number).*?\*\*\]', '<phone>', s)
    s = re.sub('\[\*\*.*?(Hospital|Location|State|Address|Country|Wardname|PO|Company).*?\*\*\]', '<loc>', s)
    s = re.sub('\[\*\*.*?\*\*\]', '<deidother>', s)
    return s

def tag_negation(doc):

    from nltk.sentiment.util import mark_negation
    return ' '.join( mark_negation(doc.split()) )


def cleanString(s, lower = True):
    s = replcDeid(s)
    s = update(s)
    if lower:
        s = s.lower()
    return s


def replaceContractions(s):
    contractions = ["don't","wouldn't","couldn't","shouldn't", "weren't", "hadn't" , "wasn't", "didn't" , "doesn't","haven't" , "isn't","hasn't"]
    for c in contractions:
        s = s.replace( c, c[:-3] +' not')
    return s

def preprocess_string(s):
    s = cleanString(s, True)
    s = replaceContractions(s)
    return s


def cleanNotes(content):
    """
    Process a chunk of text
    """
    lsOut = []
    content = str(content)
    if len(content) > 0:
        lsS = splitSentence(content)
        for s in lsS:
            if len(s) > 0:
                s = cleanString(s, lower = True)
                s = replaceContractions(s)
                lsOut.append(s)
        out = ' '.join(lsOut)
    else:
        out = ''
    return out


def CleanSBUNoteEvents(sbu, outpath):
    Counter = 0
    with bz2.open(sbu, 'rt') as f:
        with open(outpath, 'a'):
            for index, line in enumerate(f):
                record = ujson.loads(line)
                enc_list = record['encounters']
                for enc in enc_list:
                    Counter += 1
                    outpath.write(cleanNotes(to_string(enc['notes'])))

    print(str(Counter), 'Notes from SBU')

    outpath.close()


# using the CAML write_discharge_summaries and various pre-processing steps
# but own version of pre-processing texts combining cleaning contractions, using d for digit, and some rules from deepEHR
def CleanMIMICiiiNoteEvents(out_file):
    notes_file = 'data/NOTEEVENTS.csv'
    print("processing notes file")
    with open(notes_file, 'r') as csvfile:
        with open(out_file, 'w') as outfile:
            print("writing to %s" % (out_file))
            #outfile.write(','.join(['SUBJECT_ID', 'HADM_ID', 'CHARTTIME', 'TEXT']) + '\n')
            notereader = csv.reader(csvfile)
            #header
            next(notereader)
            i = 0
            for line in tqdm(notereader):
                subj = line[1]
                category = line[6]
                if category in ['Pharmacy', 'Discharge summary', 'Radiology', 'Nursing', 'Nursing/other', 'Respiratory']:
                    note = line[10]
                    text = '"' + clean_mimic(cleanNotes(note)) + '"'
                    print(text)
                    outfile.write(text + os.linesep)
                i += 1
            print(str(i), 'notes from mimic written out!')
    return out_file


#
# infile = '/Users/isabelmetzger/fastText/data/PubMedArticles.txt'
# with open(infile, 'r') as f:
#     with open('/Users/isabelmetzger/fastText/data/cliniDataPreproc/PubMedArticlesPrec.txt', 'w') as otf:
#         i = 0
#         for line in f.read().split('\n'):
#
#             i += 1
#             clean_note = cleanNotes(line)
#             print(clean_note, str(i))
#
#             otf.write(clean_note + os.linesep)
#
# print("PubMedArticles:", str(i))


infile = '/Users/isabelmetzger/Downloads/JHU/JHUGeriatricCases.txt'
with open(infile, 'r') as f:
    with open('/Users/isabelmetzger/fastText/data/cliniDataPreproc/JHUGeriatricCases.txt', 'w') as otf:
        i = 0
        for line in f.read().split('\n'):

            i += 1
            clean_note = cleanNotes(line)
            print(clean_note, str(i))

            otf.write(clean_note + os.linesep)

print("PubMedArticles:", str(i))
# CleanMIMICiiiNoteEvents(out_file = '/Users/isabelmetzger/fastText/data/cliniDataPreproc/mimiciiipreproc.csv')