import os
import re
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

import data_handlers.database_common as database_common
import data_handlers.data_handler_users as data_handler_users
import uuid


@database_common.connection_handler
def get_question(cursor: RealDictCursor, question_id: int):
    query = """
            SELECT
                q.id,
                q.submission_time,
                q.view_number,
                q.vote_number,
                q.title,
                q.message,
                q.image,
                u.email,
                u.id AS user_id
                FROM question q
                JOIN users u ON u.id = q.user_id
                WHERE q.id = %(question_id)s"""
    cursor.execute(query, {"question_id": question_id})
    return dict(cursor.fetchone())


@database_common.connection_handler
def get_questions(cursor: RealDictCursor, order_by: str, direction: str):
    if order_by not in ["submission_time", "view_number", "vote_number", "title", "message"] or \
            direction not in ["desc", "asc"]:
        raise ValueError
    cursor.execute(
        f"""
        SELECT
                q.id,
                q.uuid,
                q.submission_time,
                q.view_number,
                q.vote_number,
                q.title,
                q.message,
                q.image,
                u.email,
                u.id AS user_id
        FROM question q
        JOIN users u ON u.id = q.user_id
        ORDER BY {order_by} {direction}
        """)
    return cursor.fetchall()


@database_common.connection_handler
def get_latest_questions(cursor: RealDictCursor, show):
    cursor.execute(
        sql.SQL("""
            SELECT
                q.id,
                q.uuid,
                q.submission_time,
                q.view_number,
                q.vote_number,
                q.title,
                q.message,
                q.image,
                u.email,
                u.id AS user_id
            FROM question q
            JOIN users u ON u.id = q.user_id
            ORDER BY submission_time DESC LIMIT %(show)s
            """),
        {"show": show}
    )
    return cursor.fetchall()


@database_common.connection_handler
def get_last_added_question(cursor: RealDictCursor):
    cursor.execute('SELECT MAX(id) FROM question')
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
def get_searched_questions(cursor: RealDictCursor, phrase: str):
    cursor.execute(
        sql.SQL("""
            SELECT
                q.id,
                q.uuid,
                q.submission_time,
                q.view_number,
                q.vote_number,
                q.title,
                q.message,
                q.image,
                u.email,
                u.id AS user_id
            FROM question q
            JOIN users u ON u.id = q.user_id
            WHERE message ILIKE %(phrase)s or title ILIKE %(phrase)s
            """),
        {'phrase': f'%{phrase}%'}
    )

    return cursor.fetchall()


@database_common.connection_handler
def qet_questions_by_user_id(cursor, user_id: int):
    cursor.execute(
        sql.SQL(
            """
            SELECT title, id
            FROM question
            WHERE user_id = %(user_id)s
            """), {
           'user_id': user_id,
        }
    )
    return cursor.fetchall()


@database_common.connection_handler
def qet_questions_by_tag(cursor, tag_id: int):
    cursor.execute(
        sql.SQL(
            """
           select 
           question.id as id,
           u.id as user_id,
           u.email,
           question.submission_time,
           question.view_number,
           question.vote_number,
           question.title,
           question.message,
           question.image,
           tag.id
           from question
            join question_tag qt on question.id = qt.question_id
            join tag on qt.tag_id = tag.id
            join users u on u.id = question.user_id
            WHERE tag.id = %(tag_id)s
            """), {
           'tag_id': tag_id,
        }
    )
    return cursor.fetchall()


def highlight_search(questions: dict, phrase: str):
    if phrase:
        for question in questions:
            highlight_entry(question, phrase, field='title')
            highlight_entry(question, phrase, field='message')
    raise ValueError


def highlight_entry(entry: dict, phrase: str, field):
    words_to_highlight = re.findall(f'(?i){phrase}', entry[field])
    for to_replace in words_to_highlight:
        entry[field] = entry[field].replace(to_replace, f"<mark>{to_replace}</mark>")


@database_common.connection_handler
def add_question(cursor: RealDictCursor, new_entry: dict, email):
    adding = """INSERT INTO question (uuid, user_id, submission_time, title, message, image)
                VALUES (%(uuid)s, %(user_id)s, now()::timestamp(0), %(title)s, %(message)s, %(image)s)
                """
    cursor.execute(adding, {
        'user_id': data_handler_users.get_user_id(email),
        'title': new_entry['title'],
        'message': new_entry['message'],
        'image': new_entry.get('image', None),
        'uuid': str(uuid.uuid4()),
    })


def edit_question(new_entry: dict):
    image = new_entry.get('image', 0)
    if image:
        edit_question_receiving_image(new_entry, image)
    else:
        edit_question_receiving_no_image(new_entry)


@database_common.connection_handler
def edit_question_receiving_image(cursor: RealDictCursor, new_entry: dict, new_image: str):
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
        'question_id': new_entry['id']
    })


@database_common.connection_handler
def edit_question_receiving_no_image(cursor: RealDictCursor, new_entry: dict):
    edit = """
         UPDATE question
             SET title = %(new_title)s,
             message = %(new_message)s
         WHERE id = %(question_id)s
    """
    cursor.execute(edit, {
        'new_title': new_entry['title'],
        'new_message': new_entry['message'],
        'question_id': new_entry['id']
    })


@database_common.connection_handler
def delete_question(cursor: RealDictCursor, question_id: int, path):
    try:
        delete_question_images(question_id, path)
    except ValueError:
        pass

    cursor.execute(
        sql.SQL(
            """
            DELETE FROM question
            WHERE id = %(delete_value)s
            """
        ), {'delete_value': question_id}
    )


def delete_question_images(entry_id, path):
    file_list = get_image_names_for_question(entry_id)
    if file_list:
        for file in file_list:
            os.unlink(os.path.join(path, file))
    raise ValueError


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
def up_vote_question(cursor, question_id):
    cursor.execute(
        sql.SQL("""
                UPDATE {table} 
                    SET vote_number = vote_number + 1
                WHERE id = %(entry_id)s;
                """
                ).format(table=sql.Identifier('question')), {"entry_id": question_id})


@database_common.connection_handler
def down_vote_question(cursor, question_id):
    cursor.execute(
        sql.SQL("""
                UPDATE {table}
                    SET vote_number = vote_number - 1
                WHERE id = %(entry_id)s;
                """
                ).format(table=sql.Identifier('question')), {"entry_id": question_id})