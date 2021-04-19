import connection


def get_answers(id_elem: str):
    answers = connection.read_elem_from_file('answer')
    return [answer for answer in answers if answer['question_id'] == id_elem]


def generate_list(parameter):
    return [line for line in parameter]


def read_questions():
    questions = connection.read_elem_from_file('question')
    print(questions)
    return generate_list(questions)