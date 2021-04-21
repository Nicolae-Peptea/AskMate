import csv
import os
from datetime import datetime

QUESTIONS_PATH = 'data_play/question.csv'
ANSWER_PATH = 'data_play/answer.csv'
QUESTIONS_DATA_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWER_DATA_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


def get_single_entry_by_id(file_path, entry_id):
    entries = read_file(file_path)
    for entry in entries:
        if int(entry["id"]) == entry_id:
            return entry


def vote_entry(file_path, file_headers, entry_to_vote, vote):
    entry = entry_to_vote
    vote_as_int = int(entry['vote_number'])
    if vote == 'up':
        vote_as_int += 1
        entry['vote_number'] = str(vote_as_int)
    else:
        vote_as_int -= 1
        entry['vote_number'] = str(vote_as_int)
    write_elem_to_file(entry_to_vote, file_path, file_headers)


def get_single_question(question_id):
    return get_single_entry_by_id(file_path=QUESTIONS_PATH, entry_id=question_id)


def get_single_answer(answer_id):
    return get_single_entry_by_id(file_path=ANSWER_PATH, entry_id=answer_id)


def get_ordered_questions(questions, order_by, direction):
    integers = ["submission_time", "view_number", "vote_number"]
    for question in questions:
        for piece in range(len(questions) - 1):
            if direction == "asc":
                if order_by in integers:
                    if int(questions[piece][order_by]) > int(questions[piece+1][order_by]):
                        questions[piece], questions[piece + 1] = questions[piece + 1], questions[piece]
                else:
                    if questions[piece][order_by] > questions[piece+1][order_by]:
                        questions[piece], questions[piece + 1] = questions[piece + 1], questions[piece]
            else:
                if order_by in integers:
                    if int(questions[piece][order_by]) < int(questions[piece+1][order_by]):
                        questions[piece], questions[piece + 1] = questions[piece + 1], questions[piece]
                else:
                    if questions[piece][order_by] < questions[piece+1][order_by]:
                        questions[piece], questions[piece + 1] = questions[piece + 1], questions[piece]
    return questions


def get_answers_for_question(id_elem: str):
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
    write_elem_to_file(question, QUESTIONS_PATH, QUESTIONS_DATA_HEADER)


def delete_question(question_id, app):
    my_question = dict(get_single_question(question_id))
    delete_image(my_question, app)
    delete_entry(entry_id=question_id, file_path=QUESTIONS_PATH, file_header=QUESTIONS_DATA_HEADER)


def vote_question(question_id, vote):
    return vote_entry(file_path=QUESTIONS_PATH,
                      file_headers=QUESTIONS_DATA_HEADER,
                      entry_to_vote=get_single_question(question_id=question_id),
                      vote=vote,)


def increment_views_algorithm(file_path, file_headers, entry):
    incremented_views = int(entry['view_number']) + 1
    entry['view_number'] = str(incremented_views)
    write_elem_to_file(entry, file_path, file_headers)


def increment_views(question_id):
    return increment_views_algorithm(file_path=QUESTIONS_PATH, 
                                     file_headers=QUESTIONS_DATA_HEADER, 
                                     entry=get_single_question(question_id=question_id)
                                     )


def add_answer(new_entry, question_id):
    new_question = {
        'id': get_next_id(ANSWER_PATH),
        'question_id': question_id,
        'vote_number': 0,
        'submission_time': round(datetime.timestamp(datetime.now())),
    }
    new_question.update(new_entry)
    write_elem_to_file(new_question, ANSWER_PATH, ANSWER_DATA_HEADER)


def delete_answer(answer_id):
    delete_entry(entry_id=answer_id, file_path=ANSWER_PATH, file_header=ANSWER_DATA_HEADER)


def delete_answers(question_id, app):
    answers = get_answers_for_question(question_id)
    for answer in answers:
        if int(answer['question_id']) == question_id:
            delete_image(answer, app)
            delete_answer(int(answer['id']))


def vote_answer(answer_id, vote):
    return vote_entry(file_path=ANSWER_PATH,
                      file_headers=ANSWER_DATA_HEADER,
                      entry_to_vote=get_single_answer(answer_id=answer_id),
                      vote=vote,)


# CONNECTION


def delete_image(location, app):
    if location['image']:
        filename = location['image']
        files = os.listdir(app.config['UPLOAD_PATH'])
        if filename in files:
            os.unlink(os.path.join(app.config['UPLOAD_PATH'], filename))


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
