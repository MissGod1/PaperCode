#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2020/11/24 14:20:52
@Author  :   Baize
@Version :   1.0
@Contact :   
@License :   
@Desc    :   
'''

from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.model_selection import cross_val_score, train_test_split
import numpy as np
from sklearn.metrics import f1_score, accuracy_score, recall_score, precision_score
from sklearn.svm import SVC
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
    php_list = normal_list + webshell_list
    normal_verctorizer = CountVectorizer(ngram_range=(2,2), decode_error='ignore',
                        token_pattern=r'\s\w+\s', min_df=1)
    normal_tfidftransformer = TfidfTransformer()
    X = normal_verctorizer.fit_transform(php_list)
    X = normal_tfidftransformer.fit_transform(X).toarray()
    y = len(normal_list)*[0] + len(webshell_list)*[1]

    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.33)
    model = MultinomialNB()
    # model = SVC()
    model.fit(x_train, y_train)
    y_predict = model.predict(x_test)
    # print(y_predict)
    f1 = f1_score(y_test, y_predict, average='micro') * 100
    precision = precision_score(y_test, y_predict) * 100
    recall = recall_score(y_test, y_predict) * 100
    accuracy = accuracy_score(y_test, y_predict) * 100
    print("Accuracy = %.2f%%, Precision = %.2f%%, Recall = %.2f%%, F1 Score = %.2f%%" % (f1, accuracy, precision, recall))
    # gnb = GaussianNB()
    # score = cross_val_score(gnb, X, y, cv=10)
    # print(X.shape)
    # print(score)
    # print(np.mean(score)*100)

