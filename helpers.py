#!/usr/bin/python
# -*- coding: utf-8 -*-

from cPickle import load, dump
from collections import defaultdict
from os.path import isfile
from datetime import datetime
from random import shuffle


class Question(object):

    '''
    Question v0.1
    '''
    QID_COUNTER = 0

    def __init__(self, question, answer, distractors):
        Question.QID_COUNTER += 1
        self.qid = Question.QID_COUNTER
        self.ques = question.lower()
        self.answer = answer
        self.distractors = distractors
        self.update_time = datetime.now()


def populate_data_source(filename):
    '''
    Function used for parsing and aptly populating internal data-store.
    - If the parsed data exists, it loads the contents using cPickle's load,
    it also computes the last qid which was generated - knowing this helps
    in checking if the requested qid is in the range of qids which have
    been previously generated, hence validating if a user-request can be
    serviced.
    - If the parsed data does not exist, code primarily parses the file named
    'filename' and generates a data-store with schema :
                         {topic : [Question(), ... ], ...}
    Moreover, the parsed data is dumped on local drive so as to avoid parsing
    the sample csv in subsequent server runs.
    '''
    data_source = None
    if isfile('parsed.data'):
        data_source = load(open('parsed.data', 'rb'))
        for topic in data_source:
            Question.QID_COUNTER += len(data_source[topic])
    elif isfile(filename):
        data_source = defaultdict(list)
        with open(filename) as file_input:
            header_read = False
            for line in file_input:
                if not header_read:
                    header_read = True
                    continue
                question, answer, distractors = \
                    [elem.strip() for elem in line.split('|')]
                distractors = [i.strip() for i in distractors.split(',') if i]
                data_source['arithmetic'].append(
                    Question(question, answer, distractors))
        dump(data_source, open('parsed.data', 'wb'))
    return data_source


def select_k_largest(arr, k, key):
    '''
    k-select algorithm
    time-complexity : O(kn)
    space-complexity : O(1)
    '''
    if all([arr, key]):
        if all([k, k < len(arr)]):
            for i in range(k):
                for j in range(i + 1, len(arr)):
                    if key(arr[i]) < key(arr[j]):
                        arr[i], arr[j] = arr[j], arr[i]
            return arr[:k]
        arr.sort(key=key, reverse=True)
        return arr


def get_questions_rev_chrono_order(all_data, number=None, topic=None):
    '''
    Returns a list of Question objects in a reverse chronological order as
    determined w.r.t their time of creation. It can also be provided parameters
    for returning a list of size 'number' of a smaller size if the initial list
    has fewer elements. Also, the list generation can be guided by 'topic'.
    '''
    data = []
    if not topic:
        for topic in all_data:
            for question in all_data[topic]:
                data.append(question)
    elif topic in all_data:
        data = all_data[topic]
    if data:
        return select_k_largest(data, number, lambda x: x.update_time)


def verify_value(request_object, key=None, affirmatives=None):
    '''
    Provided a request context object, check if a key exists. If the key
    exists, ensure that its value is one among the 'affirmatives'.
    '''
    if all([request_object, key, affirmatives]):
        temp = request_object.args.get(key, None)
        return True if temp and temp in affirmatives else False


def get_choices(answer, distractors):
    '''
    Returns a shuffled list of answer, along with the distractors.
    '''
    result = [answer]
    result.extend([elem for elem in distractors])
    shuffle(result)
    return result
