import os
import sys

import psycopg2
import database_common
from datetime import datetime
from psycopg2 import sql
from psycopg2.extras import RealDictCursor


@database_common.connection_handler
def get_questions(cursor):
    cursor.execute(
        sql.SQL("select * from {table}").
            format(table=sql.Identifier('question')))
    return cursor.fetchall()


@database_common.connection_handler
def get_comments_by_question_id(cursor, question_id):
    query = """SELECT * FROM comment
                WHERE question_id = %(question_id)s"""
    cursor.execute(query, {"question_id": question_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_comments_for_answers_by_question_id(cursor):
    query = "SELECT * FROM comment"
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_single_question(cursor, question_id):
    query = """SELECT * FROM question
                WHERE id = %(question_id)s"""
    cursor.execute(query, {"question_id": question_id})
    return dict(cursor.fetchone())


@database_common.connection_handler
def get_single_answer(cursor, answer_id):
    query = """SELECT * FROM answer
                WHERE id = %(answer_id)s"""
    cursor.execute(query, {"answer_id": answer_id})
    return dict(cursor.fetchone())


@database_common.connection_handler
def get_single_comment(cursor, comment_id):
    query = """SELECT * FROM comment
                WHERE id = %(comment_id)s"""
    cursor.execute(query, {"comment_id": comment_id})
    return dict(cursor.fetchone())


def get_ordered_questions(parameters):
    questions = generate_data_with_integers(list(read_file(QUESTIONS_PATH)))
    order_by = parameters.get('order_by', 'submission_time')
    direction = parameters.get('order_direction', 'desc')
    should_reverse = direction == 'desc'

    return sorted(questions, key=lambda elem: elem[order_by], reverse=should_reverse)


@database_common.connection_handler
def get_answers_for_question(cursor, question_id):
    query = """SELECT * FROM answer
                WHERE question_id = %(question_id)s"""
    cursor.execute(query, {"question_id": question_id})
    return cursor.fetchall()


@database_common.connection_handler
def add_question(cursor, new_entry):
    adding = """INSERT INTO question ("submission_time","title","message","image","view_number","vote_number")
                VALUES (now()::timestamp(0), %(title)s, %(message)s, %(image)s, 0, 0)
                """
    cursor.execute(adding, {
        'title': new_entry['title'],
        'message': new_entry['message'],
        'image': new_entry.get('image', None),
    })


@database_common.connection_handler
def get_last_added_question_id(cursor):
    cursor.execute('SELECT MAX(id) FROM question')
    return cursor.fetchone()['max']


@database_common.connection_handler
def get_last_added_answer_id(cursor):
    cursor.execute('SELECT MAX(id) FROM answer')
    return cursor.fetchone()['max']


@database_common.connection_handler
def edit_question(cursor, new_entry, question_id):
    new_image = new_entry.get('image', 0)
    if new_image:
        edit = """
        UPDATE question 
            SET title=%(new_title)s,
            message=%(new_message)s,
            image=%(new_image)s
        WHERE id = %(question_id)s
        """
        cursor.execute(edit, {
            'new_title': new_entry['title'],
            'new_message': new_entry['message'],
            'new_image': new_image,
            'question_id': question_id
        })
    else:
        edit = """
        UPDATE question 
            SET title=%(new_title)s,
            message=%(new_message)s
        WHERE id = %(question_id)s
        """
        cursor.execute(edit, {
            'new_title': new_entry['title'],
            'new_message': new_entry['message'],
            'question_id': question_id
        })


@database_common.connection_handler
def edit_answer(cursor, new_entry, answer_id):
    # functie cu edit
    new_image = new_entry.get('image', 0)
    if new_image:
        edit = """
        UPDATE answer 
            SET 
            message=%(new_message)s,
            image=%(new_image)s
        WHERE id = %(answer_id)s
        """
        cursor.execute(edit, {
            'new_message': new_entry['message'],
            'new_image': new_image,
            'answer_id': answer_id,
        })
    else:
        edit = """
        UPDATE answer 
            SET message=%(new_message)s
        WHERE id = %(answer_id)s
        """
        cursor.execute(edit, {
            'new_message': new_entry['message'],
            'answer_id': answer_id,
        })


@database_common.connection_handler
def delete_entry(cursor, delete_by, delete_value, table):
    cursor.execute(
        sql.SQL("""DELETE FROM {table} WHERE {delete_by} = %(delete_value)s""").
            format(delete_by=sql.Identifier(delete_by),
                   table=sql.Identifier(table)), {'delete_value': delete_value}
    )


def delete_question(question_id, path):
    delete_question_images(question_id, path)
    delete_entry('question_id', question_id, 'question_tag')
    delete_entry('question_id', question_id, 'answer')
    delete_entry('question_id', question_id, 'comment')
    delete_entry('id', question_id, 'question')


@database_common.connection_handler
def get_image_names_for_question(cursor, entry_id):
    query = """
    SELECT image
        FROM question
    WHERE id= %(entry_id)s
        UNION
    SELECT image
        FROM answer
    WHERE question_id=%(entry_id)s
    """
    cursor.execute(query, {'entry_id': entry_id})
    return [value for e in cursor.fetchall() for key, value in e.items() if value]


@database_common.connection_handler
def get_image_names_for_answers(cursor, entry_id):
    query = """
       SELECT image
           FROM answer
       WHERE id= %(entry_id)s
       """
    cursor.execute(query, {'entry_id': entry_id})
    return [value for e in cursor.fetchall() for key, value in e.items() if value]


def increment_views_algorithm(file_path, file_headers, entry):
    incremented_views = int(entry['view_number']) + 1
    entry['view_number'] = str(incremented_views)
    write_elem_to_file(entry, file_path, file_headers)


def increment_views(question_id):
    return increment_views_algorithm(QUESTIONS_PATH, file_headers=QUESTIONS_DATA_HEADER,
                                     entry=get_single_question(question_id=question_id))


@database_common.connection_handler
def vote_question(cursor, entry_id, table, vote=0):
    to_increase = 1 if vote == 'upvote' else - 1

    cursor.execute(
        sql.SQL("""
                UPDATE {table} SET 
                vote_number = vote_number + %(increase)s
                WHERE id = %(entry_id)s""").
            format(table=sql.Identifier(table)), {"entry_id": entry_id, "increase": to_increase})


@database_common.connection_handler
def add_answer(cursor, new_entry, question_id):
    adding = """INSERT INTO answer ("submission_time","question_id","message","image","vote_number")
                VALUES (now()::timestamp(0), %(question_id)s, %(message)s, %(image)s, 0)
                """
    cursor.execute(adding, {
        'question_id': question_id,
        'message': new_entry['message'],
        'image': new_entry.get('image', None),
    })


@database_common.connection_handler
def get_question_id(cursor, answer_id):
    query = """
    SELECT question_id FROM answer
    WHERE id = %(answer_id)s
    """
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchone()['question_id']


def delete_answer(answer_id, path):
    delete_answer_image(answer_id, path)
    delete_entry('answer_id', answer_id, 'comment')
    delete_entry('id', answer_id, 'answer')


def delete_question_images(entry_id, path):
    file_list = get_image_names_for_question(entry_id)
    if file_list:
        for file in file_list:
            os.unlink(os.path.join(path, file))


def delete_answer_image(entry_id, path):
    file_list = get_image_names_for_answers(entry_id)
    if file_list:
        for file in file_list:
            os.unlink(os.path.join(path, file))


@database_common.connection_handler
def add_comment_to_question(cursor, new_entry, question_id):
    adding = """INSERT INTO comment ("submission_time","question_id","message","edited_count")
                    VALUES (now()::timestamp(0), %(question_id)s, %(message)s, 0)
                    """
    cursor.execute(adding, {
        'question_id': question_id,
        'message': new_entry['comment'],
    })


@database_common.connection_handler
def add_comment_to_answer(cursor, new_entry, answer_id):
    adding = """INSERT INTO comment ("submission_time","answer_id","message","edited_count")
                    VALUES (now()::timestamp(0), %(answer_id)s, %(message)s, 0)
                    """
    cursor.execute(adding, {
        'answer_id': answer_id,
        'message': new_entry['comment'],
    })