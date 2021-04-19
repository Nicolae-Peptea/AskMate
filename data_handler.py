import connection, util


def get_questions():
    questions = connection.read_elem_from_file('question')
    return util.generate_list(questions)


def get_answers(id_elem: str):
    answers = connection.read_elem_from_file('answer')
    return [answer for answer in answers if answer['question_id'] == id_elem]


def add_entry(old_entries, new_entry, question_or_answer):
    new_story = util.add_id(dbase_len=old_entries,
                            elem_to_add=new_entry)
    old_entries.append(new_story)
    connection.write_elem_from_file(entries=old_entries,
                                    question_or_answer=question_or_answer)
