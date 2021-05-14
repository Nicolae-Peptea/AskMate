import os
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

import database_common


@database_common.connection_handler
def get_answer(cursor: RealDictCursor, answer_id: int):
    query = """SELECT * FROM answer
                WHERE id = %(answer_id)s"""
    cursor.execute(query, {"answer_id": answer_id})
    return dict(cursor.fetchone())


@database_common.connection_handler
def get_answers_for_question(cursor: RealDictCursor, question_id: int):
    query = """SELECT * FROM answer
                WHERE question_id = %(question_id)s"""
    cursor.execute(query, {"question_id": question_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_last_added_answer_id(cursor: RealDictCursor):
    cursor.execute('SELECT MAX(id) FROM answer')
    return cursor.fetchone()['max']


@database_common.connection_handler
def get_image_names_for_answers(cursor: RealDictCursor, entry_id: int):
    query = """
       SELECT image
           FROM answer
       WHERE id= %(entry_id)s
       """
    cursor.execute(query, {'entry_id': entry_id})
    return [value for e in cursor.fetchall() for key, value in e.items() if value]


@database_common.connection_handler
def add_answer(cursor: RealDictCursor, new_entry: dict, question_id: int):
    adding = """INSERT INTO answer ("submission_time","question_id","message","image","vote_number")
                VALUES (now()::timestamp(0), %(question_id)s, %(message)s, %(image)s, 0)
                """
    cursor.execute(adding, {
        'question_id': question_id,
        'message': new_entry['message'],
        'image': new_entry.get('image', None),
    })


def edit_answer(new_entry: dict):
    image = new_entry.get('image', 0)
    if image:
        edit_answer_receiving_image(new_entry, image)
    else:
        edit_answer_receiving_no_image(new_entry, image)


@database_common.connection_handler
def edit_answer_receiving_image(cursor: RealDictCursor, new_entry: dict, image):
    edit = """
    UPDATE answer 
        SET 
            message = %(new_message)s,
            image = %(new_image)s
    WHERE id = %(answer_id)s
    """
    cursor.execute(edit, {
        'new_message': new_entry['message'],
        'new_image': image,
        'answer_id': new_entry['id'],
    })


@database_common.connection_handler
def edit_answer_receiving_no_image(cursor: RealDictCursor, new_entry: dict, answer_id: int):
    edit = """
    UPDATE answer 
        SET message = %(new_message)s
    WHERE id = %(answer_id)s
    """
    cursor.execute(edit, {
        'new_message': new_entry['message'],
        'answer_id': new_entry['id'],
    })


@database_common.connection_handler
def delete_answer(cursor: RealDictCursor, answer_id, path):
    try:
        delete_answer_image(answer_id, path)
    except ValueError:
        pass
    cursor.execute(
        sql.SQL(
            """
            DELETE FROM answer
            WHERE id = %(delete_value)s
            """
        ), {'delete_value': answer_id}
    )


def delete_answer_image(entry_id, path):
    file_list = get_image_names_for_answers(entry_id)
    if file_list:
        for file in file_list:
            os.unlink(os.path.join(path, file))
    raise ValueError