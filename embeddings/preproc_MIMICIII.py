# importing import libs
import re
import random
import pandas as pd
import numpy as np
import os
import sys


def select_only_discharge_notes(data):
    """
    getting discharge notes forf manual labelers/ expert labelers
    """
    for d in data:
        if 'notes' in d:
            new_notes = []
            for note in d['notes']:
                if 'discharge' in note['note_type'].lower():
                    new_notes.append(note)
            d['notes'] = new_notes
    return data

def clean_mimic(s):
    s = re.sub('\[\*\*.*\*\*\]|\\n|\s+', ' ', s).replace('  ', ' ').lower()
    return s

def Clean4WordEmbeddingsMIMICIII(pathname1, pathname2):
    """
    pathname1: path to csv for mimiciii noteevents (NOTEEVENTS.csv)
    pathname2: path to txt where cleaned mimic text will go
    """
    mimic_note_events = pd.read_csv(pathname1)

    outfile = open(pathname2, 'a')
    counter = 0
    mimic_text = mimic_note_events['TEXT'].fillna("fillna")
    for index,line in enumerate(mimic_text) # test_sample['TEXT']):
        counter += 1
        new_note = clean_mimic(line)+ os.linesep
        outfile.write(new_note)

    print('cleaned and wrote out ',counter, 'notes!')
    outfile.close()
    

