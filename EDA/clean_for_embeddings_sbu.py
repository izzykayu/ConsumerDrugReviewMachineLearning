import bz2
import ujson
import pandas as pd
import sys



# # def clean4
# with bz2.open('/Users/isabelmetzger/PycharmProjects/EmoBank/datasets/annotated_drug_reviews.txt.bz2',
#               'rt') as fh:
#     counter = 0
#     df = pd.read_csv(fh, sep='\|\!\|', header=None)
#     for index, line in
    # for index, line in enumerate(fh):
    #     record = pd.read_csv('')
# with bz2.open('~/PycharmProjects/DeepNLP-models-Pytorch/sbu_enctype_101_json.txt.bz2', 'rt') as fh:
#     counter = 0
#     for index, line in enumerate(fh):
#         record = ujson.loads(line)
#         enc = record['encounters']
#         counter += 1
#         enc_pat_df=pd.DataFrame(enc)
#         enc_pat_df.to_csv(sys.argv[2] + str(counter) + 'sbu.txt', sep="|")
#         #['notes'])