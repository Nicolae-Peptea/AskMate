import csv
from datetime import datetime

QUESTIONS_PATH = 'data_play/question.csv'
ANSWER_PATH = 'data_play/answer.csv'
QUESTIONS_DATA_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWER_DATA_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


def get_questions():
    return read_file(QUESTIONS_PATH)


def get_single_question(question_id):
    questions = list(get_questions())
    for question in questions:
        if int(question["id"]) == question_id:
            return question


def get_ordered_questions(questions, order_by, direction):
    for question in questions:
        for piece in range(len(questions) - 1):
            if direction == "asc":
                if questions[piece][order_by] > questions[piece+1][order_by]:
                    questions[piece], questions[piece + 1] = questions[piece + 1], questions[piece]
            else:
                if questions[piece][order_by] < questions[piece+1][order_by]:
                    questions[piece], questions[piece + 1] = questions[piece + 1], questions[piece]
    return questions


def get_answers(id_elem: str):
    answers = read_file(ANSWER_PATH)
    return [answer for answer in answers if answer['question_id'] == str(id_elem)]


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
    write_elem_to_file(new_entry, QUESTIONS_PATH, QUESTIONS_DATA_HEADER)


def add_answer(new_entry, question_id):
    new_question = {
        'id': get_next_id(ANSWER_PATH),
        'question_id': question_id,
        'vote_number': 0,
        'submission_time': round(datetime.timestamp(datetime.now())),
    }
    new_question.update(new_entry)
    write_elem_to_file(new_question, ANSWER_PATH, ANSWER_DATA_HEADER)


def delete_question(question_id):
    delete_entry(entry_id=question_id, file_path=QUESTIONS_PATH, file_header=QUESTIONS_DATA_HEADER)


def delete_answer(answer_id):
    delete_entry(entry_id=answer_id, file_path=ANSWER_PATH, file_header=ANSWER_DATA_HEADER)


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


def delete_entry(entry_id, file_path, file_header):
    entries = list(read_file(file_path))
    with open(file_path, 'w') as file:
        dict_writer = csv.DictWriter(file, fieldnames=file_header)
        dict_writer.writeheader()
        for elem in entries:
            if int(elem['id']) == entry_id:
                continue
            dict_writer.writerow(elem)
