import csv
from datetime import datetime

QUESTIONS_PATH = 'data_play/question.csv'
ANSWER_PATH = 'data_play/answer.csv'
QUESTIONS_DATA_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWER_DATA_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


def get_questions():
    questions = read_file(QUESTIONS_PATH)
    return questions


def get_answers(id_elem: str):
    answers = read_file(ANSWER_PATH)
    return [answer for answer in answers if answer['question_id'] == str(id_elem)]


def get_answer(questions, question_id):
    for question in questions:
        if question["id"] == str(question_id):
            return question


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

# CONNECTION


def read_file(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        yield from reader


def get_next_id(file_path):
    return int(max(read_file(file_path), default={'id': 0}, key=lambda e: int(e['id']))['id']) + 1


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
