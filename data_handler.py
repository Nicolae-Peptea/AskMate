import connection


def get_answers(id_elem: str):
    answers = connection.read_elem_from_file('answer')
    return [answer for answer in answers if answer['question_id'] == id_elem]


print (get_answers('2'))