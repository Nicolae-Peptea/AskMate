import csv


ANSWERS_PATH = "answer.csv"
QUESTIONS_PATH = "question.csv"
DATA_HEADERS = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']


def read_from_file(file_name):
    with open(file_name) as file:
        input_file = list(csv.DictReader(file))
    for line in input_file:
        yield line


def generate_list(questions):
    return [line for line in questions]


def read_questions():
    questions = read_from_file(QUESTIONS_PATH)
    return generate_list(questions)


def read_answers():
    answers = read_from_file(ANSWERS_PATH)
    return generate_list(answers)
