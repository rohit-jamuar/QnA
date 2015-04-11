#!/usr/bin/python
# -*- coding: utf-8 -*-


from flask import Flask, request, jsonify
from cPickle import dump
from random import choice
from sys import argv
from datetime import datetime
from helpers import Question, populate_data_source, get_choices
from helpers import get_questions_rev_chrono_order, verify_value


DATA_STORE = None
APP = Flask(__name__)


if len(argv) == 2:
    DATA_STORE = populate_data_source(argv[1])
    if not DATA_STORE:
        print 'Could not locate sample data. Exiting....'
        exit(1)
else:
    print 'You need to pass the sample data-set as a command-line arg!'
    exit(1)


@APP.route('/get_topics', methods=['GET'])
def fetch_topic_names():
    '''
    Returns names of topics currently being supported by data-store.
    '''
    return jsonify({'Topics': '{}'.format(','.join([t for t in DATA_STORE]))})


@APP.route('/get_question/<int:qid>', methods=['GET'])
@APP.route('/get_question/<topic>', methods=['GET'])
def fetch_question(qid=-1, topic=None):
    '''
    The endpoint is responsible for fetching a question. The end-user gets to
    have a say in how a question is fetched - the user can provide the 'qid'
    of the question or can mention the 'topic'. The 'topic' and 'qid' serve
    as extra filters which need to be used. Moreover, the end-user can retrieve
    questions in reverse order of creation - this can be facilitated by
    providing a GET param.
    '''
    topic = topic.lower() if topic else None
    if 0 < qid <= Question.QID_COUNTER:
        for topic in DATA_STORE:
            for question in DATA_STORE[topic]:
                if question.qid == qid:
                    choices = get_choices(question.answer, question.distractors)
                    return jsonify({'qid': question.qid,
                        'Question': question.ques.capitalize(),
                        'Choices': choices})
    elif all([topic, topic in DATA_STORE]):
        sort_requested = verify_value(request, 'sort', {u'y', u'Y'})
        if sort_requested:
            data = get_questions_rev_chrono_order(DATA_STORE, 1, topic)
            if data:
                choices = get_choices(data[0].answer, data[0].distractors)
                return jsonify({'qid': data[0].qid,
                                'Question': data[0].ques.capitalize(),
                                'Choices': choices})
            return jsonify({'Error':\
                'Unable to fetch data in reverse chronological order!'})
        else:
            rand_question = choice(DATA_STORE[topic])
            opts = get_choices(rand_question.answer, rand_question.distractors)
            return jsonify({'qid': rand_question.qid,
                            'Question': rand_question.ques.capitalize(),
                            'Choices': opts})
    else:
        return jsonify({'Error':
            'Either an invalid question-id or an invalid topic requested!'})


@APP.route('/get_all_questions', methods=['GET'])
@APP.route('/get_all_questions/<topic>', methods=['GET'])
def get_all_questions(topic=None):
    '''
    This endpoint is responsible for returning all the questions present in the
    internal data-store. The end-user has the ability to filter questions on
    the basis of topic. Also, the end-user can enable chronological sorting by
    passing an HTTP GET param.
    '''
    max_count = request.args.get('max_count', None)
    try:
        max_count = int(max_count) if max_count else None
    except ValueError:
        max_count = None
    sort_requested = verify_value(request, 'sort', {u'y', u'Y'})
    questions_to_return = None
    topic = topic.lower() if topic else None
    if all([topic, topic in DATA_STORE]):
        if sort_requested:
            questions_to_return = [
                    question.ques.capitalize() for question in
                    get_questions_rev_chrono_order(DATA_STORE,
                            number=max_count, topic=topic)
                ]
        else:
            questions_to_return = []
            if max_count:
                for question in DATA_STORE[topic]:
                    if len(questions_to_return) == max_count:
                        break
                    questions_to_return.append(question.ques.capitalize())
            else:
                questions_to_return = [question.ques.capitalize()
                                       for question in DATA_STORE[topic]]
    elif not topic:
        if sort_requested:
            questions_to_return = [
                    q.ques.capitalize() for q in
                    get_questions_rev_chrono_order(DATA_STORE,
                                                   number=max_count)
                ]
        else:
            questions_to_return = []
            if max_count:
                stop_appending = False
                for topic in DATA_STORE:
                    if stop_appending:
                        break
                    for question in DATA_STORE[topic]:
                        questions_to_return.append(question.ques.capitalize())
                        if len(questions_to_return) == max_count:
                            stop_appending = True
                            break
            else:
                questions_to_return = [question.ques.capitalize()
                                       for topic in DATA_STORE
                                       for question in DATA_STORE[topic]]
    else:
        return jsonify({'Error': 'Invalid topic was requested!'})
    return jsonify({'Questions': questions_to_return})


@APP.route('/edit_question/<int:qid>', methods=['POST'])
def edit_question(qid=-1):
    '''
    This endpoint would allow the end-users to change an existing question.
    '''
    if 0 < qid <= Question.QID_COUNTER:
        succesfully_edited = False
        if request.json and all([True if field in request.json else False
                for field in {u'Question', u'Answer', u'Distractors'}]):
            for topic in DATA_STORE:
                if succesfully_edited:
                    break
                for index in range(len(DATA_STORE[topic])):
                    if DATA_STORE[topic][index].qid == qid:
                        DATA_STORE[topic][index].ques = \
                            request.json[u'Question'].lower()
                        DATA_STORE[topic][index].answer = \
                            request.json[u'Answer']
                        DATA_STORE[topic][index].distractors = [
                                elem.strip()
                                for elem in request.json[u'Distractors']
                                .split(',') if elem
                            ]
                        DATA_STORE[topic][index].update_time = datetime.now()
                        dump(DATA_STORE, open('parsed.data', 'wb'))
                        succesfully_edited = True
                        break
        return jsonify({'Response': 'Successfully edited the question!'})\
            if succesfully_edited\
            else jsonify({'Response': 'Could not edit the question!'})
    else:
        return jsonify({'Error': 'Invalid question-id passed!'})


@APP.route('/create_question', methods=['POST'])
def create_question():
    '''
    This endpoint would allow the end-user to add a new question. The endpoint
    would primarily check if the question exists, if it does, the endpoint
    would return an error message, else, a new question would be added and
    the internal data-store and the pickled file on local disk.
    '''
    if request.json and all(
        [True if field in request.json else False
         for field in {u'Question', u'Answer', u'Distractors', u'Topic'}]):
        ques, ans, distracts, topic = [request.json[field]
                for field in [u'Question', u'Answer', u'Distractors', u'Topic']]
        distracts = [elem.strip() for elem in distracts.split(',') if elem]
        topic, ques = topic.lower(), ques.lower()
        if topic in DATA_STORE:
            for question in DATA_STORE[topic]:
                if question.ques == ques:
                    return jsonify({'Error': 'This question already exists!'})
        new_question = Question(ques, ans, distracts)
        DATA_STORE[topic].append(new_question)
        dump(DATA_STORE, open('parsed.data', 'wb'))
        return jsonify({'Response':
                        'Successfully added a new question (qid = {})!'
                        .format(new_question.qid)})
    return jsonify({'Error': 'Necessary fields were not passed in the JSON!'})

if __name__ == '__main__':
    APP.run(debug=True)
