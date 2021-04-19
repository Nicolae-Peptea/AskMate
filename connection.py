import csv


def get_path(param: str):
    if param == 'question':
        return 'data_play/question.csv'
    elif param == 'answer':
        return 'data_play/answer.csv'
    else:
        return


def get_header(param: str):
    data_header_question = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
    data_header_answer = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']
    if param == 'question':
        return data_header_question
    elif param == 'answer':
        return data_header_answer
    else:
        return


def read_elem_from_file(question_or_answer):
    file_path = get_path(question_or_answer)
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for elem in reader:
            yield elem


def write_elem_from_file(entries, question_or_answer):
    file_path = get_path(question_or_answer)
    with open(file_path, 'w') as file:
        dict_writer = csv.DictWriter(file, fieldnames=get_header(question_or_answer))
        dict_writer.writeheader()
        for elem in entries:
            dict_writer.writerow(elem)


def modify_stuff():
    dictionary = read_elem_from_file('question')
    for story in dictionary:
        if story:
            pass
