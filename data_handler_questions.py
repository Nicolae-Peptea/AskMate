import os
import re
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

import database_common


@database_common.connection_handler
def get_question(cursor: RealDictCursor, question_id: int):
    query = """SELECT * FROM question
                WHERE id = %(question_id)s"""
    cursor.execute(query, {"question_id": question_id})
    return dict(cursor.fetchone())


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
def get_latest_questions(cursor: RealDictCursor, show):
    cursor.execute(
        sql.SQL("""
        SELECT * FROM {table}
        ORDER BY {column} DESC LIMIT %(show)s
        """).
            format(table=sql.Identifier('question'),
                   column=sql.Identifier('submission_time')),
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
        sql.SQL(
            """
            SELECT * FROM {table}
            WHERE {col_1} ILIKE %(phrase)s or {col_2} ILIKE %(phrase)s
            """
        ).format(
            table=sql.Identifier('question'),
            col_1=sql.Identifier('message'),
            col_2=sql.Identifier('title'),
        ),
        {'phrase': f'%{phrase}%'}
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
def add_question(cursor: RealDictCursor, new_entry: dict):
    adding = """INSERT INTO question ("submission_time","title","message","image","view_number","vote_number")
                VALUES (now()::timestamp(0), %(title)s, %(message)s, %(image)s, 0, 0)
                """
    cursor.execute(adding, {
        'title': new_entry['title'],
        'message': new_entry['message'],
        'image': new_entry.get('image', None),
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
def vote_question(cursor, entry_id, table, vote=0):
    to_increase = 1 if vote == 'upvote' else - 1

    cursor.execute(
        sql.SQL("""
                UPDATE {table} 
                    SET vote_number = vote_number + %(increase)s
                WHERE id = %(entry_id)s
                """).
            format(table=sql.Identifier(table)), {"entry_id": entry_id, "increase": to_increase})
