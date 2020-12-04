#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test.py
@Time    :   2020/11/24 14:27:57
@Author  :   Baize
@Version :   1.0
@Contact :   
@License :   
@Desc    :   
'''
#%%


from nltk.util import pr
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
import numpy as np
def get_raw_data(filename) -> list:
    raw = []
    with open(filename, 'r') as fp:
        for line in fp.readlines():
           raw.append(line.strip())
    return raw

if __name__ == "__main__":
    normal_file = 'data/opcode/normal_opcodes.txt'
    webshell_file = 'data/opcode/webshell_opcodes.txt'
    
    normal_list = get_raw_data(normal_file)
    webshell_list = get_raw_data(webshell_file)

    normal_verctorizer = CountVectorizer(ngram_range=(2,2), decode_error='ignore',
                        token_pattern=r'\s\w+\s', min_df=1)
    normal_tfidftransformer = TfidfTransformer()
    x1 = normal_verctorizer.fit_transform(normal_list)
    x1 = normal_tfidftransformer.fit_transform(x1).toarray()
    y1 = len(x1)*[0]

    webshell_verctorizer = CountVectorizer(ngram_range=(2,2), decode_error='ignore',
                        token_pattern=r'\s\w+\s', min_df=1)
    webshell_tfidftransformer = TfidfTransformer()
    x2 = webshell_verctorizer.fit_transform(webshell_list)
    x2 = webshell_tfidftransformer.fit_transform(x1).toarray()
    y2 = len(x2)*[0]

    X = np.concatenate((x1, x2))
    y = np.concatenate((y1, y2))

    # x_test, y_test, x_train, y_train = train_test_split(X, y, test_size=0.33)

    gnb = GaussianNB()
    score = cross_val_score(gnb, X, y, cv=10)
    print(score)
    print(np.mean(score)*100)

