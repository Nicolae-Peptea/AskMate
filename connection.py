import csv


def get_path(param: str):
    if param == 'question':
        return 'sample_data/question.csv'
    elif param == 'answer':
        return 'sample_data/answer.csv'
    else:
        return


def get_header(param: str):
    data_header_question = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message,image']
    data_header_answer = ['id', 'submission_time', 'vote_number', 'question_id', 'message,image']
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


def modify_stuff():
    dictionary = read_elem_from_file('question')
    for story in dictionary:
        if story:
            pass
