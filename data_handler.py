import csv
import os
import psycopg2
import database_common
from datetime import datetime
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

QUESTIONS_PATH = 'data_play/question.csv'
ANSWER_PATH = 'data_play/answer.csv'
QUESTIONS_DATA_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWER_DATA_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


@database_common.connection_handler
def get_questions(cursor):
    cursor.execute(
        sql.SQL("select * from {table}").
            format(table=sql.Identifier('question')))
    return cursor.fetchall()


def get_single_entry_by_id(file_path, entry_id):
    entries = read_file(file_path)
    for entry in entries:
        if int(entry["id"]) == entry_id:
            return entry


def vote_entry(file_path, file_headers, entry_to_vote, vote):
    voted = int(entry_to_vote['vote_number']) + int(vote)
    entry_to_vote['vote_number'] = voted
    write_elem_to_file(entry_to_vote, file_path, file_headers)


def generate_data_with_integers(items: dict):
    for elem in items:
        for key in elem:
            try:
                elem[key] = int(elem[key])
            except ValueError:
                pass
    return items



def get_next_id(file_path):
    return int(max(read_file(file_path), default={'id': 0}, key=lambda e: int(e['id']))['id']) + 1


@database_common.connection_handler
def get_single_question(cursor, question_id):
    query = """SELECT * FROM question
                WHERE id = %(question_id)s"""
    cursor.execute(query, {"question_id":question_id})
    return {key:value for e in cursor.fetchall() for key,value in e.items()}


def get_single_answer(answer_id):
    return get_single_entry_by_id(file_path=ANSWER_PATH, entry_id=answer_id)


def get_ordered_questions(parameters):
    questions = generate_data_with_integers(list(read_file(QUESTIONS_PATH)))
    order_by = parameters.get('order_by', 'submission_time')
    direction = parameters.get('order_direction', 'desc')
    should_reverse = direction == 'desc'

    return sorted(questions, key=lambda elem: elem[order_by], reverse=should_reverse)


@database_common.connection_handler
def get_answers_for_question(cursor, question_id):
    query = """SELECT * FROM answer
                WHERE question_id = %(question_id)s"""
    cursor.execute(query, {"question_id": question_id})
    return cursor.fetchall()


def get_next_question_id():
    return get_next_id(QUESTIONS_PATH)


def add_question(new_entry):

    new_question = {
        'id': get_next_id(QUESTIONS_PATH),
        'view_number': 0,
        'vote_number': 0,
        'submission_time': round(datetime.timestamp(datetime.now())),
    }
    new_question.update(new_entry)
    add_id = write_elem_to_file(new_question, QUESTIONS_PATH, QUESTIONS_DATA_HEADER)
    return add_id


def edit_question(new_entry, question_id):
    question = get_single_question(question_id)
    question.update(new_entry)
    write_elem_to_file(question, QUESTIONS_PATH, QUESTIONS_DATA_HEADER)


def delete_question(question_id, path):
    delete_answers(question_id, path)
    delete_entry(path, entry_id=question_id, file_path=QUESTIONS_PATH,
                 file_header=QUESTIONS_DATA_HEADER)


def vote_question(question_id, vote):
    return vote_entry(QUESTIONS_PATH, file_headers=QUESTIONS_DATA_HEADER,
                      entry_to_vote=get_single_question(question_id=question_id), vote=vote)


def increment_views_algorithm(file_path, file_headers, entry):
    incremented_views = int(entry['view_number']) + 1
    entry['view_number'] = str(incremented_views)
    write_elem_to_file(entry, file_path, file_headers)


def increment_views(question_id):
    return increment_views_algorithm(QUESTIONS_PATH, file_headers=QUESTIONS_DATA_HEADER,
                                     entry=get_single_question(question_id=question_id))


def get_next_answer_id():
    return get_next_id(ANSWER_PATH)


def add_answer(new_entry, question_id):
    new_question = {
        'id': get_next_id(ANSWER_PATH),
        'question_id': question_id,
        'vote_number': 0,
        'submission_time': round(datetime.timestamp(datetime.now())),
    }
    new_question.update(new_entry)
    write_elem_to_file(new_question, ANSWER_PATH, ANSWER_DATA_HEADER)


def delete_answer(answer_id, path):
    delete_entry(path, entry_id=answer_id, file_path=ANSWER_PATH,
                 file_header=ANSWER_DATA_HEADER)


def delete_answers(question_id, path):
    answers = get_answers_for_question(question_id)
    for answer in answers:
        delete_answer(int(answer["id"]), path)


def vote_answer(entry_to_vote, vote):
    return vote_entry(file_path=ANSWER_PATH, file_headers=ANSWER_DATA_HEADER,
                      entry_to_vote=entry_to_vote, vote=vote)


# CONNECTION


def delete_image(location, path):
    if location['image']:
        filename = location['image']
        files = os.listdir(path)
        if filename in files:
            os.unlink(os.path.join(path, filename))
        else:
            pass


def read_file(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        yield from reader


def write_elem_to_file(elem, file_path, file_header):
    entries = list(read_file(file_path))
    updated_id = None

    with open(file_path, 'w') as file:
        dict_writer = csv.DictWriter(file, fieldnames=file_header)
        dict_writer.writeheader()
        for e in entries:
            if e['id'] == elem['id']:
                dict_writer.writerow(elem)
                updated_id = e['id']
            else:
                dict_writer.writerow(e)

        if not updated_id:
            dict_writer.writerow(elem)
            updated_id = elem['id']

    return updated_id


def delete_entry(path, entry_id, file_path, file_header):
    entries = list(read_file(file_path))
    with open(file_path, 'w') as file:
        dict_writer = csv.DictWriter(file, fieldnames=file_header)
        dict_writer.writeheader()
        for elem in entries:
            if int(elem['id']) == entry_id:
                delete_image(elem, path)
                continue
            dict_writer.writerow(elem)
