import os
import re
import sys

import psycopg2
import database_common
from datetime import datetime
from psycopg2 import sql
from psycopg2.extras import RealDictCursor


# GET
@database_common.connection_handler
def get_questions(cursor: RealDictCursor, order_by: str, direction: str):
    if order_by not in ["submission_time", "view_number", "vote_number", "title", "message"] or \
            direction not in ["desc", "asc"]:
        raise ValueError
    cursor.execute(
        f"""
        SELECT * FROM question 
        ORDER BY {order_by} {direction}
        """)
    return cursor.fetchall()


@database_common.connection_handler
def get_latest_5_questions(cursor: RealDictCursor):
    cursor.execute(
        sql.SQL("""
        SELECT * FROM {table}
        ORDER BY {column} DESC LIMIT 5
        """).
            format(table=sql.Identifier('question'),
                   column=sql.Identifier('submission_time'))
    )
    return cursor.fetchall()


@database_common.connection_handler
def get_comments_for_answers_by_question_id(cursor: RealDictCursor):
    query = "SELECT * FROM comment"
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_comments_by_question_id(cursor: RealDictCursor, question_id: int):
    query = """SELECT * FROM comment
                WHERE question_id = %(question_id)s"""
    cursor.execute(query, {"question_id": question_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_question(cursor: RealDictCursor, question_id: int):
    query = """SELECT * FROM question
                WHERE id = %(question_id)s"""
    cursor.execute(query, {"question_id": question_id})
    return dict(cursor.fetchone())


@database_common.connection_handler
def get_answer(cursor: RealDictCursor, answer_id: int):
    query = """SELECT * FROM answer
                WHERE id = %(answer_id)s"""
    cursor.execute(query, {"answer_id": answer_id})
    return dict(cursor.fetchone())


@database_common.connection_handler
def get_comment(cursor: RealDictCursor, comment_id: int):
    query = """SELECT * FROM comment
                WHERE id = %(comment_id)s"""
    cursor.execute(query, {"comment_id": comment_id})
    return dict(cursor.fetchone())


def get_comment_and_question_id(comment_id: int):
    comment = get_comment(comment_id)

    if comment['question_id'] is not None:
        question_id = comment['question_id']
    elif comment['answer_id']:
        question_id = get_question_id(comment['answer_id'])
    return comment, question_id


@database_common.connection_handler
def get_answers_for_question(cursor: RealDictCursor, question_id: int):
    query = """SELECT * FROM answer
                WHERE question_id = %(question_id)s"""
    cursor.execute(query, {"question_id": question_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_last_added_question_id(cursor: RealDictCursor):
    cursor.execute('SELECT MAX(id) FROM question')
    return cursor.fetchone()['max']


@database_common.connection_handler
def get_last_added_answer_id(cursor: RealDictCursor):
    cursor.execute('SELECT MAX(id) FROM answer')
    return cursor.fetchone()['max']


@database_common.connection_handler
def get_image_names_for_question(cursor: RealDictCursor, entry_id: int):
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
def get_image_names_for_answers(cursor: RealDictCursor, entry_id: int):
    query = """
       SELECT image
           FROM answer
       WHERE id= %(entry_id)s
       """
    cursor.execute(query, {'entry_id': entry_id})
    return [value for e in cursor.fetchall() for key, value in e.items() if value]


@database_common.connection_handler
def get_question_id(cursor: RealDictCursor, answer_id: int):
    query = """
    SELECT question_id FROM answer
    WHERE id = %(answer_id)s
    """
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchone()['question_id']


@database_common.connection_handler
def get_question_tags(cursor: RealDictCursor, question_id: int):
    query = """
    SELECT * FROM question_tag, tag
    WHERE question_id = %(question_id)s
    AND tag.id = question_tag.tag_id
    """
    cursor.execute(query, {'question_id': question_id})
    return [dict(value) for value in cursor.fetchall()]


# ADD
@database_common.connection_handler
def add_question(cursor: RealDictCursor, new_entry: dict):
    print (new_entry)
    adding = """INSERT INTO question ("submission_time","title","message","image","view_number","vote_number")
                VALUES (now()::timestamp(0), %(title)s, %(message)s, %(image)s, 0, 0)
                """
    cursor.execute(adding, {
        'title': new_entry['title'],
        'message': new_entry['message'],
        'image': new_entry.get('image', None),
    })


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


@database_common.connection_handler
def add_comment_to_question(cursor: RealDictCursor, new_entry: dict, question_id: int):
    adding = """INSERT INTO comment ("submission_time","question_id","message","edited_count")
                    VALUES (now()::timestamp(0), %(question_id)s, %(message)s, 0)
                    """
    cursor.execute(adding, {
        'question_id': question_id,
        'message': new_entry['message'],
    })


@database_common.connection_handler
def add_comment_to_answer(cursor: RealDictCursor, new_entry: dict, answer_id: int):
    adding = """INSERT INTO comment ("submission_time","answer_id","message","edited_count")
                    VALUES (now()::timestamp(0), %(answer_id)s, %(message)s, 0)
                    """
    cursor.execute(adding, {
        'answer_id': answer_id,
        'message': new_entry['message'],
    })


@database_common.connection_handler
def add_question_tag(cursor: RealDictCursor, question_id: int, new_tag, existing_tag):
    if new_tag:
        add_new_tag = """INSERT INTO tag ("name")
                    VALUES (%(name)s);
                    SELECT id FROM tag
                    WHERE name=%(name)s;"""
        cursor.execute(add_new_tag, {'name': new_tag})
        tag_id = cursor.fetchone()['id']
        attach_tag_to_question="""
        INSERT INTO question_tag ("question_id", "tag_id")
                    VALUES (%(question_id)s, %(tag_id)s)"""
        cursor.execute(attach_tag_to_question, {
            'question_id': question_id,
            'tag_id': tag_id
        })
    else:
        select_tag = """SELECT id FROM tag WHERE name=%(name)s;"""
        cursor.execute(select_tag, {'name': existing_tag})
        tag_id = cursor.fetchone()['id']
        print(tag_id)
        attach_tag_to_question="""
        INSERT INTO question_tag ("question_id", "tag_id")
                    VALUES (%(question_id)s, %(tag_id)s)"""
        cursor.execute(attach_tag_to_question, {
            'question_id': question_id,
            'tag_id': tag_id
        })


# EDIT
@database_common.connection_handler
def edit_question(cursor: RealDictCursor, new_entry: dict, question_id: int):
    new_image = new_entry.get('image', 0)
    if new_image:
        edit = """
        UPDATE question 
            SET title = %(new_title)s,
            message = %(new_message)s,
            image = %(new_image)s
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
            SET title = %(new_title)s,
            message = %(new_message)s
        WHERE id = %(question_id)s
        """
        cursor.execute(edit, {
            'new_title': new_entry['title'],
            'new_message': new_entry['message'],
            'question_id': question_id
        })


@database_common.connection_handler
def edit_answer(cursor: RealDictCursor, new_entry: dict, answer_id: int):
    new_image = new_entry.get('image', 0)
    if new_image:
        edit = """
        UPDATE answer 
            SET 
            message = %(new_message)s,
            image = %(new_image)s
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
            SET message = %(new_message)s
        WHERE id = %(answer_id)s
        """
        cursor.execute(edit, {
            'new_message': new_entry['message'],
            'answer_id': answer_id,
        })


@database_common.connection_handler
def edit_comment(cursor: RealDictCursor, new_entry: dict, comment_id: int):
    edit = """
    UPDATE comment 
    SET message = %(new_message)s,
    submission_time = now()::timestamp(0),
    edited_count = edited_count + 1
    WHERE id = %(comment_id)s
    """
    cursor.execute(edit, {
        'new_message': new_entry['message'],
        'comment_id': comment_id
    })


# DELETE
@database_common.connection_handler
def delete_entry(cursor, field_name, delete_value, table):
    if field_name not in ["question_id", "id", "answer_id"]:
        raise ValueError

    cursor.execute(
        sql.SQL("""DELETE FROM {table} WHERE {delete_by} = %(delete_value)s""").
            format(delete_by=sql.Identifier(field_name),
                   table=sql.Identifier(table)), {'delete_value': delete_value}
    )


def delete_question(question_id, path):
    delete_question_images(question_id, path)
    delete_entry('question_id', question_id, 'question_tag')
    delete_entry('question_id', question_id, 'answer')
    delete_entry('question_id', question_id, 'comment')
    delete_entry('id', question_id, 'question')


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
def delete_comment(cursor, comment_id):
    delete = "DELETE FROM comment WHERE id = %(comment_id)s"
    cursor.execute(delete, {'comment_id': comment_id})


@database_common.connection_handler
def delete_question_tag(cursor, question_id, tag_id):
    delete = """
        DELETE FROM question_tag 
        WHERE question_id = %(question_id)s
        AND tag_id = %(tag_id)s"""
    cursor.execute(delete, {'question_id': question_id, 'tag_id': tag_id})


# DO

@database_common.connection_handler
def update_views(cursor: RealDictCursor, question_id: int):
    update = """
    UPDATE question 
    SET view_number = view_number + 1
    WHERE id = %(question_id)s
    """
    cursor.execute(update, {
        'question_id': question_id
    })


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
def get_searched_questions(cursor: RealDictCursor, phrase: str):
    query = f"""
    SELECT * FROM question
    WHERE message ILIKE '%{phrase}%' or title ILIKE '%{phrase}%'
    """
    cursor.execute(query)
    return cursor.fetchall()


def highlighted_search(questions: dict, phrase: str):
    if phrase:
        for question in questions:
            for to_replace in re.findall(f'(?i){phrase}', question['message']):
                question['message'] = question['message'].replace(to_replace, f"<mark>{to_replace}</mark>")
            for to_replace in re.findall(f'(?i){phrase}', question['title']):
                question['title'] = question['title'].replace(to_replace, f"<mark>{to_replace}</mark>")
